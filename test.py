from dotenv import load_dotenv
load_dotenv()
from binance import Client
from pathlib import Path
import requests
import pandas as pd
import ta
import numpy as np
import time
import os
import json
import hashlib
import hmac

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
api_telegram1 = os.getenv("api_telegram1")
msg_id_telegram1 = os.getenv("msg_id_telegram1")
file_path = os.getenv("file_path")

client = Client(api_key, api_secret)

# API endpoint for trades
ENDPOINT = 'https://api.binance.com/api/v3/myTrades'

# Get all trades for a specific symbol
def get_trades(symbol):
    # Build query string parameters
    params = {
        'symbol': symbol,
        'timestamp': int(time.time() * 1000),
        'recvWindow': 5000
    }
    # Generate signature for request
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(bytes(api_secret, 'utf-8'), bytes(query_string, 'utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    # Send request
    response = requests.get(ENDPOINT, headers={'X-MBX-APIKEY': api_key}, params=params)
    return json.loads(response.text)

# Calculate PNL for all trades
def calculate_pnl(trades):
    total_pnl = 0
    for trade in trades:
        if trade['isBuyer']:
            # Bought the asset
            bought_amount = float(trade['qty'])
            bought_price = float(trade['price'])
            sold_amount = 0
            sold_price = 0
        else:
            # Sold the asset
            bought_amount = 0
            bought_price = 0
            sold_amount = float(trade['qty'])
            sold_price = float(trade['price'])
        # Calculate PNL for the trade
        pnl = (sold_amount * sold_price) - (bought_amount * bought_price)
        # Add PNL to total
        total_pnl += pnl
    return total_pnl

# Specify the symbol you want to fetch trades for
#symbol = 'BTCUSDT'
symbol = 'BTCBUSD'

# Get all trades for the specified symbol
trades = get_trades(symbol)

# Calculate PNL for all trades
pnl = calculate_pnl(trades)

# Print PNL
print(f"Total PNL for {symbol}: {pnl}")