    # pivot_signal_bot.py
import os
import time
import requests
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime
import threading # New import for threading
from flask import Flask # New import for Flask

    # --- Configuration ---
load_dotenv()

    # Binance API (no API key needed for public data like klines)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    # Telegram Bot API
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Cryptocurrencies and Intervals to monitor
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"] # Add or remove symbols as needed
INTERVALS = [Client.KLINE_INTERVAL_15MINUTE, Client.KLINE_INTERVAL_1HOUR] # 15m and 1h intervals

    # Bot settings
CHECK_INTERVAL_SECONDS = 300 # Check every 5 minutes

    # Flask app for keeping the service alive
app = Flask(__name__)

@app.route('/')
def home():
    """Simple endpoint to respond to health checks/pings."""
    return "Bot is alive and running!", 200

    # --- Helper Functions ---

def send_telegram_message(message):
    """Sends a message to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot token or chat ID not set. Cannot send message.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"Telegram message sent successfully: {message}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

def get_candlestick_data(symbol, interval, limit=100):
    """Fetches candlestick data from Binance."""
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        parsed_klines = []
        for kline in klines:
            parsed_klines.append({
                'open_time': kline[0],
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[5]),
                'close_time': kline[6]
            })
        return parsed_klines
    except Exception as e:
        print(f"Error fetching {symbol} {interval} klines: {e}")
        return []

def calculate_pivot_points(high, low, close):
    """Calculates Classic Pivot Points (PP, R1-R3, S1-S3)."""
        pp = (high + low + close) / 3
        r1 = (2 * pp) - low
        s1 = (2 * pp) - high
        r2 = pp + (high - low)
        s2 = pp - (high - low)
        r3 = r1 + (high - low)
        s3 = s1 - (high - low)
        return {
            'pp': pp,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }

def calculate_nsdt_zones(klines, sensitivity_factor=0.005, min_cluster_size=3):
        """
        Calculates simplified NSDT auto support/resistance zones based on highs, lows, and clustering.
        This is a simplified approach for demonstration, not a full NSDT implementation.
        It identifies price levels where multiple highs or lows are clustered.
        """
    if not klines:
        return {'support': [], 'resistance': []}

    all_extrema = []
    for kline in klines:
        all_extrema.append({'price': kline['high'], 'type': 'resistance'})
        all_extrema.append({'price': kline['low'], 'type': 'support'})

        # Sort by price
    all_extrema.sort(key=lambda x: x['price'])

    zones = {'support': [], 'resistance': []}
        
        # Cluster similar prices into zones
    current_cluster = []
    for i, extrema in enumerate(all_extrema):
        if not current_cluster:
            current_cluster.append(extrema)
        else:
                # Check if current extrema is within sensitivity of the last one in the cluster
            last_price_in_cluster = current_cluster[-1]['price']
            price_diff = abs(extrema['price'] - last_price_in_cluster)
                
                # Define sensitivity dynamically based on price
            sensitivity_threshold = last_price_in_cluster * sensitivity_factor

            if price_diff <= sensitivity_threshold and extrema['type'] == current_cluster[-1]['type']:
                    current_cluster.append(extrema)
            else:
                    # New cluster or type change, process the old cluster
                if len(current_cluster) >= min_cluster_size:
                    zone_type = current_cluster[0]['type']
                    zone_prices = [item['price'] for item in current_cluster]
                    avg_price = sum(zone_prices) / len(zone_prices)
                    zones[zone_type].append(avg_price)
                    current_cluster = [extrema]
        
        # Process the last cluster
        if len(current_cluster) >= min_cluster_size:
            zone_type = current_cluster[0]['type']
            zone_prices = [item['price'] for item in current_cluster]
            avg_price = sum(zone_prices) / len(zone_prices)
            zones[zone_type].append(avg_price)

        # Sort and remove duplicates (if any, due to averaging)
        zones['support'] = sorted(list(set([round(z, 4) for z in zones['support']])))
        zones['resistance'] = sorted(list(set([round(z, 4) for z in zones['resistance']])))

        return zones

def generate_signal(symbol, interval, current_price, pp_levels, nsdt_zones):
        """Generates BUY/SELL signals based on Pivot Points and NSDT zones."""
        signal = None
        reason = []

        # Check against Pivot Points
        # Buy if price is near support levels (S1, S2, S3)
        if current_price <= pp_levels['s1'] * 1.001 and current_price >= pp_levels['s1'] * 0.999: # Within 0.1% of S1
            signal = "BUY"
            reason.append(f"Near S1 ({pp_levels['s1']:.4f})")
        elif current_price <= pp_levels['s2'] * 1.001 and current_price >= pp_levels['s2'] * 0.999:
            signal = "BUY"
            reason.append(f"Near S2 ({pp_levels['s2']:.4f})")
        elif current_price <= pp_levels['s3'] * 1.001 and current_price >= pp_levels['s3'] * 0.999:
            signal = "BUY"
            reason.append(f"Near S3 ({pp_levels['s3']:.4f})")

        # Sell if price is near resistance levels (R1, R2, R3)
        if current_price >= pp_levels['r1'] * 0.999 and current_price <= pp_levels['r1'] * 1.001: # Within 0.1% of R1
            if signal != "BUY": # Avoid conflicting signals
                signal = "SELL"
                reason.append(f"Near R1 ({pp_levels['r1']:.4f})")
        elif current_price >= pp_levels['r2'] * 0.999 and current_price <= pp_levels['r2'] * 1.001:
            if signal != "BUY":
                signal = "SELL"
                reason.append(f"Near R2 ({pp_levels['r2']:.4f})")
        elif current_price >= pp_levels['r3'] * 0.999 and current_price <= pp_levels['r3'] * 1.001:
            if signal != "BUY":
                signal = "SELL"
                reason.append(f"Near R3 ({pp_levels['r3']:.4f})")

        # Check against NSDT zones
        # A small buffer for zone detection
        zone_buffer_factor = 0.002 # 0.2% buffer

        for zone in nsdt_zones['support']:
            lower_bound = zone * (1 - zone_buffer_factor)
            upper_bound = zone * (1 + zone_buffer_factor)
            if lower_bound <= current_price <= upper_bound:
                if signal != "SELL": # Prioritize buy if both support/resistance are hit (unlikely)
                    signal = "BUY"
                    reason.append(f"In NSDT Support Zone ({zone:.4f})")
                    break # Only need one reason

        for zone in nsdt_zones['resistance']:
            lower_bound = zone * (1 - zone_buffer_factor)
            upper_bound = zone * (1 + zone_buffer_factor)
            if lower_bound <= current_price <= upper_bound:
                if signal != "BUY":
                    signal = "SELL"
                    reason.append(f"In NSDT Resistance Zone ({zone:.4f})")
                    break # Only need one reason

        if signal:
            return signal, " and ".join(reason)
        return None, None

    # --- Main Bot Logic ---

  def bot_loop():
        """Function containing the main trading bot logic."""
      print("Starting trading bot loop...")
      print(f"Monitoring symbols: {', '.join(SYMBOLS)}")
      print(f"Monitoring intervals: {', '.join(INTERVALS)}")
      print(f"Checking every {CHECK_INTERVAL_SECONDS} seconds.")

      while True:
          timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          print(f"\n--- Checking at {timestamp} ---")

          for symbol in SYMBOLS:
              for interval in INTERVALS:
                  print(f"Fetching data for {symbol} ({interval})...")
                  klines = get_candlestick_data(symbol, interval, limit=100) # Get enough data for NSDT

                  if not klines or len(klines) < 2: # Need at least 2 candles for last completed and current price
                      print(f"Not enough data for {symbol} ({interval}). Skipping.")
                      continue

                    # The last completed candle is klines[-2]
                    # The current (uncompleted) candle's close is klines[-1]['close']
                  last_completed_candle = klines[-2]
                  current_price = klines[-1]['close']

                  high = last_completed_candle['high']
                  low = last_completed_candle['low']
                  close = last_completed_candle['close']

                    # Calculate Pivot Points
                  pp_levels = calculate_pivot_points(high, low, close)
                    
                    # Calculate NSDT Zones using a broader range of candles (e.g., last 50)
                  nsdt_zones = calculate_nsdt_zones(klines[-50:]) # Use last 50 candles for zone calculation

                    # Generate Signal
                  signal, reason = generate_signal(symbol, interval, current_price, pp_levels, nsdt_zones)

                  print(f"  {symbol} ({interval}) Current Price: {current_price:.4f}")
                  print(f"    PP: {pp_levels['pp']:.4f}, R1: {pp_levels['r1']:.4f}, S1: {pp_levels['s1']:.4f}")
                  print(f"    NSDT Support Zones: {nsdt_zones['support']}")
                  print(f"    NSDT Resistance Zones: {nsdt_zones['resistance']}")

                  if signal:
                      alert_message = (
                          f"🚨 *{symbol} {interval} Signal!* 🚨\n"
                          f"📊 *Action:* {signal}!\n"
                          f"💰 *Price:* {current_price:.4f}\n"
                          f"📈 *Reason:* {reason}\n"
                          f"--- \n"
                          f"📍 *Pivot Points:*\n"
                          f"  PP: `{pp_levels['pp']:.4f}`\n"
                          f"  R1: `{pp_levels['r1']:.4f}`, R2: `{pp_levels['r2']:.4f}`, R3: `{pp_levels['r3']:.4f}`\n"
                          f"  S1: `{pp_levels['s1']:.4f}`, S2: `{pp_levels['s2']:.4f}`, S3: `{pp_levels['s3']:.4f}`\n"
                          f"🌐 *NSDT Zones:*\n"
                          f"  Support: `{', '.join(map(lambda x: f'{x:.4f}', nsdt_zones['support']))}`\n"
                          f"  Resistance: `{', '.join(map(lambda x: f'{x:.4f}', nsdt_zones['resistance']))}`"
                      )
                      send_telegram_message(alert_message)
                  else:
                      print(f"  No signal for {symbol} ({interval}) at current price.")

          print(f"Sleeping for {CHECK_INTERVAL_SECONDS} seconds...")
          time.sleep(CHECK_INTERVAL_SECONDS)

  if __name__ == "__main__":
        # Start the bot logic in a separate thread
      bot_thread = threading.Thread(target=bot_loop)
      bot_thread.daemon = True # Allow the main program to exit even if this thread is running
      bot_thread.start()

        # Start the Flask web server
        # Render provides a PORT environment variable, use it. Default to 5000 for local testing.
      port = int(os.environ.get("PORT", 5000))
      print(f"Starting Flask web server on port {port}...")
      app.run(host='0.0.0.0', port=port)

    
