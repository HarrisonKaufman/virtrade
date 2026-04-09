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

#this is live pricing and OHLCV for current day
def get_finnhub_quote(symbol):
    return finnhub_client.quote(symbol)

#this is historical OHLCV data for a symbol
def get_alpha_vantage_daily(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    return data

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