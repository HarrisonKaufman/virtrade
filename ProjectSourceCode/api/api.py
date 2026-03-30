import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=NVDA&interval=5min&apikey={api_key}'
r = requests.get(url)
data = r.json()

print(data)