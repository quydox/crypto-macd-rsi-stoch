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

# crypto_coins = client.futures_symbol_ticker()
# for item in crypto_coins:
# #    if (int(float(item['price'])) < 1) and item['symbol'].endswith('BUSD'):
        # print(item)

# open_pos = client.futures_account()['positions']
# for item in open_pos:
    # if item['symbol'] == '1000SHIBBUSD':
        # print(item)

# open_pos1 = client.get_account()['balances']
# for item in open_pos1:
    # if item['asset'] == 'SHIB':
        # print(item)

# open_pos1 = client.get_account()['balances']
# for item in open_pos1:
    # if item['asset'] == 'SHIB':
        # print(item)

# ticker_test = client.get_ticker(symbol='SHIBBUSD')
# print(ticker_test)

# get_asset = client.get_asset_details(asset='SHIB')
# print(get_asset)

# get_orders = client.get_my_trades(symbol='SHIBBUSD')
# for item in get_orders:
    # print(item['isMaker'],item['qty'],item['price'])

# open_pos = client.futures_get_open_orders()
# print(open_pos)
# for item in open_pos:
    # print(item)

# exchange_info = client.get_exchange_info()
# for item in exchange_info:
    # print(item['symbols'])

#acc_balance = client.futures_account_balance()
#for check_balance in acc_balance:
#    if check_balance['asset'] == "BUSD":
#        busd_balance = check_balance["balance"]
#        print(int(float(busd_balance))/168 * 100 - 100)

#active_position = client.futures_account()['positions']
# for item in active_position:
    # if item['symbol'] == "BTCBUSD":
        # print(item)

active_position = client.futures_position_information(symbol='BTCBUSD')
for item in active_position:
    if int(float(df.Close.iloc[-1])) > int(float(item['entryPrice'])):
        print("BUY")
    else:
        print("SELL")

# current_price = client.get_symbol_ticker(symbol='BTCBUSD')
# print(int(float(current_price['price']) * 0.995))

# print(int(float(current_price['price']) * 1.005))


# fees = client.get_trade_fee(symbol='BTCBUSD')
# print(fees)