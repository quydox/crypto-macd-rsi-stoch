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

client = Client(api_key, api_secret)
exchange_info = client.get_exchange_info()
for s in exchange_info['symbols']:
    print(s['symbol'])
