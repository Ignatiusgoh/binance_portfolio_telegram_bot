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
api_key_strat = os.getenv('BINANCE_API_KEY')
api_secret_strat = os.getenv('BINANCE_API_SECRET')

client_strat = Client(api_key=api_key_strat, api_secret=api_secret_strat)


def get_usdt_balance():
    while True:
        try:
            futures_account_strat = client_strat.futures_account()
            for asset in futures_account_strat['assets']:
                if asset['asset'] == 'USDT':
                    strat_usdt_balance = float(asset['marginBalance'])
            
            return strat_usdt_balance
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching balance: {e}. Retrying")
            time.sleep(0.1)

def get_open_positions():
    try:
        positions_strat = client_strat.futures_account()['positions']
        open_positions_strat = [p for p in positions_strat if float(p['positionAmt']) != 0]

        return open_positions_strat
    except Exception as e:
        logging.warning(f"⚠️ Error fetching positions: {e}")
        return []

def get_order_details(symbol, order_id):
    """Fetches order details from Binance Futures."""
    try:
        order = client_strat.futures_get_order(symbol=symbol, orderId=order_id)
        return order
    except Exception as e:
        logging.error(f"❌ Error fetching order {order_id}: {e}")
        return None
    
if __name__ == '__main__': 
    print(get_usdt_balance())