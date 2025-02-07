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

def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.futures_historical_klines(symbol, interval, lookback))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

# df = getminutedata('BTCUSDT', '1m', "1 day ago SGT")
# print(df)

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
        self.df['Buy'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.ema50 > self.df.ema100) & (self.df.ema50 > self.df.ema150) & (self.df.ema100 > self.df.ema150) & (self.df['rsi'].between(50,56)), 1, 0)
        self.df['Sell'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.ema50 < self.df.ema100) & (self.df.ema50 < self.df.ema150) & (self.df.ema100 < self.df.ema150) & (self.df['rsi'].between(44,50)), 1, 0)
        self.df['TPBUY1'] = np.where((self.df.trigger) & (self.df.ema50 < self.df.ema100), 1, 0)
        self.df['TPSELL1'] = np.where((self.df.trigger) & (self.df.ema50 > self.df.ema100), 1, 0)
        self.df['TPBUY2'] = np.where((self.df.trigger) & (self.df.rsi > 70), 1, 0)
        self.df['TPSELL2'] = np.where((self.df.trigger) & (self.df.rsi < 30), 1, 0)
        self.df['uptrend'] = np.where((self.df.trigger) & (self.df.ema50 > self.df.ema150) & (self.df.ema100 > self.df.ema150), 1, 0)
        self.df['downtrend'] = np.where((self.df.trigger) & (self.df.ema50 < self.df.ema150) & (self.df.ema100 < self.df.ema150), 1, 0)


# inst = Signals(df, 2)
# inst.decide()
# print(df)

def strategy(pair, open_position=False):
    applytechnicals(df)
    inst = Signals(df, 5)
    inst.decide()
    for open_position_check in active_position:
        print(df)
        print(pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "CLOSE PRICE PREV: " + str(df.Close.iloc[-2]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']) + "\n" + "ema50: " + str(df.ema50.iloc[-1]) + "\n" + "ema100: " + str(df.ema100.iloc[-1]) + "\n" + "ema150: " + str(df.ema150.iloc[-1]))
        if df.Buy.iloc[-1]:
            #####################Read the previous buy text output and empty the file ################################
            with open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'r') as f:
                clean_buy_list = []
                for buy_list in f.readlines():
                    clean_buy_list.append(buy_list.replace("\n", ""))
            file = open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'w')
            file.close()
            #####################Read the previous sell text output and empty the file ###############################
            with open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'r') as f:
                clean_sell_list = []
                for sell_list in f.readlines():
                    clean_sell_list.append(sell_list.replace("\n", ""))
            file = open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'w')
            file.close()
            ##########################################################################################################
            if pair not in clean_buy_list:# and float(open_position_check['entryPrice']) == 0:
                body = "BUY - EMA " + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + "\n" + "ema50: " + str(df.ema50.iloc[-1]) + "\n" + "ema100: " + str(df.ema100.iloc[-1]) + "\n" + "ema150: " + str(df.ema150.iloc[-1])
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
                requests.get(base_url)
                print(body)
            with open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'a+') as f:
                f.write(str(pair) + '\n')
        elif (df.TPBUY1.iloc[-1] or df.TPBUY2.iloc[-1]) & df.uptrend.iloc[-1]:# and float(open_position_check['entryPrice']) != 0):
            #####################Read the previous buy text output and empty the file ################################
            with open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'r') as f:
                clean_buy_list = []
                for buy_list in f.readlines():
                    clean_buy_list.append(buy_list.replace("\n", ""))
            file = open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'w')
            file.close()
            ###########################################################################################################
            if pair in clean_buy_list:# and float(open_position_check['entryPrice']) != 0:
                body = "TAKE PROFIT FROM BUY: " + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + "\n" + "ema50: " + str(df.ema50.iloc[-1]) + "\n" + "ema100: " + str(df.ema100.iloc[-1]) + "\n" + "ema150: " + str(df.ema150.iloc[-1])
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
                requests.get(base_url)
                print(body)
        elif df.Sell.iloc[-1]:
            #####################Read the previous sell text output and empty the file ###############################
            with open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'r') as f:
                clean_sell_list = []
                for sell_list in f.readlines():
                    clean_sell_list.append(sell_list.replace("\n", ""))
            file = open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'w')
            file.close()
            #####################Read the previous buy text output and empty the file ################################
            with open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'r') as f:
                clean_buy_list = []
                for buy_list in f.readlines():
                    clean_buy_list.append(buy_list.replace("\n", ""))
            file = open(file_path+ pair +'_buy_future_ema_alert_minute.txt', 'w')
            file.close()
            ###########################################################################################################
            if pair not in clean_sell_list:# and float(open_position_check['entryPrice']) == 0:
                body = "SELL - EMA " + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + "\n" + "ema50: " + str(df.ema50.iloc[-1]) + "\n" + "ema100: " + str(df.ema100.iloc[-1]) + "\n" + "ema150: " + str(df.ema150.iloc[-1])
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                requests.get(base_url)
                print(body)
            with open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'a+') as f:
                f.write(str(pair) + '\n')
        elif (df.TPSELL1.iloc[-1] or df.TPSELL2.iloc[-1]) & df.downtrend.iloc[-1]: #and float(open_position_check['entryPrice']) != 0):
            #####################Read the previous sell text output and empty the file ###############################
            with open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'r') as f:
                clean_sell_list = []
                for sell_list in f.readlines():
                    clean_sell_list.append(sell_list.replace("\n", ""))
            file = open(file_path+ pair +'_sell_future_ema_alert_minute.txt', 'w')
            file.close()
            ###########################################################################################################
            if pair in clean_sell_list:# and float(open_position_check['entryPrice']) != 0:
                body = "TAKE PROFIT FROM SELL - EMA " + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ema50: " + str(df.ema50.iloc[-1]) + "\n" + "ema100: " + str(df.ema100.iloc[-1]) + "\n" + "ema150: " + str(df.ema150.iloc[-1])
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                requests.get(base_url)
                print(body)
while True:
    crypto_coins = ["BTCUSDT"]
    for coins in crypto_coins:
        # try:
        active_position = client.futures_position_information(symbol=coins)
        df = getminutedata(coins, '1m', "1 day ago SGT")
        myfile1 = Path(file_path+ coins +'_buy_future_ema_alert_minute.txt')
        myfile2 = Path(file_path+ coins +'_sell_future_ema_alert_minute.txt')
        myfile1.touch(exist_ok=True)
        myfile2.touch(exist_ok=True)
        strategy(coins)
        time.sleep(5)
        # except Exception:
        #    pass