try:
    from dotenv import load_dotenv
    load_dotenv()
    from pathlib import Path
    import requests
    import pandas as pd
    import numpy as np
    from math import floor
    import datetime
    import time
    import os
    import yfinance as yf
    print("All modules are loaded ")

except Exception as e:
    print("Some Modules are Missing :{} ".format(e))

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
api_telegram1 = os.getenv("api_telegram1")
msg_id_telegram1 = os.getenv("msg_id_telegram1")
file_path_stock = os.getenv("file_path_stock")

class Settings(object):

    def __init__(self, setting):
        self.setting = setting


class StockReader(object):

    def __init__(self, instance):
        self.instance  = instance

    def get_df(self):

        data = yf.download(
            tickers     =  self.instance.setting.get("stock").get("ticker"),
            period      =  self.instance.setting.get("stock").get("period"),
            interval    =  self.instance.setting.get("stock").get("interval"),
            auto_adjust =  True,
            prepost=True,
            threads=True
        )
        return data


class MACD(object):

    def __init__(self, df, instance):
        self.df = df
        self.instance  = instance

    def get_macd(self):

        exp1 = self.df.Close.ewm(span=self.instance.setting.get("algorithm").get("slow_ma"), adjust=False).mean()
        exp2 =  self.df.Close.ewm(span=self.instance.setting.get("algorithm").get("fast_ma"), adjust=False).mean()
        self.df["macd"] = exp1-exp2
        self.df["signal"] = self.df.macd.ewm(span=self.instance.setting.get("algorithm").get("smooth"), adjust=False).mean()
        self.df["hist"] = self.df["macd"] - self.df["signal"]

        return self.df


class GenerateTradeSignal(object):

    def __init__(self, df=None):
        self.df = df

    def get_signals(self):

        prices = self.df.Close
        buy_price = []
        sell_price = []
        macd_signal = []

        signal = 0

        for i in range(len(self.df)):

            if self.df['macd'][i] > self.df['signal'][i]:
                if signal != 1:
                    buy_price.append(prices[i])
                    sell_price.append(np.nan)
                    signal = 1
                    macd_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)

            elif self.df['macd'][i] < self.df['signal'][i]:
                if signal != -1:
                    buy_price.append(np.nan)
                    sell_price.append(prices[i])
                    signal = -1
                    macd_signal.append(signal)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)

            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)

        self.df["buy_price"] = buy_price
        self.df["sell_price"] = sell_price
        self.df["macd_signal"] = macd_signal

        return self.df


class Controller(object):

    def __init__(self, commands):
        self.commands = commands

    def get(self):

        """Step 1 load the data """
        settings = Settings(setting=self.commands)

        """step 2:get the data"""
        helper = StockReader(instance=settings)
        df = helper.get_df()

        """step 3:  get the macd """
        macd_helper = MACD(instance=settings, df=df)
        df = macd_helper.get_macd()

        signal_helper = GenerateTradeSignal(df=df)
        df = signal_helper.get_signals()

        df.to_csv("final.csv")
        
        #########Get Last ROW and LAST Column#######
        get_last_row = df.tail(1)
        get_last_column = get_last_row.macd_signal[0]
        #get_last_column = 0

        ###################SELL PRICE###############
        get_sell_price = get_last_row.sell_price[0]
    
        ###################BUY PRICE################
        get_buy_price = get_last_row.buy_price[0]

        print(stock)
        if get_last_column == 1:
            #####################Read the previous buy text output and empty the file ################################
            with open(file_path_stock+ stock +'_buy.txt', 'r') as f:
                clean_buy_list = []
                for buy_list in f.readlines():
                    clean_buy_list.append(buy_list.replace("\n", ""))
            file = open(file_path_stock+ stock +'_buy.txt', 'w')
            file.close()      
            ###########################################################################################################
            #####################Read the previous sell text output and empty the file ###############################
            with open(file_path_stock+ stock +'_sell.txt', 'r') as f:
                clean_sell_list = []
                for sell_list in f.readlines():
                    clean_sell_list.append(sell_list.replace("\n", ""))
            file = open(file_path_stock+ stock +'_sell.txt', 'w')
            file.close()      
            ##########################################################################################################                 
            if stock not in clean_buy_list:
                body = stock,"BUY",get_buy_price
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                requests.get(base_url)
            with open(file_path_stock+ stock +'_buy.txt', 'a+') as f:
                f.write(str(stock) + '\n')

        elif get_last_column == -1:
            #####################Read the previous sell text output and empty the file ###############################
            with open(file_path_stock+ stock +'_sell.txt', 'r') as f:
                clean_sell_list = []
                for sell_list in f.readlines():
                    clean_sell_list.append(sell_list.replace("\n", ""))
            file = open(file_path_stock+ stock +'_sell.txt', 'w')
            file.close()      
            ##########################################################################################################
            #####################Read the previous buy text output and empty the file ################################
            with open(file_path_stock+ stock +'_buy.txt', 'r') as f:
                clean_buy_list = []
                for buy_list in f.readlines():
                    clean_buy_list.append(buy_list.replace("\n", ""))
            file = open(file_path_stock+ stock +'_buy.txt', 'w')
            file.close()      
            ##########################################################################################################
            if stock not in clean_sell_list:
                body = stock,"SELL",get_sell_price
                base_url = 'https://api.telegram.org/bot' + str(api_telegram1) + '/sendMessage?chat_id=' + str(msg_id_telegram1)+ '&text="{}"'.format(body)
                requests.get(base_url)
            with open(file_path_stock+ stock +'_sell.txt', 'a+') as f:
                f.write(str(stock) + '\n')
#df = pd.read_csv(file_path_stock+'etoro_stock.csv')
monitor_stock = ["TSLA"]
# for stock in df['Symbol']:
for stock in monitor_stock:
    # try:  
    def main():
        # ####################Create an empty the file if does not exist #########################################
        # myfile1 = Path(file_path_stock+ stock +'_buy.txt')
        # myfile2 = Path(file_path_stock+ stock +'_sell.txt')
        # myfile1.touch(exist_ok=True)
        # myfile2.touch(exist_ok=True)
        # #########################################################################################################
        commands = {
            "stock":{
                "ticker":stock,
                'interval':"1wk",
                'period':"ytd"
            },
            "algorithm":{
                "slow_ma":21,
                "fast_ma":8,
                "smooth":5
            }
        }
        helper = Controller(commands=commands)
        response  = helper.get()

    if __name__ == "__main__":
        main()
    # except Exception:
        # pass