from datetime import datetime
import pytz


CITY_TIMEZONES = {
    'jamshoro': 'Asia/Karachi',
    'hyderabad': 'Asia/Karachi',
    'karachi': 'Asia/Karachi',
    'islamabad': 'Asia/Karachi',
    'lahore': 'Asia/Karachi',
    'pakistan': 'Asia/Karachi',
    'new york': 'America/New_York',
    'london': 'Europe/London',
    'tokyo': 'Asia/Tokyo',
    'dubai': 'Asia/Dubai',
    'paris': 'Europe/Paris',
    'los angeles': 'America/Los_Angeles',
    'san francisco': 'America/Los_Angeles',
    'sydney': 'Australia/Sydney',
    'singapore': 'Asia/Singapore',
    'moscow': 'Europe/Moscow',
    'delhi': 'Asia/Kolkata',
    'mumbai': 'Asia/Kolkata',
    'india': 'Asia/Kolkata',
    'beijing': 'Asia/Shanghai',
    'china': 'Asia/Shanghai',
}


def get_current_time(location='Jamshoro'):
    """Get current time for a given city/location."""
    try:
        loc_key = location.lower().strip()
        tz_name = CITY_TIMEZONES.get(loc_key, 'Asia/Karachi')

        tz = pytz.timezone(tz_name)
        utc_now = datetime.now(pytz.utc)
        local_now = utc_now.astimezone(tz)

        return {
            'location': location,
            'time': local_now.strftime('%I:%M %p'),
            'date': local_now.strftime('%A, %B %d, %Y'),
            'timezone': tz_name,
        }
    except Exception as e:
        return {'error': str(e)}