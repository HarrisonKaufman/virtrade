import os
import requests
import finnhub
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
NEWS_API_BASE_URL = 'https://newsapi.org/v2'

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


# daily candles for 1M/3M view
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

# hourly candles for 1D/1W view
def get_twelve_data_intraday(symbol, interval='1h', outputsize=168):
    url = f'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': TWELVE_DATA_API_KEY
    }
    r = requests.get(url, params=params)
    return r.json()
#this gets 3 most recent news stories for a given stock symbol
def get_news_for_symbol(symbol):
    url = f'{NEWS_API_BASE_URL}/everything'
    params = {
        'q': symbol,
        'sortBy': 'publishedAt',
        'pageSize': 10,  # Get more to filter for English
        'apiKey': NEWS_API_KEY,
        'language': 'en'
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        
        # Filter for English articles and limit to 3
        if data.get('articles'):
            articles = [a for a in data.get('articles', []) if a.get('description') and a.get('title')]
            data['articles'] = articles[:3]
        
        if not data.get('articles'):
            return {'error': 'No articles found', 'status': data.get('status')}
        return data
    except requests.exceptions.RequestException as e:
        return {'error': str(e), 'status_code': r.status_code if 'r' in locals() else None}
    
def get_finnhub_news(symbol, days_back=3):
    import time

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

            # Filter: symbol or company name must appear in headline or summary
            combined = (headline + " " + summary).lower()
            if symbol_lower not in combined:
                continue  # skip irrelevant articles

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
        import traceback
        print(f"[ERROR] get_finnhub_news failed for {symbol}: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}
