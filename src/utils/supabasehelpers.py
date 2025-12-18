import logging
import time
import requests
from supabase import create_client, Client as SupabaseClient
import os 
from dotenv import load_dotenv
import time

load_dotenv()

orders_table = "orders" 
order_groups_table = "order_groups" 
trades_table = "trades" 

def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("❌ SUPABASE_URL or SUPABASE_API_KEY is not set in environment variables.")

    return create_client(supabase_url, supabase_key)

def analyze_trades():
    supabase = get_supabase_client()
    max_retries = 5
    retry_delay = 0.5  # seconds

    trades = None
    for attempt in range(max_retries):
        try:
            response = supabase.table(trades_table).select("*").order("entry_time").execute()
            trades = response.data
            if trades is not None:
                break  # Exit loop if we got valid data
        except Exception as e:
            logging.warning(f"⚠️ Attempt {attempt + 1} failed to fetch from {trades_table}: {e}")
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
        if trade.get('is_closed', 0) == True:
            pnl = trade.get('realized_pnl', 0)
            
            if pnl > 0.5:
                win += 1
            elif pnl < -0.5:
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

    msg = f"📊 Trade Results ({trades_table}):\n"
    msg += f"Wins: {win}, Losses: {loss}, Breakeven: {breakeven}, Total: {total}\n"
    msg += f"Total Realized PnL: {total_pnl:.4f}\n"
    msg += f"Max Drawdown: {max_drawdown:.4f}\n"

    return msg

def get_latest_order_logs(limit=5):
    """Fetches the latest order logs from the order_groups table."""
    supabase = get_supabase_client()
    try:
        # Assuming order_groups has an 'id' or 'created_at' field for ordering.
        # If not, we might need to use order_id or group_id if they are monotonic.
        # Most Supabase tables have a created_at or id by default.
        response = supabase.table(order_groups_table).select("*").order("order_id", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        logging.error(f"❌ Error fetching latest order logs: {e}")
        return []


