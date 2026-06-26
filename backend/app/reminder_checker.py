import threading
import time
import requests
from plyer import notification
from app.agent.tools.reminder_tool import get_due_reminders, mark_notified

CHECK_INTERVAL = 60  # seconds


def _speak_reminder(title: str):
    """Send reminder text to Alfred's TTS endpoint."""
    try:
        requests.post(
            'http://localhost:5000/api/tts/generate',
            json={'text': f"Reminder, sir: {title}"},
            timeout=10
        )
    except Exception as e:
        print(f'[REMINDER] TTS error: {e}')


def _notify(title: str):
    """Fire a Windows toast notification."""
    try:
        notification.notify(
            title='Alfred Reminder',
            message=title,
            app_name='Alfred',
            timeout=10,
        )
    except Exception as e:
        print(f'[REMINDER] Notification error: {e}')


def _checker_loop():
    """Background loop that checks for due reminders every 60 seconds."""
    print('[REMINDER] Background checker started')
    while True:
        try:
            due = get_due_reminders()
            for reminder in due:
                print(f"[REMINDER] Due: {reminder['title']}")
                _notify(reminder['title'])
                _speak_reminder(reminder['title'])
                mark_notified(reminder['id'])
        except Exception as e:
            print(f'[REMINDER] Checker error: {e}')
        time.sleep(CHECK_INTERVAL)


def start_reminder_checker():
    """Start the background reminder checker thread. Call once at app startup."""
    thread = threading.Thread(target=_checker_loop, daemon=True)
    thread.start()