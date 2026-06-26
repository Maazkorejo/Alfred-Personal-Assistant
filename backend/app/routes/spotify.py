from flask import Blueprint, jsonify, request, redirect
from app.agent.tools.spotify_tool import (
    get_auth_url, exchange_code, is_authenticated,
    now_playing, play_pause, pause, resume,
    next_track, previous_track, set_volume, search_and_play
)

spotify_bp = Blueprint('spotify', __name__)


@spotify_bp.get('/spotify/auth')
def auth():
    url = get_auth_url()
    return jsonify({'auth_url': url})


@spotify_bp.get('/spotify/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    success = exchange_code(code)
    if success:
        return '''<html><body style="background:#050507;color:#E8D5A3;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <div style="text-align:center"><h2>✓ Spotify Connected</h2><p>You can close this tab. Alfred is ready.</p></div></body></html>'''
    return '''<html><body style="background:#050507;color:#ff6b6b;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
    <div style="text-align:center"><h2>✗ Auth Failed</h2><p>Please try again.</p></div></body></html>'''


@spotify_bp.get('/spotify/status')
def status():
    return jsonify({'authenticated': is_authenticated()})


@spotify_bp.get('/spotify/now-playing')
def current():
    return jsonify(now_playing())


@spotify_bp.post('/spotify/play-pause')
def toggle():
    return jsonify(play_pause())


@spotify_bp.post('/spotify/pause')
def pause_route():
    return jsonify(pause())


@spotify_bp.post('/spotify/resume')
def resume_route():
    return jsonify(resume())


@spotify_bp.post('/spotify/next')
def next_route():
    return jsonify(next_track())


@spotify_bp.post('/spotify/previous')
def prev_route():
    return jsonify(previous_track())


@spotify_bp.post('/spotify/volume')
def volume_route():
    data = request.get_json(silent=True) or {}
    vol = data.get('volume', 50)
    return jsonify(set_volume(int(vol)))


@spotify_bp.post('/spotify/play')
def play_route():
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'query required'}), 400
    return jsonify(search_and_play(query))