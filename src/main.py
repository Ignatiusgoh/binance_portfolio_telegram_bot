import logging
import time
import requests
import asyncio
from binance.client import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from src.utils.telegramhelpers import start, handle_custom_buttons
from src.utils.supabasehelpers import get_latest_order_logs
from src.utils.binancehelpers import get_order_details
import os 
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # ID of the group chat to post updates to
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# Store last processed order ID to avoid duplicate notifications
# In a production environment, this should be persisted to a file or database
last_processed_id = None

async def monitor_orders(context: ContextTypes.DEFAULT_TYPE):
    global last_processed_id
    
    if not CHAT_ID:
        logging.warning("⚠️ TELEGRAM_CHAT_ID not set in .env. Skipping order monitoring.")
        return

    logs = get_latest_order_logs(limit=10)
    if not logs:
        return

    # Sort logs by ID ascending to process them in order
    logs.sort(key=lambda x: x.get('id', 0))

    # Initialize last_processed_id on first run
    if last_processed_id is None:
        last_processed_id = logs[-1].get('id', 0)
        logging.info(f"Initialized order monitoring. Starting from ID: {last_processed_id}")
        return

    for log in logs:
        log_id = log.get('id', 0)
        if log_id > last_processed_id:
            order_type = log.get('type')
            direction = log.get('direction')
            order_id = log.get('order_id')
            symbol = "SOLUSDT" # Default or get from log if available

            # For entry trades (MO), we want to fetch the actual entry price
            entry_price = "N/A"
            if order_type == "MO":
                order_details = get_order_details(symbol, order_id)
                if order_details:
                    entry_price = order_details.get('avgPrice', "N/A")

            msg = f"🔔 *New Order Alert: {order_type}*\n\n"
            msg += f"🔹 *Direction:* {direction}\n"
            msg += f"🔹 *Order ID:* `{order_id}`\n"
            
            if order_type == "MO":
                msg += f"🔹 *Entry Price:* `{entry_price}`\n"
            
            msg += f"🔹 *Current Stoploss:* `{log.get('current_stop_loss')}`\n"
            msg += f"🔹 *Next Stoploss:* `{log.get('next_stoploss_price')}`\n"
            msg += f"🔹 *Trailing Price:* `{log.get('trailing_price')}`\n"
            msg += f"🔹 *Trailing Value:* `{log.get('trailing_value')}`"

            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg,
                    parse_mode='Markdown'
                )
                last_processed_id = log_id
            except Exception as e:
                logging.error(f"❌ Failed to send telegram notification: {e}")

# Build the application
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Add a job to the job queue to poll Supabase every 30 seconds
job_queue = app.job_queue
job_queue.run_repeating(monitor_orders, interval=30, first=10)

app.add_handler(CommandHandler("start", start))

# This keeps your old /balance, /positions, /stats commands (optional)
app.add_handler(CommandHandler("balance", handle_custom_buttons))
app.add_handler(CommandHandler("positions", handle_custom_buttons))
app.add_handler(CommandHandler("stats", handle_custom_buttons))

# This handles button taps with nice labels
# This filter ensures that the bot responds to text buttons even in groups
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_buttons))

print("Bot is running...")
app.run_polling()
