import os
import time
import requests
import finnhub
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

def get_finnhub_quote(symbol):
    return finnhub_client.quote(symbol)

def get_finnhub_candle_data(symbol):
    now = int(time.time())
    week_ago = now - 7 * 24 * 60 * 60
    url = "https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": "60",
        "from": week_ago,
        "to": now,
        "token": FINNHUB_API_KEY
    }
    return requests.get(url, params=params).json()

def get_twelve_data_daily(symbol, outputsize=90):
    url = 'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': TWELVE_DATA_API_KEY
    }
    return requests.get(url, params=params).json()

def get_twelve_data_intraday(symbol, interval='1h', outputsize=168):
    url = 'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': TWELVE_DATA_API_KEY
    }
    return requests.get(url, params=params).json()

def get_finnhub_news(symbol, days_back=3):
    now = int(time.time())
    from_time = now - days_back * 24 * 60 * 60

    try:
        news = finnhub_client.company_news(
            symbol,
            _from=time.strftime('%Y-%m-%d', time.gmtime(from_time)),
            to=time.strftime('%Y-%m-%d', time.gmtime(now))
        )

        cleaned = []
        symbol_lower = symbol.lower()

        for item in news:
            headline = item.get("headline", "")
            summary = item.get("summary", "")
            combined = (headline + " " + summary).lower()
            if symbol_lower not in combined:
                continue
            if headline and item.get("url"):
                cleaned.append({
                    "headline": headline,
                    "summary": summary,
                    "source": item.get("source"),
                    "url": item.get("url"),
                    "image": item.get("image"),
                    "datetime": item.get("datetime")
                })
            if len(cleaned) >= 3:
                break

        return {"articles": cleaned}

    except Exception as e:
        return {"error": str(e)}