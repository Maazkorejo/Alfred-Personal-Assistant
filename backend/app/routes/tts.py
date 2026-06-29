import os
from flask import Blueprint, send_from_directory, jsonify, request

tts_bp = Blueprint('tts', __name__)

DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'


@tts_bp.post('/tts/generate')
def generate():
    """Generate speech audio for given text and return the filename."""
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400

    # In demo mode, skip Piper TTS — frontend will fall back to browser TTS
    if DEMO_MODE:
        return jsonify({'error': 'TTS not available in demo mode'}), 503

    from app.agent.tts_service import generate_speech, OUTPUT_DIR
    filename = generate_speech(data['text'])
    if not filename:
        return jsonify({'error': 'Failed to generate speech'}), 500

    return jsonify({'filename': filename}), 200


@tts_bp.get('/tts/audio/<filename>')
def get_audio(filename):
    """Serve a generated audio file."""
    if DEMO_MODE:
        return jsonify({'error': 'Audio not available in demo mode'}), 503

    from app.agent.tts_service import OUTPUT_DIR
    return send_from_directory(OUTPUT_DIR, filename, mimetype='audio/wav')