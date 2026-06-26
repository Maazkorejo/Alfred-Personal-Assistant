import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = os.environ.get('DATABASE_URL')
        if '?' in db_url:
            db_url += '&connect_timeout=10'
        else:
            db_url += '?connect_timeout=10'
        _engine = create_engine(db_url, pool_size=3, max_overflow=5, pool_pre_ping=True)
    return _engine


def add_event(title: str, start_datetime: str, end_datetime: str = None, description: str = None) -> dict:
    """Add a new calendar event. start_datetime must be ISO format string e.g. 2025-01-15 14:00"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(
                text('''
                    INSERT INTO alfred_calendar (title, description, start_datetime, end_datetime)
                    VALUES (:title, :description, :start_datetime, :end_datetime)
                '''),
                {
                    'title': title,
                    'description': description,
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime,
                }
            )
            conn.commit()
        return {'success': True, 'message': f'Event "{title}" added for {start_datetime}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_today_events() -> list[dict]:
    """Get all events scheduled for today."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('''
                    SELECT id, title, description, start_datetime, end_datetime
                    FROM alfred_calendar
                    WHERE DATE(start_datetime AT TIME ZONE 'Asia/Karachi') = (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Karachi')::date
                    ORDER BY start_datetime ASC
                ''')
            )
            rows = result.fetchall()
            return [
                {
                    'id': str(r[0]),
                    'title': r[1],
                    'description': r[2],
                    'start_datetime': str(r[3]),
                    'end_datetime': str(r[4]) if r[4] else None,
                }
                for r in rows
            ]
    except Exception as e:
        return [{'error': str(e)}]


def get_upcoming_events(days: int = 7) -> list[dict]:
    """Get events in the next N days."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text(f'''
                    SELECT id, title, description, start_datetime, end_datetime
                    FROM alfred_calendar
                    WHERE start_datetime >= NOW()
                    AND start_datetime <= NOW() + INTERVAL '{int(days)} days'
                    ORDER BY start_datetime ASC
                    LIMIT 20
                ''')
            )
            rows = result.fetchall()
            return [
                {
                    'id': str(r[0]),
                    'title': r[1],
                    'description': r[2],
                    'start_datetime': str(r[3]),
                    'end_datetime': str(r[4]) if r[4] else None,
                }
                for r in rows
            ]
    except Exception as e:
        return [{'error': str(e)}]


def get_all_events() -> list[dict]:
    """Get all upcoming events for the calendar panel."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('''
                    SELECT id, title, description, start_datetime, end_datetime
                    FROM alfred_calendar
                    WHERE start_datetime >= NOW() - INTERVAL '1 day'
                    ORDER BY start_datetime ASC
                    LIMIT 50
                ''')
            )
            rows = result.fetchall()
            return [
                {
                    'id': str(r[0]),
                    'title': r[1],
                    'description': r[2],
                    'start_datetime': str(r[3]),
                    'end_datetime': str(r[4]) if r[4] else None,
                }
                for r in rows
            ]
    except Exception as e:
        return [{'error': str(e)}]


def delete_event(event_id: str) -> dict:
    """Delete a calendar event by ID."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('DELETE FROM alfred_calendar WHERE id = :id'),
                {'id': event_id}
            )
            conn.commit()
            if result.rowcount == 0:
                return {'success': False, 'error': 'Event not found'}
        return {'success': True, 'message': 'Event deleted'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def search_events(keyword: str) -> list[dict]:
    """Search events by title or description keyword."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('''
                    SELECT id, title, description, start_datetime, end_datetime
                    FROM alfred_calendar
                    WHERE title ILIKE :kw OR description ILIKE :kw
                    ORDER BY start_datetime ASC
                    LIMIT 10
                '''),
                {'kw': f'%{keyword}%'}
            )
            rows = result.fetchall()
            return [
                {
                    'id': str(r[0]),
                    'title': r[1],
                    'description': r[2],
                    'start_datetime': str(r[3]),
                    'end_datetime': str(r[4]) if r[4] else None,
                }
                for r in rows
            ]
    except Exception as e:
        return [{'error': str(e)}]