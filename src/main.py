import logging
import time
import requests
from binance.client import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from src.utils.telegramhelpers import start, handle_custom_buttons
import os 
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))

# This keeps your old /balance, /positions, /stats commands (optional)
app.add_handler(CommandHandler("balance", handle_custom_buttons))
app.add_handler(CommandHandler("positions", handle_custom_buttons))
app.add_handler(CommandHandler("stats", handle_custom_buttons))

# This handles button taps with nice labels
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_buttons))

print("Bot is running...")
app.run_polling()