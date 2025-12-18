# Telegram Trading Monitor Bot

A Telegram bot that monitors your Binance futures trading portfolio and provides real-time updates on orders, positions, and trade statistics. The bot also automatically posts notifications when new orders are placed or stop-loss orders are updated.

## Features

- 📊 **Portfolio Balance**: View your current USDT balance
- 📈 **Open Positions**: Check all active futures positions
- 📋 **Trade Statistics**: View win/loss statistics, total PnL, and max drawdown
- 🔔 **Order Notifications**: Automatic alerts when new orders (MO/SL) are placed
- 📝 **Comprehensive Logging**: All activities logged to `telegram_bot.log`

## Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))
- Binance Futures API credentials (API Key and Secret)
- Supabase credentials (URL and API Key)
- A Telegram group chat ID (for order notifications)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd telegram_monitoring_bot
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install "python-telegram-bot[job-queue]" python-binance supabase python-dotenv
   ```

## Configuration

1. **Create a `.env` file in the project root:**
   ```bash
   touch .env
   ```

2. **Add your credentials to `.env`:**
   ```env
   # Telegram Bot Configuration
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_group_chat_id_here

   # Binance API Configuration
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_API_SECRET=your_binance_api_secret_here

   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_API_KEY=your_supabase_api_key_here
   ```

### Getting Your Telegram Chat ID

To get your group chat ID:
1. Add the bot to your group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":-1001234567890}` - the negative number is your chat ID

Alternatively, you can use bots like `@userinfobot` or `@getidsbot` in your group.

### Setting Up Telegram Bot Privacy

**Important for Group Chats:** If you want the bot to respond to buttons in group chats, you must disable Privacy Mode:

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/setprivacy`
3. Select your bot
4. Choose **Disabled**

This allows the bot to see all messages in the group, not just commands and mentions.

## Running the Bot

### Local Development

From the project root directory:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the bot
python3 -m src.main
```

**Important:** Always run from the project root using `python3 -m src.main`, not `python3 src/main.py`

### Running on a Server (DigitalOcean, AWS, etc.)

#### Option 1: Using tmux (Quick & Simple)

1. **SSH into your server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Navigate to the project directory:**
   ```bash
   cd /path/to/telegram_monitoring_bot
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Create a tmux session:**
   ```bash
   tmux new -s trading-bot
   ```

5. **Run the bot:**
   ```bash
   python3 -m src.main
   ```

6. **Detach from tmux (keeps bot running):**
   - Press `Ctrl + B`, then press `D`

7. **Re-attach later to view logs:**
   ```bash
   tmux attach -t trading-bot
   ```

#### Option 2: Using systemd (Production - Auto-restart on crash/reboot)

1. **Create a systemd service file:**
   ```bash
   sudo nano /etc/systemd/system/trading-bot.service
   ```

2. **Add the following content (adjust paths as needed):**
   ```ini
   [Unit]
   Description=Telegram Trading Monitor Bot
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/binance_portfolio_telegram_bot
   Environment="PATH=/root/binance_portfolio_telegram_bot/venv/bin"
   ExecStart=/root/binance_portfolio_telegram_bot/venv/bin/python -m src.main
   Restart=always
   RestartSec=10
   StandardOutput=append:/root/binance_portfolio_telegram_bot/telegram_bot.log
   StandardError=append:/root/binance_portfolio_telegram_bot/telegram_bot.log

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable trading-bot
   sudo systemctl start trading-bot
   ```

4. **Check status:**
   ```bash
   sudo systemctl status trading-bot
   ```

5. **View logs:**
   ```bash
   sudo journalctl -u trading-bot -f
   ```

## Usage

1. **Start the bot** (see Running the Bot section above)

2. **Open Telegram** and find your bot

3. **Send `/start`** to initialize the keyboard buttons

4. **Use the buttons:**
   - 📊 **Show current portfolio balance**: Displays your USDT balance
   - 📈 **Show open positions**: Lists all active futures positions
   - 📋 **Show trade statistics**: Shows win/loss stats, total PnL, and max drawdown

5. **Order Notifications**: The bot automatically monitors your Supabase `order_groups` table and sends notifications to your group chat whenever:
   - A new market order (MO) is placed (LONG or SHORT)
   - A stop-loss order (SL) is placed or updated

## Logging

All bot activities are logged to `telegram_bot.log` in the project root directory.

**View logs in real-time:**
```bash
tail -f telegram_bot.log
```

**View recent logs:**
```bash
tail -n 100 telegram_bot.log
```

## Troubleshooting

### Buttons Not Working

1. **Check Privacy Mode**: Ensure Privacy Mode is disabled (see Configuration section)
2. **Send `/start`**: The bot needs to be initialized with `/start` first
3. **Check logs**: Look for `📥 RECEIVED:` entries in `telegram_bot.log` to see if messages are reaching the bot

### Bot Not Starting

1. **Check environment variables**: Ensure all required variables are set in `.env`
2. **Check virtual environment**: Make sure you've activated the venv
3. **Check dependencies**: Run `pip list` to verify all packages are installed
4. **Check logs**: The bot logs startup errors to `telegram_bot.log`

### Order Notifications Not Appearing

1. **Verify `TELEGRAM_CHAT_ID`**: Ensure it's set correctly in `.env`
2. **Check Supabase connection**: Verify your Supabase credentials are correct
3. **Check table name**: Ensure the `order_groups` table exists in your Supabase database
4. **Check logs**: Look for errors in `telegram_bot.log` related to Supabase queries

### Import Errors

If you see `ModuleNotFoundError: No module named 'src'`:
- Always run from the project root: `python3 -m src.main`
- Never run: `python3 src/main.py` (this breaks imports)

## Project Structure

```
telegram_monitoring_bot/
├── src/
│   ├── main.py                 # Main bot entry point
│   └── utils/
│       ├── binancehelpers.py   # Binance API interactions
│       ├── supabasehelpers.py # Supabase database queries
│       ├── telegramhelpers.py # Telegram button handlers
│       └── logger.py          # Logging configuration
├── venv/                       # Virtual environment
├── .env                        # Environment variables (create this)
├── telegram_bot.log           # Log file (created automatically)
└── README.md                   # This file
```

## Support

For issues or questions:
1. Check the logs in `telegram_bot.log`
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed

## License

This project is for personal use. Use at your own risk when trading with real funds.

