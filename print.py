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

pair="SHIBBUSD"
current_price = client.get_symbol_ticker(symbol=coins)
qty = int(15/(float(current_price['price'])))
fees = client.get_trade_fee(symbol=pair)
for item in fees:
    qty = int(qty)-(float(item['takerCommission'])*int(qty))
    print(qty)