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
api_key_strat_1 = os.getenv('BINANCE_API_KEY_STRAT_1')
api_secret_strat_1 = os.getenv('BINANCE_API_SECRET_STRAT_1')
api_key_strat_2 = os.getenv('BINANCE_API_KEY_STRAT_1')
api_secret_strat_2 = os.getenv('BINANCE_API_SECRET_STRAT_1')

client_strat_1 = Client(api_key=api_key_strat_1, api_secret=api_secret_strat_1)
client_strat_2 = Client(api_key=api_key_strat_2, api_secret=api_secret_strat_2)

def get_usdt_balance():
    while True:
        try:
            futures_account_strat_1 = client_strat_1.futures_account()
            for asset in futures_account_strat_1['assets']:
                if asset['asset'] == 'USDT':
                    strat_1_usdt_balance = float(asset['marginBalance'])
            
            futures_account_strat_2 = client_strat_2.futures_account()
            for asset in futures_account_strat_2['assets']:
                if asset['asset'] == 'USDT':
                    strat_2_usdt_balance = float(asset['marginBalance'])
            return strat_1_usdt_balance, strat_2_usdt_balance
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching balance: {e}. Retrying")
            time.sleep(0.1)

def get_open_positions():
    try:
        positions_strat_1 = client_strat_1.futures_account()['positions']
        open_positions_strat_1 = [p for p in positions_strat_1 if float(p['positionAmt']) != 0]
        positions_strat_2 = client_strat_2.futures_account()['positions']
        open_positions_strat_2 = [p for p in positions_strat_2 if float(p['positionAmt']) != 0]

        return open_positions_strat_1, open_positions_strat_2
    except Exception as e:
        logging.warning(f"⚠️ Error fetching positions: {e}")
        return []