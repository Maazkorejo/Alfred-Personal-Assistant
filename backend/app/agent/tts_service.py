import subprocess
import os
import re
import uuid
import sys

VOICE_MODEL = os.path.join(os.path.dirname(__file__), '..', '..', 'piper_voices', 'en_GB-alan-medium.onnx')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'tts_output')
LENGTH_SCALE = '0.85'

os.makedirs(OUTPUT_DIR, exist_ok=True)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting before speaking."""
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s?', '', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'^[-*+]\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'-{2,}', '', text)
    return text.strip()


def sanitize_for_speech(text: str) -> str:
    """
    Remove characters Piper can't handle: non-Latin scripts, emoji,
    stylized Unicode (mathematical alphanumeric symbols), etc.
    Keeps standard ASCII + common punctuation.
    """
    # Keep only basic Latin letters, numbers, and common punctuation
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Collapse multiple spaces caused by removed characters
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def generate_speech(text: str) -> str:
    """
    Generate speech audio from text using Piper.
    Returns the filename of the generated .wav file (relative to OUTPUT_DIR).
    """
    clean_text = strip_markdown(text)
    clean_text = sanitize_for_speech(clean_text)
    if not clean_text:
        return None

    filename = f"{uuid.uuid4().hex}.wav"
    output_path = os.path.join(OUTPUT_DIR, filename)

    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'piper', '-m', VOICE_MODEL, '-f', output_path, '--length_scale', LENGTH_SCALE],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.communicate(input=clean_text.encode('utf-8'), timeout=15)

        if os.path.exists(output_path):
            return filename
        return None

    except Exception as e:
        print(f"[TTS] Error generating speech: {e}")
        return None