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

crypto_coins = client.get_symbol_ticker()
for item in crypto_coins:
    print(item['symbol'])
    # if (int(float(item['price'])) < 1) and item['symbol'].endswith('USDT'):
        # try:
            # df = getminutedata(item['symbol'], '4h', "60 days ago SGT")
            # myfile1 = Path(file_path+ item['symbol'] +'_buy_future_ema_potential_alert.txt')
            # myfile2 = Path(file_path+ item['symbol'] +'_sell_future_ema_potential_alert.txt')
            # myfile1.touch(exist_ok=True)
            # myfile2.touch(exist_ok=True)
            # strategy(item['symbol'])
            # time.sleep(10)
        # except Exception:
            # pass