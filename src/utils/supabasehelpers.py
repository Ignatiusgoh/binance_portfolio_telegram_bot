import logging
import time
import requests
from supabase import create_client, Client as SupabaseClient
import os 
from dotenv import load_dotenv

load_dotenv()

# Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")
print(supabase_url)
print(supabase_key)
supabase = create_client(supabase_url, supabase_key)

def analyze_trades():
    try:
        response = supabase.table("trades") \
            .select("*") \
            .execute()
        trades = response.data
        print(trades)
        # win = sum(1 for t in trades if t['result'] == 'win')
        # loss = sum(1 for t in trades if t['result'] == 'loss')
        # breakeven = sum(1 for t in trades if t['result'] == 'breakeven')
        # total = len(trades)
        # return f"Wins: {win}, Losses: {loss}, Breakeven: {breakeven}, Total: {total}"
    except Exception as e:
        print(f"Error fetching trade data: {e}")
        return f"Error fetching trade data: {e}"
    
analyze_trades()