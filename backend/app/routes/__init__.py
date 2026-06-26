from .health import health_bp
from .chat import chat_bp
from .emails import emails_bp
from .memory import memory_bp
from .tts import tts_bp
from .calendar import calendar_bp
from .reminders import reminders_bp
from .spotify import spotify_bp

__all__ = ['health_bp', 'chat_bp', 'emails_bp', 'memory_bp', 'tts_bp', 'calendar_bp', 'reminders_bp', 'spotify_bp']