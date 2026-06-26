import os
from sqlalchemy import create_engine, text, event
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise RuntimeError('DATABASE_URL is not set')

        # Add connect_timeout to the connection string
        if '?' in db_url:
            db_url += '&connect_timeout=10'
        else:
            db_url += '?connect_timeout=10'

        _engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        _warm_pool()
    return _engine


def _warm_pool():
    """Open one connection at startup to pay the latency cost before first request."""
    try:
        with _engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('[DB] Connection pool warmed up')
    except Exception as e:
        print(f'[DB] Pool warmup failed (non-fatal): {e}')


def save_message(role: str, content: str, session_id: str = None):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text(
                'INSERT INTO conversation_history (role, content, session_id) VALUES (:role, :content, :session_id)'
            ),
            {'role': role, 'content': content, 'session_id': session_id}
        )
        conn.commit()


def get_recent_history(limit: int = 10, session_id: str = None) -> list[dict]:
    engine = get_engine()
    with engine.connect() as conn:
        if session_id:
            result = conn.execute(
                text(
                    'SELECT role, content FROM conversation_history WHERE session_id = :session_id ORDER BY created_at DESC LIMIT :limit'
                ),
                {'limit': limit, 'session_id': session_id}
            )
        else:
            result = conn.execute(
                text(
                    'SELECT role, content FROM conversation_history WHERE session_id IS NULL ORDER BY created_at DESC LIMIT :limit'
                ),
                {'limit': limit}
            )
        rows = result.fetchall()
        return [{'role': r[0], 'content': r[1]} for r in reversed(rows)]


def get_all_history(limit: int = 100) -> list[dict]:
    """Fetch full conversation history for the Memory panel."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                'SELECT role, content, created_at FROM conversation_history ORDER BY created_at DESC LIMIT :limit'
            ),
            {'limit': limit}
        )
        rows = result.fetchall()
        return [
            {'role': r[0], 'content': r[1], 'created_at': str(r[2])}
            for r in rows
        ]


def get_memory_stats() -> dict:
    """Get summary stats about stored memory."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*), MIN(created_at) FROM conversation_history'))
        row = result.fetchone()
        return {
            'total_messages': row[0] or 0,
            'first_message_at': str(row[1]) if row[1] else None,
        }


def clear_all_history():
    """Delete all conversation history."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM conversation_history'))
        conn.commit()


def get_all_sessions() -> list[dict]:
    """Get a list of distinct chat sessions with their first message and timestamp."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text('''
                SELECT DISTINCT session_id,
                    (SELECT content FROM conversation_history c2
                     WHERE c2.session_id = c1.session_id AND c2.role = 'user'
                     ORDER BY created_at ASC LIMIT 1) as first_message,
                    MIN(created_at) as started_at
                FROM conversation_history c1
                WHERE session_id IS NOT NULL
                GROUP BY session_id
                ORDER BY started_at DESC
                LIMIT 50
            ''')
        )
        rows = result.fetchall()
        return [
            {'session_id': str(r[0]), 'first_message': r[1] or '(empty)', 'started_at': str(r[2])}
            for r in rows
        ]


def get_session_messages(session_id: str) -> list[dict]:
    """Get all messages for a specific session."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text('SELECT role, content, created_at FROM conversation_history WHERE session_id = :session_id ORDER BY created_at ASC'),
            {'session_id': session_id}
        )
        rows = result.fetchall()
        return [{'role': r[0], 'content': r[1], 'created_at': str(r[2])} for r in rows]