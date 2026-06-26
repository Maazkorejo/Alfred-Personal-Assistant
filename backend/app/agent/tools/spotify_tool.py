import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

_sp = None


def get_spotify():
    global _sp
    if _sp is None:
        auth_manager = SpotifyOAuth(
            client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.environ.get('SPOTIFY_REDIRECT_URI'),
            scope=SCOPE,
            cache_path=os.path.join(os.path.dirname(__file__), '.spotify_cache'),
            open_browser=False,
        )
        _sp = spotipy.Spotify(auth_manager=auth_manager)
    return _sp


def get_auth_url() -> str:
    """Get the Spotify OAuth authorization URL."""
    auth_manager = SpotifyOAuth(
        client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
        client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.environ.get('SPOTIFY_REDIRECT_URI'),
        scope=SCOPE,
        cache_path=os.path.join(os.path.dirname(__file__), '.spotify_cache'),
        open_browser=False,
    )
    return auth_manager.get_authorize_url()


def exchange_code(code: str) -> bool:
    """Exchange auth code for tokens and cache them."""
    try:
        auth_manager = SpotifyOAuth(
            client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.environ.get('SPOTIFY_REDIRECT_URI'),
            scope=SCOPE,
            cache_path=os.path.join(os.path.dirname(__file__), '.spotify_cache'),
            open_browser=False,
        )
        auth_manager.get_access_token(code)
        return True
    except Exception as e:
        print(f'[SPOTIFY] Auth error: {e}')
        return False


def is_authenticated() -> bool:
    """Check if we have a valid cached token."""
    try:
        sp = get_spotify()
        sp.current_user()
        return True
    except:
        return False


def now_playing() -> dict:
    """Get currently playing track."""
    try:
        sp = get_spotify()
        current = sp.current_playback()
        if not current or not current.get('item'):
            return {'error': 'Nothing is currently playing'}
        item = current['item']
        artists = ', '.join(a['name'] for a in item['artists'])
        return {
            'track': item['name'],
            'artist': artists,
            'album': item['album']['name'],
            'is_playing': current['is_playing'],
            'progress_ms': current['progress_ms'],
            'duration_ms': item['duration_ms'],
        }
    except Exception as e:
        return {'error': str(e)}


def play_pause() -> dict:
    """Toggle play/pause."""
    try:
        sp = get_spotify()
        current = sp.current_playback()
        if not current:
            return {'error': 'No active Spotify device found'}
        if current['is_playing']:
            sp.pause_playback()
            return {'success': True, 'action': 'paused'}
        else:
            sp.start_playback()
            return {'success': True, 'action': 'resumed'}
    except Exception as e:
        return {'error': str(e)}


def pause() -> dict:
    """Pause playback."""
    try:
        get_spotify().pause_playback()
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}


def resume() -> dict:
    """Resume playback."""
    try:
        get_spotify().start_playback()
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}


def next_track() -> dict:
    """Skip to next track."""
    try:
        get_spotify().next_track()
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}


def previous_track() -> dict:
    """Go to previous track."""
    try:
        get_spotify().previous_track()
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}


def set_volume(volume: int) -> dict:
    """Set volume 0-100."""
    try:
        volume = max(0, min(100, volume))
        get_spotify().volume(volume)
        return {'success': True, 'volume': volume}
    except Exception as e:
        return {'error': str(e)}


def search_and_play(query: str) -> dict:
    """Search for a track and play it."""
    try:
        sp = get_spotify()
        results = sp.search(q=query, limit=1, type='track')
        tracks = results['tracks']['items']
        if not tracks:
            return {'error': f'No tracks found for "{query}"'}
        track = tracks[0]
        sp.start_playback(uris=[track['uri']])
        artists = ', '.join(a['name'] for a in track['artists'])
        return {
            'success': True,
            'track': track['name'],
            'artist': artists,
        }
    except Exception as e:
        return {'error': str(e)}