import os
import requests
import finnhub
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

#this is live pricing and OHLCV for current day
def get_finnhub_quote(symbol):
    return finnhub_client.quote(symbol)

#this is historical OHLCV data for a symbol
def get_alpha_vantage_daily(symbol):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    return data