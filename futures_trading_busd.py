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

# df = getminutedata('BTCUSDT', '1h', "7 days ago SGT")
# print(df)

def applytechnicals(df):
    df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14, smooth_window=3)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=6)
    df['macd'] = ta.trend.macd_diff(df.Close, window_slow=21, window_fast=8, window_sign=5)
    df['ema5'] = ta.trend.ema_indicator(df.Close, window=5)
    df['ema8'] = ta.trend.ema_indicator(df.Close, window=8)
    df['ema10'] = ta.trend.ema_indicator(df.Close, window=10)
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
        self.df['uptrend'] = np.where((self.df.trigger) & (self.df.ema5 > self.df.ema10) & (self.df.ema8 > self.df.ema10), 1, 0)
        self.df['downtrend'] = np.where((self.df.trigger) & (self.df.ema5 < self.df.ema10) & (self.df.ema8 < self.df.ema10), 1, 0)
        self.df['Buy'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.ema5 > self.df.ema8) & (self.df.ema5 > self.df.ema10) & (self.df.ema8 > self.df.ema10) & (self.df['rsi'].between(50,56)), 1, 0)
        self.df['Sell'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.ema5 < self.df.ema8) & (self.df.ema5 < self.df.ema10) & (self.df.ema8 < self.df.ema10) & (self.df['rsi'].between(44,50)), 1, 0)
        self.df['TPBUY1'] = np.where((self.df.trigger) & (self.df.ema5 < self.df.ema8) & (self.df.uptrend.iloc[-1]), 1, 0)
        self.df['TPSELL1'] = np.where((self.df.trigger) & (self.df.ema5 > self.df.ema8) & (self.df.downtrend.iloc[-1]), 1, 0)
# inst = Signals(df, 2)
# inst.decide()
# print(df)

def strategy(pair, qty, open_position=False):
    applytechnicals(df)
    inst = Signals(df, 5)
    inst.decide()
    for open_position_check in active_position:
        print(df)
        print(pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "CLOSE PRICE PREV: " + str(df.Close.iloc[-2]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']))
        for check_balance in acc_balance:
            if check_balance['asset'] == "BUSD":
                busd_balance = check_balance["balance"]
                profit_balance = int(float(busd_balance))/50 * 100 - 100
                if df.Buy.iloc[-1] and float(open_position_check['entryPrice']) == 0:
                    order = client.futures_create_order(symbol=pair, side='BUY', type='MARKET', quantity=qty, leverage=2)
                    client.futures_create_order(symbol=pair, side='SELL', type='STOP_MARKET', stopPrice=stop_loss_market_buy, closePosition='true', timeInForce='GTE_GTC' )
                    #client.futures_create_order(symbol=pair,side='SELL',type='TAKE_PROFIT_MARKET',stopPrice=stop_loss_market_sell, closePosition='true', timeInForce='GTE_GTC')
                    open_position = True
                    body = pair, "\n" + "PROFIT: ", profit_balance, "\n" + "ORDER: ", order,"\n" + "BUY - NEW ENTRY: ", str(df.Close.iloc[-1]), "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice'])
                    base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
                    requests.get(base_url)
                    print(body)
                elif (df.TPBUY1.iloc[-1] and float(open_position_check['entryPrice']) != 0):
                    fees = client.get_trade_fee(symbol=pair)
                    for item in fees:
                        qty_order = qty-(float(item['takerCommission'])*qty)
                        order = client.futures_create_order(symbol=pair, side='SELL', type='MARKET', quantity=qty_order, leverage=2)
                        body = "TAKE PROFIT FROM BUY: " + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']) + "\n" + "TP1: " + str(df.TPBUY1.iloc[-1])
                        base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                        requests.get(base_url)
                        print(body)
                elif df.Sell.iloc[-1] and float(open_position_check['entryPrice']) == 0:
                    fees = client.get_trade_fee(symbol=pair)
                    for item in fees:
                        qty_order = qty-(float(item['takerCommission'])*qty)
                        order = client.futures_create_order(symbol=pair, side='SELL', type='MARKET', quantity=qty_order, leverage=2)
                        client.futures_create_order(symbol=pair, side='BUY', type='STOP_MARKET', stopPrice=stop_loss_market_sell, closePosition='true', timeInForce='GTE_GTC' )
                        #client.futures_create_order(symbol=pair,side='BUY',type='TAKE_PROFIT_MARKET',stopPrice=stop_loss_market_buy, closePosition='true', timeInForce='GTE_GTC')
                        body = pair, "\n" + "PROFIT: ", profit_balance, "\n" + "ORDER: ", order,"\n" + "SELL - NEW ENTRY: ", str(df.Close.iloc[-1]), "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice'])
                        base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                        requests.get(base_url)
                        print(body)
                elif (df.TPSELL1.iloc[-1] and float(open_position_check['entryPrice']) != 0):
                    order = client.futures_create_order(symbol=pair, side='BUY', type='MARKET', quantity=qty, leverage=2)
                    open_position = True
                    body = "TAKE PROFIT FROM SELL: " + pair + "\n" + "CLOSE PRICE: " + str(df.Close.iloc[-1]) + "\n" + "ENTRY PRICE: " + str(open_position_check['entryPrice']) + "\n" + "TP1: " + str(df.TPSELL1.iloc[-1])
                    base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
                    requests.get(base_url)
                    print(body)
while True:
    crypto_coins = ["BTCBUSD"]
    for coins in crypto_coins:
        # try:
        df = getminutedata(coins, '1m', "1 day ago SGT")
        acc_balance = client.futures_account_balance()
        active_position = client.futures_position_information(symbol=coins)
        current_price = client.get_symbol_ticker(symbol=coins)
        stop_loss_market_buy = int(float(current_price['price']) * 0.998)
        stop_loss_market_sell = int(float(current_price['price']) * 1.002)
        total_coins = round(float(50/(float(current_price['price']))),3)
        strategy(coins, total_coins)
        time.sleep(5)
        # except Exception as e:
            # body = "An error occurred while calling the Binance API: {}".format(e)
            # base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1) + '&text="{}"'.format(body)
            # requests.get(base_url)