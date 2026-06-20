from flask import Blueprint, jsonify
from app.memory.db import get_all_history, get_memory_stats, clear_all_history

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