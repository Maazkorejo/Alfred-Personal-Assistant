import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
BASE_URL = 'https://api.openweathermap.org/data/2.5'


def get_weather(city='Jamshoro'):
    """Fetch current weather for a city."""
    try:
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
        }

        res = requests.get(f'{BASE_URL}/weather', params=params, timeout=10)
        data = res.json()

        if data.get('cod') != 200:
            return {'error': data.get('message', 'Could not fetch weather')}

        return {
            'city': data.get('name', city),
            'country': data.get('sys', {}).get('country', ''),
            'temp': round(data.get('main', {}).get('temp', 0)),
            'feels_like': round(data.get('main', {}).get('feels_like', 0)),
            'condition': data.get('weather', [{}])[0].get('description', ''),
            'humidity': data.get('main', {}).get('humidity', 0),
            'wind_speed': data.get('wind', {}).get('speed', 0),
        }

    except Exception as e:
        return {'error': str(e)}