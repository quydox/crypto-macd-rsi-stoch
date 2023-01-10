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
    frame = pd.DataFrame(yf.download(symbol, interval = "1h", period = "60d"))
    frame = frame.iloc[:,:6]
    frame.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    frame = frame.astype(float)
    return frame
# df = getminutedata("TSLA")
#print(df)

def applytechnicals(df):
    df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close, window_slow=26, window_fast=12, window_sign=9)
    df['ema50'] = ta.trend.ema_indicator(df.Close, window=50)
    df['ema100'] = ta.trend.ema_indicator(df.Close, window=100)
    df['ema150'] = ta.trend.ema_indicator(df.Close, window=150)
    df.dropna(inplace=True)

# applytechnicals(df)
# print(df)

class Signals:
    def __init__(self,df, lags):
        self.df = df
        self.lags = lags

    def gettrigger(self):
        dfx = pd.DataFrame()
        for i in range(self.lags +1):
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
            dfx = pd.concat([mask], ignore_index=True)
        return dfx.sum(axis=0)

    def decide(self):
        self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
        self.df['Buy'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.ema50 > self.df.ema100) & (self.df.ema50 > self.df.ema150) & (self.df.ema100 > self.df.ema150) & (self.df.macd > 0) & (self.df.rsi > 50), 1, 0)
        self.df['Sell'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.ema50 < self.df.ema100) & (self.df.ema50 < self.df.ema150) & (self.df.ema100 < self.df.ema150) & (self.df.macd < 0) & (self.df.rsi < 50), 1, 0)
        self.df['Stochastic'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)), 1, 0)
        self.df['rsiBUY'] = np.where((self.df.trigger) & (self.df.rsi > 50), 1, 0)
        self.df['macdBUY'] = np.where((self.df.trigger) & (self.df.macd > 0), 1, 0)
        self.df['emaBUY1'] = np.where((self.df.trigger) & (self.df.ema50 > self.df.ema150), 1, 0)
        self.df['emaBUY2'] = np.where((self.df.trigger) & (self.df.ema100 > self.df.ema150), 1, 0)
        self.df['macdSELL'] = np.where((self.df.trigger) & (self.df.macd < 0), 1, 0)
        self.df['rsiSELL'] = np.where((self.df.trigger) & (self.df.rsi < 50), 1, 0)
        self.df['emaSELL1'] = np.where((self.df.trigger) & (self.df.ema50 < self.df.ema150), 1, 0)
        self.df['emaSELL2'] = np.where((self.df.trigger) & (self.df.ema100 < self.df.ema150), 1, 0)
        self.df['stochBUY'] = np.where((self.df.trigger) & (self.df['%K'] > self.df['%D']), 1, 0)
        self.df['stochSELL'] = np.where((self.df.trigger) & (self.df['%K'] < self.df['%D']), 1, 0)
        self.df['TPBUY1'] = np.where((self.df.trigger) & (self.df.ema50 < self.df.ema100) & (self.df.rsi < 50), 1, 0)
        self.df['TPSELL1'] = np.where((self.df.trigger) & (self.df.ema50 > self.df.ema100) & (self.df.rsi > 50), 1, 0)
        self.df['TPBUY2'] = np.where((self.df.trigger) & (self.df.rsi > 70) & (self.df['%K'] < self.df['%D']), 1, 0)
        self.df['TPSELL2'] = np.where((self.df.trigger) & (self.df.rsi < 30) & (self.df['%K'] > self.df['%D']), 1, 0)
        self.df['TPBUY3'] = np.where((self.df.trigger) & (self.df.macd < 0) & (self.df.ema50 < self.df.ema100), 1, 0)
        self.df['TPSELL3'] = np.where((self.df.trigger) & (self.df.macd > 0) & (self.df.ema50 > self.df.ema100), 1, 0)
        self.df['uptrend'] = np.where((self.df.trigger) & (self.df.ema50 > self.df.ema150) & (self.df.ema100 > self.df.ema150), 1, 0)
        self.df['downtrend'] = np.where((self.df.trigger) & (self.df.ema50 < self.df.ema150) & (self.df.ema100 < self.df.ema150), 1, 0)


# inst = Signals(df, 2)
# inst.decide()
# print(df)

def strategy(pair):
    applytechnicals(df)
    inst = Signals(df, 5)
    inst.decide()
    print(df)
    if df.Buy.iloc[-1] & df.uptrend.iloc[-1]:
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_indices.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_indices.txt', 'w')
        file.close()
        ###########################################################################################################
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_indices.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_indices.txt', 'w')
        file.close()
        ##########################################################################################################
        if pair not in clean_buy_list:
            body = "BUY -" + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']) + "\n" + "MACD: " + str(df.macd.iloc[-1]) + "\n" + "RSI: " + str(df.rsi.iloc[-1]) + "\n" + "EMA7: " + str(df.ema7.iloc[-1]) + "\n" + "EMA25: " + str(df.ema25.iloc[-1])
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
        with open(file_path+ pair +'_buy_indices.txt', 'a+') as f:
            f.write(str(pair) + '\n')
    elif df.TPSELL2.iloc[-1] or ((df.TPSELL1.iloc[-1] or df.TPSELL3.iloc[-1])):
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_indices.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_indices.txt', 'w')
        file.close()
        if pair in clean_sell_list:
            body = "BUY - TAKE PROFIT FROM SELL" + pair + "\n" + profit_balance + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']) + "\n" + "MACD: " + str(df.macd.iloc[-1]) + "\n" + "RSI: " + str(df.rsi.iloc[-1]) + "\n" + "EMA7: " + str(df.ema7.iloc[-1]) + "\n" + "EMA25: " + str(df.ema25.iloc[-1] + "\n" + order)
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
    elif df.Sell.iloc[-1] & df.downtrend.iloc[-1]:
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_indices.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_indices.txt', 'w')
        file.close()
        ##########################################################################################################
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_indices.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_indices.txt', 'w')
        file.close()
        ###########################################################################################################
        if pair not in clean_sell_list:
            body = pair, "\n" + "PROFIT: ", profit_balance, "\n" + "ORDER: ", order,"\n" + "SELL - CLOSE OR NEW ENTRY: ", str(df.Close.iloc[-1]), "\n" + "EMA: ", str(df.ema7.iloc[-1]), "\n" + " MACD: ", str(df.macd.iloc[-1])
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
        with open(file_path+ pair +'_sell_indices.txt', 'a+') as f:
            f.write(str(pair) + '\n')
    elif df.TPBUY2.iloc[-1] or ((df.TPBUY1.iloc[-1] or df.TPBUY3.iloc[-1])):
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_indices.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_indices.txt', 'w')
        file.close()
        ###########################################################################################################
        if pair in clean_buy_list:
            body = "SELL - TAKE PROFIT FROM BUY" + pair + "\n" + profit_balance + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']) + "\n" + "MACD: " + str(df.macd.iloc[-1]) + "\n" + "RSI: " + str(df.rsi.iloc[-1]) + "\n" + "EMA7: " + str(df.ema7.iloc[-1]) + "\n" + "EMA25: " + str(df.ema25.iloc[-1] + "\n" + order)
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
while True:
    crypto_coins = ["TSLA"]
    for coins in crypto_coins:
        # try:
        df = getminutedata(coins)
        myfile1 = Path(file_path+ coins +'_buy_indices.txt')
        myfile2 = Path(file_path+ coins +'_sell_indices.txt')
        myfile1.touch(exist_ok=True)
        myfile2.touch(exist_ok=True)
        strategy(coins)
        time.sleep(10)
        # except Exception:
        #    pass