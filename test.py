from dotenv import load_dotenv
load_dotenv()
import os
import requests
from binance.client import Client

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
#api_telegram = os.getenv("api_telegram")
#msg_id_telegram = os.getenv("msg_id_telegram")

#api_telegram = os.getenv("api_telegram")
#body = "4 hour timeframe test"
#base_url = 'https://api.telegram.org/bot' + str(api_telegram) + '/sendMessage?chat_id=-584537790&text="{}"'.format(body)
#requests.get(base_url)

client = Client(api_key, api_secret)
exchange_info = client.get_exchange_info()
for s in exchange_info['symbols']:
    print(s['symbol'])
