import logging
import time
import requests
from src.utils.binancehelpers import get_usdt_balance, get_open_positions
from src.utils.supabasehelpers import analyze_trades
from telegram.ext import ApplicationBuilder, CommandHandler, ContextType, CallbackQueryHandler, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from supabase import create_client, Client as SupabaseClient

keyboard = [["/balance", "/positions", "/stats"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Show current portfolio balance", callback_data="balance")],
        [InlineKeyboardButton("📈 Show open positions", callback_data="positions")],
        [InlineKeyboardButton("📋 Show trade statistics", callback_data="stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option below:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    data = query.data

    if data == "balance":
        balance = get_usdt_balance()
        await query.edit_message_text(f"💰 Current USDT Balance: {balance:.2f}")
    elif data == "positions":
        positions = get_open_positions()
        if not positions:
            await query.edit_message_text("📭 No open positions.")
        else:
            msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
            await query.edit_message_text(f"📈 Open Positions:\n{msg}")
    elif data == "stats":
        stats = analyze_trades()
        await query.edit_message_text(f"📋 Trade Summary:\n{stats}")



# async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     balance = get_usdt_balance()
#     await update.message.reply_text(f"Your USDT balance: {balance:.2f}")

# async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     positions = get_open_positions()
#     if not positions:
#         await update.message.reply_text("No open positions.")
#         return
#     msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
#     await update.message.reply_text(f"Open Positions:\n{msg}")

# async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     summary = analyze_trades()
#     await update.message.reply_text(f"Trade Summary:\n{summary}")