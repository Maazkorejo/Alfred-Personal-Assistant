"""
Alfred Clap-to-Wake Listener
Run this script in the background. It listens for two sharp claps
within ~1.5 seconds and brings Alfred to focus (or opens it).
"""

import sounddevice as sd
import numpy as np
import time
import webbrowser
import win32gui
import win32con

SAMPLE_RATE = 44100
THRESHOLD = 0.35          # Amplitude threshold for a "clap" spike
CLAP_WINDOW = 1.5         # Max seconds between two claps to count as a pattern
COOLDOWN = 3.0            # Seconds to wait after triggering before listening again
ALFRED_URL = "http://localhost:5173"
ALFRED_WINDOW_TITLE = "Alfred"  # Matches part of the browser tab title

last_clap_time = 0
clap_count = 0
last_trigger_time = 0


def find_alfred_window():
    """Find a browser window with 'Alfred' in the title."""
    result = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if ALFRED_WINDOW_TITLE.lower() in title.lower():
                result.append(hwnd)
        return True

    win32gui.EnumWindows(callback, None)
    return result[0] if result else None


def wake_alfred():
    """Focus existing Alfred window, or open a new tab if not found."""
    hwnd = find_alfred_window()
    if hwnd:
        print("[CLAP] Found existing Alfred window — bringing to focus.")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    else:
        print("[CLAP] No existing window found — opening Alfred.")
        webbrowser.open(ALFRED_URL)


def audio_callback(indata, frames, time_info, status):
    global last_clap_time, clap_count, last_trigger_time

    now = time.time()
    volume = np.max(np.abs(indata))
    print(f"Volume: {volume:.3f}", end='\r')

    if now - last_trigger_time < COOLDOWN:
        return

    if volume > THRESHOLD:
        if now - last_clap_time < CLAP_WINDOW:
            clap_count += 1
        else:
            clap_count = 1

        last_clap_time = now

        if clap_count >= 2:
            print("[CLAP] Double clap detected! Waking Alfred...")
            wake_alfred()
            clap_count = 0
            last_trigger_time = now


def main():
    print("=" * 50)
    print("ALFRED CLAP-TO-WAKE LISTENER")
    print("Clap twice quickly to wake Alfred.")
    print("Press Ctrl+C to stop.")
    print("=" * 50)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback,
        blocksize=2048,
    ):
        while True:
            time.sleep(0.1)


if __name__ == '__main__':
    main()