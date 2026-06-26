from datetime import datetime, timedelta
import re
from app.memory.db import get_engine
from sqlalchemy import text


def create_reminder(title: str, due_at: datetime) -> dict:
    """Create a new reminder."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('INSERT INTO reminders (title, due_at) VALUES (:title, :due_at) RETURNING id'),
                {'title': title, 'due_at': due_at}
            )
            conn.commit()
            reminder_id = result.fetchone()[0]
        return {'success': True, 'id': reminder_id, 'title': title, 'due_at': due_at.isoformat()}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def list_reminders(include_completed: bool = False) -> list[dict]:
    """List all reminders, optionally including completed ones."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = 'SELECT id, title, due_at, completed FROM reminders'
            if not include_completed:
                query += ' WHERE completed = FALSE'
            query += ' ORDER BY due_at ASC'
            result = conn.execute(text(query))
            rows = result.fetchall()
            return [
                {'id': r[0], 'title': r[1], 'due_at': str(r[2]), 'completed': r[3]}
                for r in rows
            ]
    except Exception as e:
        return [{'error': str(e)}]


def get_all_reminders() -> list[dict]:
    """Get all reminders including completed ones for the panel."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('''
                    SELECT id, title, due_at, completed, notified
                    FROM reminders
                    ORDER BY due_at DESC
                    LIMIT 50
                ''')
            )
            rows = result.fetchall()
            return [
                {
                    'id': r[0],
                    'title': r[1],
                    'due_at': str(r[2]),
                    'completed': r[3],
                    'notified': r[4],
                }
                for r in rows
            ]
    except Exception as e:
        return [{'error': str(e)}]


def complete_reminder(reminder_id: int) -> dict:
    """Mark a reminder as completed."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(
                text('UPDATE reminders SET completed = TRUE WHERE id = :id'),
                {'id': reminder_id}
            )
            conn.commit()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def delete_reminder(reminder_id: int) -> dict:
    """Delete a reminder permanently."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM reminders WHERE id = :id'), {'id': reminder_id})
            conn.commit()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_due_reminders() -> list[dict]:
    """Get reminders that are due now and haven't been notified yet."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text('''
                    SELECT id, title, due_at FROM reminders
                    WHERE completed = FALSE AND notified = FALSE AND due_at <= NOW()
                ''')
            )
            rows = result.fetchall()
            return [{'id': r[0], 'title': r[1], 'due_at': str(r[2])} for r in rows]
    except Exception as e:
        return [{'error': str(e)}]


def mark_notified(reminder_id: int):
    """Mark a reminder as having been notified."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(
                text('UPDATE reminders SET notified = TRUE WHERE id = :id'),
                {'id': reminder_id}
            )
            conn.commit()
    except Exception:
        pass


def parse_relative_time(text_input: str) -> datetime:
    """
    Parse simple relative time expressions like 'in 30 minutes', 'in 2 hours'.
    Returns None if it can't parse — caller should fall back to LLM-provided ISO timestamp.
    """
    text_input = text_input.lower().strip()
    now = datetime.now()
    match = re.search(r'in (\d+) (minute|minutes|hour|hours|min|mins)', text_input)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if 'hour' in unit:
            return now + timedelta(hours=amount)
        else:
            return now + timedelta(minutes=amount)
    return None