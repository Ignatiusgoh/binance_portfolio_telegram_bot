import logging
import time
import requests
from src.utils.binancehelpers import get_usdt_balance, get_open_positions
from src.utils.supabasehelpers import analyze_trades
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from supabase import create_client, Client as SupabaseClient

custom_keyboard = [
    ["📊 Show current portfolio balance"],
    ["📈 Show open positions"],
    ["📋 Show trade statistics"]
]
reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Choose an option below:", reply_markup=reply_markup)

async def handle_custom_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user = update.effective_user
    chat = update.effective_chat
    
    # Catch-all log to see EVERY message the bot sees
    logging.info(f"📥 RECEIVED: '{text}' from {user.first_name} ({user.id}) in {chat.type} chat ({chat.id})")

    if text == "📊 Show current portfolio balance":
        try:
            balance = get_usdt_balance()
            logging.info(f"Successfully fetched balance for user {user.id}: {balance}")
            await update.message.reply_text(f"💰 USDT Balance: {balance:.2f}", reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Error fetching balance for user {user.id}: {e}")
            await update.message.reply_text("❌ Error fetching balance. Check logs.", reply_markup=reply_markup)


    elif text == "📈 Show open positions":
        try:
            positions = get_open_positions()
            logging.info(f"Fetched {len(positions)} open positions for user {user.id}")
            if not positions:
                await update.message.reply_text("📭 No open positions.", reply_markup=reply_markup)
            else:
                msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
                await update.message.reply_text(f"📈 Open Positions:\n{msg}", reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Error fetching positions for user {user.id}: {e}")
            await update.message.reply_text("❌ Error fetching positions. Check logs.", reply_markup=reply_markup)

    elif text == "📋 Show trade statistics":
        try:
            logging.info(f"Calculating trade statistics for user {user.id}")
            stats = analyze_trades()
            await update.message.reply_text(f"📋 Trade Summary:\n{stats}", reply_markup=reply_markup)
            logging.info(f"Trade statistics sent to user {user.id}")
        except Exception as e:
            logging.error(f"Error fetching statistics for user {user.id}: {e}")
            await update.message.reply_text("❌ Error fetching statistics. Check logs.", reply_markup=reply_markup)
