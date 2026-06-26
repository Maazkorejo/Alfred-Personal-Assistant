from flask import Blueprint, jsonify, request
from app.agent.tools.reminder_tool import list_reminders, complete_reminder, delete_reminder, create_reminder
from datetime import datetime

reminders_bp = Blueprint('reminders', __name__)


@reminders_bp.get('/reminders')
def get_reminders():
    include_completed = request.args.get('include_completed', 'false') == 'true'
    reminders = list_reminders(include_completed=include_completed)
    return jsonify({'reminders': reminders}), 200


@reminders_bp.post('/reminders')
def add_reminder():
    data = request.get_json(silent=True)
    if not data or 'title' not in data or 'due_at' not in data:
        return jsonify({'error': 'Missing title or due_at'}), 400

    try:
        due_at = datetime.fromisoformat(data['due_at'])
    except ValueError:
        return jsonify({'error': 'Invalid due_at format, use ISO format'}), 400

    result = create_reminder(data['title'], due_at)
    if not result['success']:
        return jsonify({'error': result['error']}), 500
    return jsonify(result), 201


@reminders_bp.patch('/reminders/<int:reminder_id>/complete')
def mark_complete(reminder_id):
    result = complete_reminder(reminder_id)
    if not result['success']:
        return jsonify({'error': result['error']}), 500
    return jsonify({'success': True}), 200


@reminders_bp.delete('/reminders/<int:reminder_id>')
def remove_reminder(reminder_id):
    result = delete_reminder(reminder_id)
    if not result['success']:
        return jsonify({'error': result['error']}), 500
    return jsonify({'success': True}), 200