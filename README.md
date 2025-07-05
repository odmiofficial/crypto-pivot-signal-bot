    # Crypto Pivot Signal Bot

    A Python-based trading bot that fetches live candlestick data from Binance, calculates Classic Pivot Points and simplified NSDT auto support/resistance zones, generates BUY/SELL signals, and sends alerts to a Telegram channel.

    ## Features

    * **Multi-Cryptocurrency Support:** Monitor multiple trading pairs (e.g., BTCUSDT, ETHUSDT).
    * **Multiple Timeframes:** Analyze 15-minute and 1-hour candlestick data.
    * **Classic Pivot Points:** Calculates PP, R1-R3, and S1-S3 levels.
    * **NSDT Auto Support/Resistance Zones:** Identifies potential support and resistance zones based on historical highs, lows, and clustering (simplified implementation).
    * **BUY/SELL Signals:** Generates signals when the price interacts with calculated support or resistance levels/zones.
    * **Telegram Alerts:** Sends detailed alerts including symbol, price, signal, and relevant support/resistance levels/zones.
    * **Configurable:** Easily add/remove symbols and adjust check intervals.
    * **Secure:** Uses `.env` file for sensitive API keys and chat IDs.
    * **24/7 Uptime (Free Tier Workaround):** Includes a small web server to allow deployment on platforms like Render's free Web Services, kept alive by external ping services.

    ## Getting Started

    Follow these steps to set up and run the bot.

    ### Prerequisites

    * Python 3.8+ installed.
    * A Telegram account to create a bot and get your chat ID.

    ### 1. Clone the Repository

    ```bash
    git clone [https://github.com/your-username/crypto-pivot-signal-bot.git](https://github.com/your-username/crypto-pivot-signal-bot.git)
    cd crypto-pivot-signal-bot
    ```

    ### 2. Install Dependencies

    It's recommended to use a virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

    ### 3. Configure Telegram Bot

    1.  **Create a Telegram Bot:**
        * Open Telegram and search for `@BotFather`.
        * Start a chat with `@BotFather` and send `/newbot`.
        * Follow the instructions to choose a name and a username for your bot.
        * `BotFather` will give you an **HTTP API Token**. Keep this token safe.
    2.  **Get your Chat ID:**
        * Start a chat with your newly created bot. Send any message (e.g., "Hi").
        * Open your web browser and go to `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` (replace `<YOUR_BOT_TOKEN>` with your bot's token).
        * Look for the `"chat"` object in the JSON response. Your `id` field within that object is your `TELEGRAM_CHAT_ID`. It will be a number (e.g., `-123456789`).

    ### 4. Set up Environment Variables

    1.  Rename `.env.example` to `.env`:

        ```bash
        mv .env.example .env
        ```
    2.  Edit the `.env` file and fill in your Telegram Bot Token and Chat ID:

        ```
        # .env

        TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
        TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID

        # Binance API Key and Secret (Optional, not strictly needed for public data)
        # BINANCE_API_KEY=YOUR_BINANCE_API_KEY
        # BINANCE_API_SECRET=YOUR_BINANCE_API_SECRET
        ```

    ### 5. Run the Bot Locally (Optional)

    ```bash
    python pivot_signal_bot.py
    ```

    The bot will start fetching data, calculating levels, and sending alerts to your Telegram chat if signals are generated. It runs in an infinite loop, checking every 5 minutes by default. The Flask server will also start on port 5000 (you can visit `http://localhost:5000` in your browser to see "Bot is alive and running!").

    ## Customization

    * **Symbols and Intervals:** Edit the `SYMBOLS` and `INTERVALS` lists in `pivot_signal_bot.py` to monitor different cryptocurrencies or timeframes.
    * **Check Interval:** Adjust `CHECK_INTERVAL_SECONDS` in `pivot_signal_bot.py` to change how often the bot fetches data.
    * **NSDT Sensitivity:** Modify `sensitivity_factor` and `min_cluster_size` in `calculate_nsdt_zones` for different zone detection behavior.
    * **Signal Logic:** Refine the `generate_signal` function to implement more complex trading strategies.

    ## Deployment on Render (24/7 Free Tier)

    To run your bot 24/7 on Render's free tier, we'll use a "Web Service" combined with an external "ping" service.

    ### 1. Push Your Code to GitHub

    Make sure your updated `pivot_signal_bot.py`, `requirements.txt`, `.env.example`, and `README.md` are pushed to your GitHub repository.

    If you haven't pushed your code to GitHub yet, follow these steps in your terminal (from your project folder):

    ```bash
    # If you haven't initialized Git yet:
    git init
    # Create .gitignore if you haven't:
    touch .gitignore
    echo ".env" >> .gitignore # Add .env to .gitignore
    git add .
    git commit -m "Add initial project files and Flask server for Render"

    # If you haven't connected to GitHub yet (replace with your repo URL):
    git remote add origin [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    git branch -M main # Rename your branch to 'main' if it's 'master'
    git push -u origin main
    ```
    If you already pushed, just make sure to commit your changes and push again:
    ```bash
    git add .
    git commit -m "Update bot for Render 24/7 hosting with Flask server"
    git push origin main
    ```

    ### 2. Create a Render Web Service

    1.  Go to [Render Dashboard](https://dashboard.render.com/) and log in.
    2.  Click "New" -> "Web Service".
    3.  Connect your GitHub repository. You might need to grant Render access to your repo.
    4.  **Configuration:**
        * **Name:** Give your service a clear name (e.g., `crypto-signal-bot`).
        * **Region:** Choose a region close to you or your target audience.
        * **Branch:** `main` (or the branch you pushed your code to).
        * **Root Directory:** Leave empty if your `pivot_signal_bot.py` is at the root of your repo.
        * **Runtime:** `Python 3`
        * **Build Command:** `pip install -r requirements.txt`
        * **Start Command:** `python pivot_signal_bot.py` (Render will automatically set the `PORT` environment variable for Flask).
        * **Instance Type:** Select "Free".
    5.  **Environment Variables:**
        * Go to the "Environment" tab (or click "Advanced" during creation).
        * Add your sensitive information as environment variables (these will be securely stored and not visible in your code or GitHub):
            * `TELEGRAM_BOT_TOKEN`: Your actual Telegram bot token.
            * `TELEGRAM_CHAT_ID`: Your actual Telegram chat ID.
            * *(Optional)* `BINANCE_API_KEY` and `BINANCE_API_SECRET` if you ever plan to use authenticated Binance endpoints.
    6.  **Create Web Service:** Click the "Create Web Service" button. Render will now build and deploy your bot. This might take a few minutes.

    ### 3. Keep it Alive (Avoid Sleeping/Inactivity)

    Once your Render service is deployed and running, you'll see a public URL (e.g., `https://your-service-name.onrender.com/`). This is the URL we need to ping.

    Render's free web services will spin down if they don't receive traffic for 15 minutes. To prevent this, you need an external service to "ping" your bot's URL periodically.

    1.  **Find Your Render Service URL:** On your Render dashboard, click on your newly deployed service. You'll see its public URL at the top (e.g., `https://crypto-signal-bot.onrender.com/`). Copy this URL.
    2.  **Use an Uptime Monitoring Service:**
        * Go to a free uptime monitoring service like [UptimeRobot](https://uptimerobot.com/) (they have a free tier).
        * Sign up for an account.
        * Once logged in, click "Add New Monitor".
        * **Monitor Type:** Select "HTTP(s)".
        * **Friendly Name:** Give it a name (e.g., `Crypto Bot Ping`).
        * **URL (or IP):** Paste your Render service URL (e.g., `https://crypto-signal-bot.onrender.com/`).
        * **Monitoring Interval:** Set this to something less than 15 minutes, for example, **5 minutes** (or even 1 minute to be extra safe).
        * **Alert Contacts:** You can set up alerts if your bot goes down, but for just keeping it alive, this isn't strictly necessary.
        * Click "Create Monitor".

    UptimeRobot (or a similar service) will now send an HTTP request to your Render bot's URL every 5 minutes. This traffic will tell Render that your service is "active," preventing it from spinning down. Your bot's main logic will continue to run in the background, sending Telegram alerts as configured.

    By following these steps, your bot should run continuously on Render's free tier!
    ```
