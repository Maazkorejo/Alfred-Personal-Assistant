"""
Alfred System Tray Icon
Right-click the tray icon to open Alfred or exit.
"""

import pystray
from PIL import Image, ImageDraw
import threading
import webbrowser
import subprocess
import os
import requests
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
ALFRED_URL = "http://localhost:5173"
ALFRED_BACKEND_URL = "http://localhost:5000/api/health"


def create_icon():
    """Create a simple gold batman-style circle icon."""
    img = Image.new('RGB', (64, 64), color=(5, 5, 7))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=(232, 213, 163))
    draw.ellipse([18, 18, 46, 46], fill=(5, 5, 7))
    draw.ellipse([24, 24, 40, 40], fill=(232, 213, 163))
    return img


def is_backend_running() -> bool:
    try:
        requests.get(ALFRED_BACKEND_URL, timeout=2)
        return True
    except:
        return False


def is_frontend_running() -> bool:
    try:
        requests.get(ALFRED_URL, timeout=2)
        return True
    except:
        return False


def launch_alfred():
    if not is_backend_running():
        subprocess.Popen(
            f'start "Alfred Backend" cmd /k "{VENV_PYTHON} {os.path.join(BASE_DIR, "run.py")}"',
            shell=True
        )
        time.sleep(6)

    if not is_frontend_running():
        subprocess.Popen(
            f'start "Alfred Frontend" cmd /k "cd /d {FRONTEND_DIR} && npm run dev"',
            shell=True
        )
        time.sleep(5)

    webbrowser.open(ALFRED_URL)


def on_open(icon, item):
    threading.Thread(target=launch_alfred, daemon=True).start()


def on_exit(icon, item):
    icon.stop()


def main():
    icon = pystray.Icon(
        name='Alfred',
        icon=create_icon(),
        title='Alfred — AI Assistant',
        menu=pystray.Menu(
            pystray.MenuItem('Open Alfred', on_open, default=True),
            pystray.MenuItem('Exit', on_exit),
        )
    )
    icon.run()


if __name__ == '__main__':
    main()