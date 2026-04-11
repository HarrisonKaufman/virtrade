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

TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')

#this is live pricing and OHLCV for current day
def get_finnhub_quote(symbol):
    return finnhub_client.quote(symbol)

#this is historical OHLCV data for a symbol
def get_alpha_vantage_daily(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    return data

# week of candles from finnhub, since AV is heavily rate limited
def get_finnhub_candle_data(symbol):
    import requests, time

    now = int(time.time())
    week_ago = now - 7 * 24 * 60 * 60  # 7 days

    url = f"https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": "60",
        "from": week_ago,
        "to": now,
        "token": FINNHUB_API_KEY
    }

    return requests.get(url, params=params).json()


def get_twelve_data_daily(symbol, outputsize=90):
    url = f'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': TWELVE_DATA_API_KEY
    }
    r = requests.get(url, params=params)
    return r.json()