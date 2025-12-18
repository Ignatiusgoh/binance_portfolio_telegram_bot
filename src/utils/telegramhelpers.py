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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose an option below:", reply_markup=reply_markup)

async def handle_custom_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    chat = update.effective_chat
    
    logging.info(f"Button pressed: '{text}' | User: {user.first_name} ({user.id}) | Chat: {chat.title if chat.title else 'Private'} ({chat.id})")

    if text == "📊 Show current portfolio balance":
        try:
            balance = get_usdt_balance()
            logging.info(f"Successfully fetched balance for user {user.id}: {balance}")
            await update.message.reply_text(f"💰 USDT Balance: {balance:.2f}")
        except Exception as e:
            logging.error(f"Error fetching balance for user {user.id}: {e}")
            await update.message.reply_text("❌ Error fetching balance. Check logs.")


    elif text == "📈 Show open positions":
        try:
            positions = get_open_positions()
            logging.info(f"Fetched {len(positions)} open positions for user {user.id}")
            if not positions:
                await update.message.reply_text("📭 No open positions.")
            else:
                msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
                await update.message.reply_text(f"📈 Open Positions:\n{msg}")
        except Exception as e:
            logging.error(f"Error fetching positions for user {user.id}: {e}")
            await update.message.reply_text("❌ Error fetching positions. Check logs.")

    elif text == "📋 Show trade statistics":
        try:
            logging.info(f"Calculating trade statistics for user {user.id}")
            stats = analyze_trades()
            await update.message.reply_text(f"📋 Trade Summary:\n{stats}")
            logging.info(f"Trade statistics sent to user {user.id}")
        except Exception as e:
            logging.error(f"Error fetching statistics for user {user.id}: {e}")
            await update.message.reply_text("❌ Error fetching statistics. Check logs.")
