from flask import Blueprint, jsonify
from app.memory.db import get_all_history, get_memory_stats, clear_all_history, get_all_sessions, get_session_messages

memory_bp = Blueprint('memory', __name__)


@memory_bp.get('/memory')
def list_memory():
    """Return conversation history and stats for the Memory panel."""
    history = get_all_history(limit=100)
    stats = get_memory_stats()
    return jsonify({'history': history, 'stats': stats}), 200


@memory_bp.delete('/memory')
def delete_memory():
    """Clear all conversation history."""
    clear_all_history()
    return jsonify({'success': True, 'message': 'Memory cleared'}), 200

@memory_bp.get('/sessions')
def list_sessions():
    """Return all chat sessions for the Chat History panel."""
    sessions = get_all_sessions()
    return jsonify({'sessions': sessions}), 200


@memory_bp.get('/sessions/<session_id>')
def get_session(session_id):
    """Return all messages from a specific session."""
    messages = get_session_messages(session_id)
    return jsonify({'messages': messages}), 200