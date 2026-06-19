import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise RuntimeError('DATABASE_URL is not set')
        _engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    return _engine


def save_message(role: str, content: str):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text(
                'INSERT INTO conversation_history (role, content) VALUES (:role, :content)'
            ),
            {'role': role, 'content': content}
        )
        conn.commit()


def get_recent_history(limit: int = 10) -> list[dict]:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                'SELECT role, content FROM conversation_history ORDER BY created_at DESC LIMIT :limit'
            ),
            {'limit': limit}
        )
        rows = result.fetchall()
        return [{'role': r[0], 'content': r[1]} for r in reversed(rows)]