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

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
api_telegram1 = os.getenv("api_telegram1")
msg_id_telegram1 = os.getenv("msg_id_telegram1")
file_path = os.getenv("file_path")

client = Client(api_key, api_secret)

# pair="SHIBBUSD"
# coins="SHIBBUSD"
# current_price = client.get_symbol_ticker(symbol=coins)
# qty = int(15/(float(current_price['price'])))
# fees = client.get_trade_fee(symbol=pair)
# for item in fees:
    # qty = int(int(qty)-(float(item['takerCommission'])*int(qty)))
    # print(qty)

# current_price = client.get_symbol_ticker()
# for item in current_price:
    # #print(int(float(item['price'])))
    # if (int(float(item['price'])) < 1) and "BUSD" in item['symbol']:
        # print(item['symbol'],item['price'])

# crypto_coins = client.get_symbol_ticker()
# for item in crypto_coins:
    # if (int(float(item['price'])) < 1) and "BUSD" in item['symbol']:
        # print(item['symbol'])

# crypto_coins = client.futures_symbol_ticker()
# for item in crypto_coins:
# #    if (int(float(item['price'])) < 1) and item['symbol'].endswith('BUSD'):
        # print(item)

open_pos = client.futures_account()['asset']
print(open_pos)

# open_pos1 = client.get_account()['balances']
# for item in open_pos1:
    # if item['asset'] == 'SHIB':
        # print(item)

# open_pos1 = client.get_lending_position()
# for item in open_pos1:
    # print(item)