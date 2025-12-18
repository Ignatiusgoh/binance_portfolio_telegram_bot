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

    if text == "📊 Show current portfolio balance":
        balance = get_usdt_balance()
        await update.message.reply_text(f"💰 USDT Balance: {balance:.2f}")


    elif text == "📈 Show open positions":
        positions = get_open_positions()
        if not positions:
            await update.message.reply_text("📭 No open positions.")

        else:
            msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
            await update.message.reply_text(f"📈 Open Positions:\n{msg}")

    elif text == "📋 Show trade statistics":
        stats = analyze_trades()
        await update.message.reply_text(f"📋 Trade Summary:\n{stats}")
