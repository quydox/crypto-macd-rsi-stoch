from dotenv import load_dotenv
load_dotenv()
from binance import Client
import requests
import pandas as pd
import ta
import numpy as np
import time
import os
api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
api_telegram1 = os.getenv("api_telegram1")
msg_id_telegram1= os.getenv("msg_id_telegram1")
# body = "Test Upgrade"
# base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
# requests.get(base_url)

def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

client = Client(api_key, api_secret)
exchange_info = client.get_exchange_info()

for s in exchange_info['symbols']:
    try:
        df = getminutedata(s['symbol'], '4h', "30 days ago UTC")
        if df.Close.iloc[-1] < 0.000001:
            print(s['symbol'],df.Close.iloc[-1])
    except Exception:
        pass

# df = getminutedata('BTCUSDT', '4h', "30 days ago UTC")
# print(df)
# if df.Close.iloc[-1] > 0:
    # print(round(df.Close.iloc[-1]))