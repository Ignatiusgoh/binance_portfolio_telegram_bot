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
from src.utils.logger import init_logger
import os 
from dotenv import load_dotenv

# Initialize logger at the very start
init_logger()
logging.info("🚀 Starting Bot...")

try:
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not TELEGRAM_TOKEN:
        logging.error("❌ TELEGRAM_TOKEN is missing from .env!")
except Exception as e:
    logging.error(f"❌ Error loading environment variables: {e}")

# ... rest of the code ...

# Store last processed timestamp to avoid duplicate notifications
# In a production environment, this should be persisted to a file or database
last_processed_timestamp = None

async def monitor_orders(context: ContextTypes.DEFAULT_TYPE):
    global last_processed_timestamp
    
    logging.info("🔄 Running order monitoring check...")
    
    if not CHAT_ID:
        logging.warning("⚠️ TELEGRAM_CHAT_ID not set in .env. Skipping order monitoring.")
        return

    logs = get_latest_order_logs(limit=10)
    if not logs:
        logging.info("ℹ️ No logs found in order_groups table")
        return

    # Sort logs by created_at ascending to process them chronologically
    # ISO timestamp strings can be compared directly as strings
    try:
        logs.sort(key=lambda x: x.get('created_at', '') if x.get('created_at') else '')
        created_ats = [log.get('created_at') for log in logs]
        logging.info(f"📊 Monitoring orders. Current last_processed_timestamp: {last_processed_timestamp}, Found {len(logs)} logs (created_ats: {created_ats})")
    except Exception as e:
        logging.error(f"❌ Error processing created_at timestamps: {e}. Logs: {logs}")
        return

    # Initialize last_processed_timestamp on first run
    if last_processed_timestamp is None:
        if logs:
            last_processed_timestamp = logs[-1].get('created_at')
            logging.info(f"Initialized order monitoring. Starting from created_at: {last_processed_timestamp}")
        else:
            last_processed_timestamp = ""
            logging.info("Initialized order monitoring. No existing logs found.")
        return

    new_orders_found = 0
    for log in logs:
        log_created_at = log.get('created_at')
        if not log_created_at:
            logging.warning(f"⚠️ Log missing created_at field: {log}")
            continue
        
        # Compare timestamps as strings (ISO format strings compare correctly)
        if log_created_at > last_processed_timestamp:
            new_orders_found += 1
            order_type = log.get('type')
            direction = log.get('direction')
            binance_order_id = log.get('order_id')  # This is the Binance order ID
            symbol = "SOLUSDT" # Default or get from log if available

            # For entry trades (MO), we want to fetch the actual entry price
            entry_price = "N/A"
            if order_type == "MO":
                order_details = get_order_details(symbol, binance_order_id)
                if order_details:
                    entry_price = order_details.get('avgPrice', "N/A")

            msg = f"🔔 *New Order Alert: {order_type}*\n\n"
            msg += f"🔹 *Direction:* {direction}\n"
            msg += f"🔹 *Order ID:* `{binance_order_id}`\n"
            
            if order_type == "MO":
                msg += f"🔹 *Entry Price:* `{entry_price}`\n"
            
            msg += f"🔹 *Current Stoploss:* `{log.get('current_stop_loss')}`\n"
            msg += f"🔹 *Next Stoploss:* `{log.get('next_stoploss_price')}`\n"
            msg += f"🔹 *Trailing Price:* `{log.get('trailing_price')}`\n"
            msg += f"🔹 *Trailing Value:* `{log.get('trailing_value')}`"

            try:
                logging.info(f"📤 Sending notification for order created_at {log_created_at} (type: {order_type}, direction: {direction})")
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg,
                    parse_mode='Markdown'
                )
                last_processed_timestamp = log_created_at
                logging.info(f"✅ Successfully sent notification. Updated last_processed_timestamp to {last_processed_timestamp}")
            except Exception as e:
                logging.error(f"❌ Failed to send telegram notification for order created_at {log_created_at}: {e}")
    
    if new_orders_found == 0:
        logging.info(f"ℹ️ No new orders found (last_processed_timestamp: {last_processed_timestamp})")
    else:
        logging.info(f"✅ Processed {new_orders_found} new order(s)")

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
