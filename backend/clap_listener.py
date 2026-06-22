"""
Alfred Clap-to-Wake Listener (v2 — spectral clap detection)

A real clap is distinguished from speech/coughs by:
1. Extremely fast attack (energy rises from baseline to peak in <5ms)
2. Broadband high-frequency content (energy ratio above ~3kHz is high)
3. Very short total duration (<60ms typically)

Speech and coughs are dominated by low-frequency vocal resonances and
have a slower, more sustained energy envelope — even "sharp" consonants
like "k" or "t" lack the broadband high-frequency burst of a real clap.
"""

import sounddevice as sd
import numpy as np
import time
import webbrowser
import win32gui
import win32con

SAMPLE_RATE = 44100
BLOCK_SIZE = 512  # ~11.6ms per block at 44.1kHz — fine enough to catch a clap's attack
CLAP_WINDOW = 1.5
COOLDOWN = 2.5
ALFRED_URL = "http://localhost:5173"
ALFRED_WINDOW_TITLE = "Alfred"

# Tunable detection parameters
AMPLITUDE_THRESHOLD = 0.25       # Minimum peak volume to even consider
HF_RATIO_THRESHOLD = 0.35        # Min fraction of energy that must be >3kHz
MIN_ONSET_SLOPE = 0.15           # Minimum jump in volume between consecutive blocks (fast attack)

last_clap_time = 0
clap_count = 0
last_trigger_time = 0
prev_volume = 0.0

# Precompute FFT frequency bins for our block size
FREQ_BINS = np.fft.rfftfreq(BLOCK_SIZE, d=1.0 / SAMPLE_RATE)
HF_CUTOFF_INDEX = np.searchsorted(FREQ_BINS, 3000)  # index where freq crosses 3kHz


def find_alfred_window():
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
    hwnd = find_alfred_window()
    if hwnd:
        print("[CLAP] Found existing Alfred window — bringing to focus.")
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"[CLAP] Could not steal focus (Windows restriction): {e}")
    else:
        print("[CLAP] No existing window found — opening Alfred.")
        webbrowser.open(ALFRED_URL)


def is_clap_like(indata, volume):
    """
    Analyze spectral content to determine if this burst is clap-like
    (broadband, high-frequency dominant) vs speech-like (low-frequency dominant).
    """
    samples = indata[:, 0] if indata.ndim > 1 else indata

    # FFT magnitude spectrum
    spectrum = np.abs(np.fft.rfft(samples))
    total_energy = np.sum(spectrum) + 1e-9

    hf_energy = np.sum(spectrum[HF_CUTOFF_INDEX:])
    hf_ratio = hf_energy / total_energy

    return hf_ratio > HF_RATIO_THRESHOLD


def audio_callback(indata, frames, time_info, status):
    global last_clap_time, clap_count, last_trigger_time, prev_volume

    now = time.time()
    volume = float(np.max(np.abs(indata)))

    if now - last_trigger_time < COOLDOWN:
        prev_volume = volume
        return

    onset_slope = volume - prev_volume
    prev_volume = volume

    if volume > AMPLITUDE_THRESHOLD and onset_slope > MIN_ONSET_SLOPE:
        if is_clap_like(indata, volume):
            if now - last_clap_time < CLAP_WINDOW:
                clap_count += 1
            else:
                clap_count = 1

            last_clap_time = now
            print(f"[CLAP] Clap-like burst detected (count={clap_count}, hf_ratio passed)")

            if clap_count >= 2:
                print("[CLAP] Double clap confirmed! Waking Alfred...")
                wake_alfred()
                clap_count = 0
                last_trigger_time = now


def main():
    print("=" * 55)
    print("ALFRED CLAP-TO-WAKE LISTENER (spectral detection v2)")
    print("Clap twice sharply to wake Alfred.")
    print("Speech, coughs, and sustained sounds are filtered out.")
    print("Press Ctrl+C to stop.")
    print("=" * 55)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback,
        blocksize=BLOCK_SIZE,
    ):
        while True:
            time.sleep(0.1)


if __name__ == '__main__':
    main()