from dotenv import load_dotenv
load_dotenv()
import os
import requests
api_telegram = os.getenv("api_telegram")
body = "Test Upgrade"
base_url = 'https://api.telegram.org/bot' + str(api_telegram) + '/sendMessage?chat_id=-584537790&text="{}"'.format(body)
requests.get(base_url)
