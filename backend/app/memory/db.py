import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_engine():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DATABASE_URL environment variable is not set')
    return create_engine(db_url)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
