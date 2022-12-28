from dotenv import load_dotenv
load_dotenv()
import yfinance as yf
from pathlib import Path
import requests
import pandas as pd
import ta
import numpy as np
from math import floor
import datetime
import time
import os


api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
api_telegram1 = os.getenv("api_telegram1")
msg_id_telegram1 = os.getenv("msg_id_telegram1")
file_path = os.getenv("file_path")

def getminutedata(symbol):
    frame = pd.DataFrame(yf.download(symbol, interval = "1m", period = "1d"))
    frame = frame.iloc[:,:4]
    frame.columns = ['Open', 'High', 'Low', 'Close']
    frame = frame.astype(float)
    return frame

# df = getminutedata("AUDCHF=X")
#print(df.High)
#df.to_csv("final.csv")

def applytechnicals(df):
    df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=6, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=6)
    df['macd'] = ta.trend.macd_diff(df.Close, window_slow=21, window_fast=8, window_sign=5)
    df['ema7'] = ta.trend.ema_indicator(df.Close, window=7)
    df['ema25'] = ta.trend.ema_indicator(df.Close, window=25)
    df['ema99'] = ta.trend.ema_indicator(df.Close, window=99)
    df.dropna(inplace=True)

# applytechnicals(df)
#print(df)

class Signals:
    def __init__(self,df, lags):
        self.df = df
        self.lags = lags

    def decide(self):
        self.df['Buy'] = np.where((self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.rsi > 50) & (self.df.macd > 0) & (self.df.ema7 > self.df.ema25) & (self.df.ema7 > self.df.ema99) & (self.df.ema25 > self.df.ema99), 1, 0)
        self.df['Sell'] = np.where((self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.rsi < 50) & (self.df.macd < 0) & (self.df.ema7 < self.df.ema25) & (self.df.ema7 < self.df.ema99) & (self.df.ema25 < self.df.ema99), 1, 0)
        self.df['Stochastic'] = np.where((self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)), 1, 0)
        self.df['rsiBUY'] = np.where((self.df.rsi > 50), 1, 0)
        self.df['macdBUY'] = np.where((self.df.macd > 0), 1, 0)
        self.df['emaBUY1'] = np.where((self.df.ema7 > self.df.ema25), 1, 0)
        self.df['emaBUY2'] = np.where((self.df.ema7 > self.df.ema99), 1, 0)
        self.df['emaBUY3'] = np.where((self.df.ema25 > self.df.ema99), 1, 0)
        self.df['macdSELL'] = np.where((self.df.macd < 0), 1, 0)
        self.df['rsiSELL'] = np.where((self.df.rsi < 50), 1, 0)
        self.df['emaSELL1'] = np.where((self.df.ema7 < self.df.ema25), 1, 0)
        self.df['emaSELL2'] = np.where((self.df.ema7 < self.df.ema99), 1, 0)
        self.df['emaSELL3'] = np.where((self.df.ema25 < self.df.ema99), 1, 0)
        self.df['uptrend'] = np.where((self.df.ema7 > self.df.ema99) & (self.df.ema25 > self.df.ema99), 1, 0)
        self.df['downtrend'] = np.where((self.df.ema7 < self.df.ema99) & (self.df.ema25 < self.df.ema99), 1, 0)

# inst = Signals(df, 2)
# inst.decide()
# print(df)

def strategy(pair):
    applytechnicals(df)
    inst = Signals(df, 5)
    inst.decide()
    print(df)
    if df.Buy.iloc[-1] & df.uptrend.iloc[-1]:
        body = "BUY -" + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1])
        base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
        requests.get(base_url)
        print(body)
        time.sleep(60)
    elif df.Sell.iloc[-1] & df.downtrend.iloc[-1]:
        body = "SELL -" + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1])
        base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
        requests.get(base_url)
        print(body)
        time.sleep(60)
while True:
    crypto_coins = ["AUDCHF=X"]
    for coins in crypto_coins:
        # try:
        df = getminutedata(coins)
        strategy(coins)
        time.sleep(5)
        # except Exception:
        #    pass