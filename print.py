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

# crypto_coins = client.futures_symbol_ticker()
# for item in crypto_coins:
# #    if (int(float(item['price'])) < 1) and item['symbol'].endswith('BUSD'):
        # print(item)

# open_pos = client.futures_account()['positions']
# for item in open_pos:
    # if item['symbol'] == '1000SHIBBUSD':
        # print(item)

# open_pos1 = client.get_account()['balances']
# for item in open_pos1:
    # if item['asset'] == 'SHIB':
        # print(item)

# open_pos1 = client.get_account()['balances']
# for item in open_pos1:
    # if item['asset'] == 'SHIB':
        # print(item)

# ticker_test = client.get_ticker(symbol='SHIBBUSD')
# print(ticker_test)

# get_asset = client.get_asset_details(asset='SHIB')
# print(get_asset)

# get_orders = client.get_my_trades(symbol='SHIBBUSD')
# for item in get_orders:
    # print(item['isMaker'],item['qty'],item['price'])

# open_pos = client.futures_get_open_orders()
# print(open_pos)
# for item in open_pos:
    # print(item)

# exchange_info = client.get_exchange_info()
# for item in exchange_info:
    # print(item['symbols'])

#acc_balance = client.futures_account_balance()
#for check_balance in acc_balance:
#    if check_balance['asset'] == "BUSD":
#        busd_balance = check_balance["balance"]
#        print(int(float(busd_balance))/168 * 100 - 100)

#active_position = client.futures_account()['positions']
# for item in active_position:
    # if item['symbol'] == "BTCBUSD":
        # print(item)

# active_position = client.futures_position_information(symbol='BTCBUSD')
# for open_position_check in active_position:
#     print(str(open_position_check['entryPrice']))
#     if float(open_position_check['entryPrice']) != 0:
#         print("Entry price not equal zero")
#     if float(open_position_check['entryPrice']) == 0:
#         print("Entry price is equal zero")
    # #if int(float(df.Close.iloc[-1])) > int(float(item['entryPrice'])):
    # if close_price > int(float(open_position_check['entryPrice'])):
    #     print("BUY", str(open_position_check['entryPrice']))
    # elif close_price <= int(float(open_position_check['entryPrice'])) * 0.995:
    #     print("SELL", str(open_position_check['entryPrice']))

# current_price = client.get_symbol_ticker(symbol='BTCBUSD')
# print(int(float(current_price['price']) * 0.995))

# print(int(float(current_price['price']) * 1.005))


# fees = client.get_trade_fee(symbol='BTCBUSD')
# print(fees)

# def getminutedata(symbol, interval, lookback):
#     frame = pd.DataFrame(client.futures_historical_klines(symbol, interval, lookback))
#     frame = frame.iloc[:,:6]
#     frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
#     frame = frame.set_index('Time')
#     frame.index = pd.to_datetime(frame.index, unit='ms')
#     frame = frame.astype(float)
#     return frame

# df = getminutedata('BTCUSDT', '1m', "1 hour ago SGT")
# # print(df)

# def applytechnicals(df):
#     df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14, smooth_window=3)
#     df['%D'] = df['%K'].rolling(3).mean()
#     df['rsi'] = ta.momentum.rsi(df.Close, window=14)
#     df['macd'] = ta.trend.macd_diff(df.Close, window_slow=21, window_fast=8, window_sign=5)
#     df['ema7'] = ta.trend.ema_indicator(df.Close, window=7)
#     df['ema25'] = ta.trend.ema_indicator(df.Close, window=25)
#     df.dropna(inplace=True)

# applytechnicals(df)
# print(df)

# class Signals:
#     def __init__(self,df, lags):
#         self.df = df
#         self.lags = lags

#     def gettrigger(self):
#         dfx = pd.DataFrame()
#         for i in range(self.lags +1):
#             mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
#             dfx = pd.concat([mask], ignore_index=True)
#         return dfx.sum(axis=0)

#     def decide(self):
#         self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
#         self.df['Buy'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.rsi > 50) & (self.df.macd > 0) & (self.df.ema < self.df.Close), 1, 0)
#         self.df['Sell'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)) & (self.df['%D'].between(20,80)) & (self.df.rsi < 50) & (self.df.macd < 0) & (self.df.ema > self.df.Close), 1, 0)
#         self.df['Stochastic'] = np.where((self.df.trigger) & (self.df['%K'].between(20,80)), 1, 0)
#         self.df['rsiBUY'] = np.where((self.df.trigger) & (self.df.rsi > 50), 1, 0)
#         self.df['macdBUY'] = np.where((self.df.trigger) & (self.df.macd > 0), 1, 0)
#         self.df['emaBUY'] = np.where((self.df.trigger) & (self.df.ema < self.df.Close), 1, 0)
#         self.df['macdSELL'] = np.where((self.df.trigger) & (self.df.macd < 0), 1, 0)
#         self.df['rsiSELL'] = np.where((self.df.trigger) & (self.df.rsi < 50), 1, 0)
#         self.df['emaSELL'] = np.where((self.df.trigger) & (self.df.ema > self.df.Close), 1, 0)


# inst = Signals(df, 5)
# inst.decide()
# print(df)
coins="BTCUSDT"
current_price = client.get_symbol_ticker(symbol=coins)
stop_loss_market_buy = int(float(current_price['price']) * 0.995)
print(stop_loss_market_buy)
client.futures_create_order(symbol=coins, side='BUY', type='STOP_MARKET', stopPrice='16939', closePosition='true')