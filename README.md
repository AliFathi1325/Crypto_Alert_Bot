<!-- @format -->

# Cryptocurrency Trading Assistant Bot

This Telegram bot provides users with real-time cryptocurrency prices and allows them to set price alerts for their favorite cryptocurrencies. It utilizes the CoinMarketCap website to fetch current price data and SQLite for storing user alerts.

## Features

- Fetch current prices for cryptocurrencies like Bitcoin and Ethereum.
- Set alerts for specific price thresholds.
- Receive notifications when the current price meets the specified conditions.

## Requirements

- Python
- `requests` library
- `beautifulsoup4` library
- `python-telegram-bot` library
- `python-dotenv` library
- `sqlite3` (included with Python)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/AliFathi1325/Crypto_Alert_Bot.git
   cd cryptocurrency-bot
   ```

2. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your Telegram bot token:

   ```plaintext
   BOT_TOKEN=your_telegram_bot_token
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

- Start the bot by sending `/start` to it in your Telegram chat.
- Select options to view current cryptocurrency prices or create a price alert.
- For price alerts, specify the price at which you want to be notified.
