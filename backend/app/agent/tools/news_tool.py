import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
BASE_URL = 'https://newsapi.org/v2'


def get_top_headlines(country='us', category=None, limit=5):
    """Fetch top headlines, optionally filtered by category."""
    try:
        params = {
            'apiKey': NEWS_API_KEY,
            'country': country,
            'pageSize': limit,
        }
        if category:
            params['category'] = category

        res = requests.get(f'{BASE_URL}/top-headlines', params=params, timeout=10)
        data = res.json()

        if data.get('status') != 'ok':
            return [{'error': data.get('message', 'Unknown error fetching news')}]

        articles = data.get('articles', [])
        return [
            {
                'title': a.get('title', ''),
                'source': a.get('source', {}).get('name', ''),
                'description': a.get('description', ''),
                'url': a.get('url', ''),
                'published_at': a.get('publishedAt', ''),
            }
            for a in articles
        ]

    except Exception as e:
        return [{'error': str(e)}]


def search_news(query, limit=5):
    """Search news worldwide by keyword."""
    try:
        params = {
            'apiKey': NEWS_API_KEY,
            'q': query,
            'pageSize': limit,
            'sortBy': 'publishedAt',
            'language': 'en',
        }

        res = requests.get(f'{BASE_URL}/everything', params=params, timeout=10)
        data = res.json()

        if data.get('status') != 'ok':
            return [{'error': data.get('message', 'Unknown error searching news')}]

        articles = data.get('articles', [])
        return [
            {
                'title': a.get('title', ''),
                'source': a.get('source', {}).get('name', ''),
                'description': a.get('description', ''),
                'url': a.get('url', ''),
                'published_at': a.get('publishedAt', ''),
            }
            for a in articles
        ]

    except Exception as e:
        return [{'error': str(e)}]