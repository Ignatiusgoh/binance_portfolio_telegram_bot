import logging
import time
import requests
from binance.client import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from supabase import create_client, Client as SupabaseClient
import os 
from dotenv import load_dotenv

load_dotenv()

# Binance API Keys
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
client = Client(api_key=api_key, api_secret=api_secret)

def get_usdt_balance():
    while True:
        try:
            futures_account = client.futures_account()
            for asset in futures_account['assets']:
                if asset['asset'] == 'USDT':
                    return float(asset['marginBalance'])
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching balance: {e}. Retrying")
            time.sleep(0.1)

def get_open_positions():
    try:
        positions = client.futures_account()['positions']
        open_positions = [p for p in positions if float(p['positionAmt']) != 0]
        return open_positions
    except Exception as e:
        logging.warning(f"⚠️ Error fetching positions: {e}")
        return []