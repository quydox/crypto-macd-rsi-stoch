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
    frame = pd.DataFrame(yf.download(symbol, interval = "5m", period = "7d"))
    frame = frame.iloc[:,:4]
    frame.columns = ['Open', 'High', 'Low', 'Close']
    frame = frame.astype(float)
    return frame

# df = getminutedata("AUDCHF=X")
#print(df.High)

def applytechnicals(df):
    df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=6)
    df['macd'] = ta.trend.macd_diff(df.Close, window_slow=21, window_fast=8, window_sign=5)
    df.dropna(inplace=True)

# applytechnicals(df)
#print(df)

class Signals:
    def __init__(self,df, lags):
        self.df = df
        self.lags = lags

    def decide(self):
        self.df['Buy'] = np.where((self.df['%K'] > self.df['%D']) & (self.df.rsi > 50) & (self.df.macd > 0), 1, 0)
        self.df['Sell'] = np.where((self.df['%K'] < self.df['%D']) & (self.df.rsi < 50) & (self.df.macd < 0), 1, 0)
        self.df['stbuy'] = np.where((self.df['%K'] > self.df['%D']), 1, 0)
        self.df['stsell'] = np.where((self.df['%K'] < self.df['%D']), 1, 0)
        self.df['rbuy'] = np.where((self.df.rsi > 50), 1, 0)
        self.df['mbuy'] = np.where((self.df.macd > 0), 1, 0)
        self.df['msell'] = np.where((self.df.macd < 0), 1, 0)
        self.df['rsell'] = np.where((self.df.rsi < 50), 1, 0)

# inst = Signals(df, 2)
# inst.decide()
# print(df)

def strategy(pair):
    applytechnicals(df)
    inst = Signals(df, 5)
    inst.decide()
    print(df)
    if df.Buy.iloc[-1]:
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_options.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_options.txt', 'w')
        file.close()
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_options.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_options.txt', 'w')
        file.close()
        ##########################################################################################################
        if pair not in clean_buy_list:
            body = "BUY -" + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1])
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
        with open(file_path+ pair +'_buy_options.txt', 'a+') as f:
            f.write(str(pair) + '\n')

    elif df.Sell.iloc[-1]:
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_options.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_options.txt', 'w')
        file.close()
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_options.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_options.txt', 'w')
        file.close()
        ###########################################################################################################
        if pair not in clean_sell_list:
            body = "SELL -" + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1])
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
        with open(file_path+ pair +'_sell_options.txt', 'a+') as f:
            f.write(str(pair) + '\n')
while True:
    crypto_coins = ["AUDCHF=X"]
    for coins in crypto_coins:
        # try:
        df = getminutedata(coins)
        myfile1 = Path(file_path+ coins +'_buy_options.txt')
        myfile2 = Path(file_path+ coins +'_sell_options.txt')
        myfile1.touch(exist_ok=True)
        myfile2.touch(exist_ok=True)
        strategy(coins)
        time.sleep(5)
        # except Exception:
        #    pass