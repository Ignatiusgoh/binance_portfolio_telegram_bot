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

def get_reply_markup():
    """Helper function to get the reply keyboard markup"""
    return ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Choose an option below:", reply_markup=get_reply_markup())

async def handle_custom_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message:
            logging.warning("⚠️ handle_custom_buttons called but update.message is None")
            return
        
        if not update.message.text:
            logging.warning(f"⚠️ handle_custom_buttons called but update.message.text is None. Message type: {type(update.message)}")
            return

        text = update.message.text
        user = update.effective_user
        chat = update.effective_chat
        
        # Catch-all log to see EVERY message the bot sees
        logging.info(f"📥 RECEIVED: '{text}' from {user.first_name if user else 'Unknown'} ({user.id if user else 'N/A'}) in {chat.type if chat else 'Unknown'} chat ({chat.id if chat else 'N/A'})")

        # Get reply_markup to ensure buttons persist
        reply_markup = get_reply_markup()

        if text == "📊 Show current portfolio balance":
            try:
                logging.info(f"Processing balance request for user {user.id if user else 'Unknown'}")
                balance = get_usdt_balance()
                logging.info(f"Successfully fetched balance for user {user.id if user else 'Unknown'}: {balance}")
                await update.message.reply_text(f"💰 USDT Balance: {balance:.2f}", reply_markup=reply_markup)
                logging.info(f"✅ Balance sent to user {user.id if user else 'Unknown'}")
            except Exception as e:
                logging.error(f"❌ Error fetching balance for user {user.id if user else 'Unknown'}: {e}", exc_info=True)
                await update.message.reply_text("❌ Error fetching balance. Check logs.", reply_markup=reply_markup)

        elif text == "📈 Show open positions":
            try:
                logging.info(f"Processing positions request for user {user.id if user else 'Unknown'}")
                positions = get_open_positions()
                logging.info(f"Fetched {len(positions)} open positions for user {user.id if user else 'Unknown'}")
                if not positions:
                    await update.message.reply_text("📭 No open positions.", reply_markup=reply_markup)
                else:
                    msg = "\n".join([f"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}" for p in positions])
                    await update.message.reply_text(f"📈 Open Positions:\n{msg}", reply_markup=reply_markup)
                logging.info(f"✅ Positions sent to user {user.id if user else 'Unknown'}")
            except Exception as e:
                logging.error(f"❌ Error fetching positions for user {user.id if user else 'Unknown'}: {e}", exc_info=True)
                await update.message.reply_text("❌ Error fetching positions. Check logs.", reply_markup=reply_markup)

        elif text == "📋 Show trade statistics":
            try:
                logging.info(f"Processing statistics request for user {user.id if user else 'Unknown'}")
                stats = analyze_trades()
                await update.message.reply_text(f"📋 Trade Summary:\n{stats}", reply_markup=reply_markup)
                logging.info(f"✅ Trade statistics sent to user {user.id if user else 'Unknown'}")
            except Exception as e:
                logging.error(f"❌ Error fetching statistics for user {user.id if user else 'Unknown'}: {e}", exc_info=True)
                await update.message.reply_text("❌ Error fetching statistics. Check logs.", reply_markup=reply_markup)
        else:
            # Log unmatched text for debugging
            logging.warning(f"⚠️ Received unmatched text: '{text}' from user {user.id if user else 'Unknown'}")
            await update.message.reply_text(f"❓ Unknown command: {text}", reply_markup=reply_markup)
            
    except Exception as e:
        logging.error(f"❌ Unexpected error in handle_custom_buttons: {e}", exc_info=True)
        if update and update.message:
            try:
                await update.message.reply_text("❌ An error occurred. Check logs for details.", reply_markup=get_reply_markup())
            except Exception as reply_error:
                logging.error(f"❌ Failed to send error message: {reply_error}")
