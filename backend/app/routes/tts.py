import os
from flask import Blueprint, send_from_directory, jsonify
from app.agent.tts_service import generate_speech, OUTPUT_DIR

tts_bp = Blueprint('tts', __name__)


@tts_bp.post('/tts/generate')
def generate():
    """Generate speech audio for given text and return the filename."""
    from flask import request
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400

    filename = generate_speech(data['text'])
    if not filename:
        return jsonify({'error': 'Failed to generate speech'}), 500

    return jsonify({'filename': filename}), 200


@tts_bp.get('/tts/audio/<filename>')
def get_audio(filename):
    """Serve a generated audio file."""
    return send_from_directory(OUTPUT_DIR, filename, mimetype='audio/wav')