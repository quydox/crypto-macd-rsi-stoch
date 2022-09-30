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

#df = getminutedata('BTCUSDT', '4h', "30 day ago UTC")
#print(df)

def applytechnicals(df):
    df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)

#applytechnicals(df)
#print(df)

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
        self.df['Buy'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.rsi > 50) & (self.df.macd > 0), 1, 0)
        self.df['Sell'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.rsi < 50) & (self.df.macd < 0), 1, 0)

#inst = Signals(df, 25)
#inst.decide()
#df[df.Buy == 1 ]
#print(df)

def strategy(pair, qty, open_position=False):
    df = getminutedata(pair, '1m', "1 day ago UTC")
    applytechnicals(df)
    inst = Signals(df, 25)
    inst.decide()
    print(pair + f' Current Close is ' + str(df.Close.iloc[-1]), str(df.macd.iloc[-1]), str(df.rsi.iloc[-1]))
    if df.Buy.iloc[-1]:
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_future.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_future.txt', 'w')
        file.close()
        ###########################################################################################################
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_future.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_future.txt', 'w')
        file.close()
        ##########################################################################################################
        if pair not in clean_buy_list:
            order = client.futures_create_order(symbol=pair,side='BUY',type='MARKET',quantity=qty)
            buyprice = order['fills'][0]['price']
            open_position = True
            body = pair, order, "BUY - 4H timeframe version. Current Price " + str(df.Close.iloc[-1])
            base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
            requests.get(base_url)
            print(body)
        with open(file_path+ pair +'_buy_future.txt', 'a+') as f:
            f.write(str(pair) + '\n')
    elif df.Sell.iloc[-1]:
        #####################Read the previous sell text output and empty the file ###############################
        with open(file_path+ pair +'_sell_future.txt', 'r') as f:
            clean_sell_list = []
            for sell_list in f.readlines():
                clean_sell_list.append(sell_list.replace("\n", ""))
        file = open(file_path+ pair +'_sell_future.txt', 'w')
        file.close()
        ##########################################################################################################
        #####################Read the previous buy text output and empty the file ################################
        with open(file_path+ pair +'_buy_future.txt', 'r') as f:
            clean_buy_list = []
            for buy_list in f.readlines():
                clean_buy_list.append(buy_list.replace("\n", ""))
        file = open(file_path+ pair +'_buy_future.txt', 'w')
        file.close()
        ###########################################################################################################
        if pair not in clean_sell_list:
            fees = client.get_trade_fee(symbol=pair)
            for item in fees:
                qty_order = qty-(float(item['takerCommission'])*qty)
                order = client.futures_create_order(symbol=pair,side='SELL',type='MARKET',quantity=qty_order)
                body = pair, order, "SELL - 1 minute timeframe version. Current Price " + str(df.Close.iloc[-1])
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                requests.get(base_url)
                print(body)
        with open(file_path+ pair +'_sell_future.txt', 'a+') as f:
            f.write(str(pair) + '\n')
while True:
    crypto_coins = ["BTCBUSD"]
    for coins in crypto_coins:
        # try:
        current_price = client.get_symbol_ticker(symbol=coins)
        total_coins = round(float(15/(float(current_price['price']))),8)
        print(total_coins)
        myfile1 = Path(file_path+ coins +'_buy_future.txt')
        myfile2 = Path(file_path+ coins +'_sell_future.txt')
        myfile1.touch(exist_ok=True)
        myfile2.touch(exist_ok=True)
        strategy(coins, 0.00076334)
        time.sleep(5)
        # except Exception:
            # pass