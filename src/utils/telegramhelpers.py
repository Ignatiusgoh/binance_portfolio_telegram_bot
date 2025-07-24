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
        await update.message.reply_text(f"💰 STRATEGY 1 Current USDT Balance: {balance[0]:.2f}")
        await update.message.reply_text(f"💰 STRATEGY 2 Current USDT Balance: {balance[1]:.2f}")

    elif text == "📈 Show open positions":
        positions = get_open_positions()
        if not positions[0]:
            await update.message.reply_text("📭 STRATEGY 1 No open positions.")
        if not positions[1]:
            await update.message.reply_text("📭 STRATEGY 2 No open positions.")
        else:
            msg_1 = "\n".join([f"STRATEGY 1 {p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions[0]])
            msg_2 = "\n".join([f"STRATEGY 2 {p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions[1]])
            await update.message.reply_text(f"📈 Open Positions:\n{msg_1}\n{msg_2}")

    elif text == "📋 Show trade statistics":
        stats = analyze_trades()
        await update.message.reply_text(f"📋 Trade Summary:\n{stats}")
