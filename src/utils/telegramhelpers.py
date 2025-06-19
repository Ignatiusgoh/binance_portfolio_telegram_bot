import logging
import time
import requests
from src.utils.binancehelpers import get_usdt_balance, get_open_positions
from src.utils.supabasehelpers import analyze_trades
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from supabase import create_client, Client as SupabaseClient

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = get_usdt_balance()
    await update.message.reply_text(f"Your USDT balance: {balance:.2f}")

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    positions = get_open_positions()
    if not positions:
        await update.message.reply_text("No open positions.")
        return
    msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
    await update.message.reply_text(f"Open Positions:\n{msg}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = analyze_trades()
    await update.message.reply_text(f"Trade Summary:\n{summary}")