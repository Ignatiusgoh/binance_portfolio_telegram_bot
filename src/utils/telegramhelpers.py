import logging
import time
import requests
from binance.client import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from supabase import create_client, Client as SupabaseClient

