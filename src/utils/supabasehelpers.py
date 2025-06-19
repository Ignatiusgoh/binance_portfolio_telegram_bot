import logging
import time
import requests
from supabase import create_client, Client as SupabaseClient
import os 
from dotenv import load_dotenv
import time

load_dotenv()

# Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")
print(supabase_url)
print(supabase_key)
supabase = create_client(supabase_url, supabase_key)

def analyze_trades():
    max_retries = 5
    retry_delay = 0.5  # seconds

    trades = None
    for attempt in range(max_retries):
        try:
            response = supabase.table("trades").select("*").order("entry_time").execute()
            trades = response.data
            if trades is not None:
                break  # Exit loop if we got valid data
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(retry_delay)

    if trades is None:
        return "❌ Failed to fetch trade data after 5 attempts."

    # Process trades
    win = 0
    loss = 0
    breakeven = 0
    cumulative_pnl = []
    total_pnl = 0

    for trade in trades:
        pnl = trade.get('realized_pnl', 0)

        if pnl > 1:
            win += 1
        elif pnl < -1:
            loss += 1
        else:
            breakeven += 1

        total_pnl += pnl
        cumulative_pnl.append(total_pnl)

    # Calculate Max Drawdown
    max_drawdown = 0
    peak = float('-inf')
    for value in cumulative_pnl:
        if value > peak:
            peak = value
        drawdown = peak - value
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    total = len(trades)
    return (
        f"Wins: {win}, Losses: {loss}, Breakeven: {breakeven}, Total: {total}\n"
        f"Total Realized PnL: {total_pnl:.4f}\n"
        f"Max Drawdown: {max_drawdown:.4f}"
    )

    
print(analyze_trades())