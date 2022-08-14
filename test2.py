from dotenv import load_dotenv
load_dotenv()
from binance import Client
import requests
import pandas as pd
import ta
import numpy as np
import time
import os
from pathlib import Path

# api_key = os.getenv("api_key")
# api_secret = os.getenv("api_secret")
# api_telegram1 = os.getenv("api_telegram1")
# msg_id_telegram1= os.getenv("msg_id_telegram1")

# client = Client(api_key, api_secret)
# exchange_info = client.get_exchange_info()

# def getminutedata(symbol, interval, lookback):
    # frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback))
    # frame = frame.iloc[:,:6]
    # frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    # frame = frame.set_index('Time')
    # frame.index = pd.to_datetime(frame.index, unit='ms')
    # frame = frame.astype(float)
    # return frame

# # from pathlib import Path
# # myfile = Path('text.txt')
# # myfile.touch(exist_ok=True)
# # f = open(myfile)
# crypto_coins = ["BTCUSDT", "SLPUSDT", "AXSUSDT", "ETHUSDT", "SHIBUSDT"]
# for coins in crypto_coins:
    # try:
        # df = getminutedata(coins, '4h', "30 day ago UTC")
        # myfile1 = Path(coins+'_buy_1h.txt')
        # myfile2 = Path(coins+'_sell_1h.txt')
        # # print(myfile1)
        # # print(myfile2)
        # myfile1.touch(exist_ok=True)
        # myfile2.touch(exist_ok=True)
        # f = open(myfile1,myfile)
            # # strategy(coins['symbol'], 50)
            # # time.sleep(10)
    # except Exception:
        # pass
file_path = os.getcwd()+'\\'
print(file_path)