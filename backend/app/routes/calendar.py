from flask import Blueprint, jsonify, request
from app.agent.tools.calendar_tool import add_event, get_all_events, delete_event, search_events

calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.get('/calendar')
def get_events():
    events = get_all_events()
    if events and 'error' in events[0]:
        return jsonify({'error': events[0]['error']}), 500
    return jsonify({'events': events}), 200


@calendar_bp.post('/calendar')
def create_event():
    data = request.get_json(silent=True)
    if not data or 'title' not in data or 'start_datetime' not in data:
        return jsonify({'error': 'title and start_datetime are required'}), 400

    result = add_event(
        title=data['title'],
        start_datetime=data['start_datetime'],
        end_datetime=data.get('end_datetime'),
        description=data.get('description'),
    )
    if not result['success']:
        return jsonify({'error': result['error']}), 500
    return jsonify(result), 201


@calendar_bp.delete('/calendar/<event_id>')
def remove_event(event_id):
    result = delete_event(event_id)
    if not result['success']:
        return jsonify({'error': result['error']}), 404
    return jsonify(result), 200


@calendar_bp.get('/calendar/search')
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({'error': 'q parameter required'}), 400
    events = search_events(keyword)
    if events and 'error' in events[0]:
        return jsonify({'error': events[0]['error']}), 500
    return jsonify({'events': events}), 200
    from flask import Blueprint, jsonify, request
from app.agent.tools.calendar_tool import add_event, get_all_events, delete_event, search_events

calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.get('/calendar')
def get_events():
    events = get_all_events()
    if events and 'error' in events[0]:
        return jsonify({'error': events[0]['error']}), 500
    return jsonify({'events': events}), 200


@calendar_bp.post('/calendar')
def create_event():
    data = request.get_json(silent=True)
    if not data or 'title' not in data or 'start_datetime' not in data:
        return jsonify({'error': 'title and start_datetime are required'}), 400

    result = add_event(
        title=data['title'],
        start_datetime=data['start_datetime'],
        end_datetime=data.get('end_datetime'),
        description=data.get('description'),
    )
    if not result['success']:
        return jsonify({'error': result['error']}), 500
    return jsonify(result), 201


@calendar_bp.delete('/calendar/<event_id>')
def remove_event(event_id):
    result = delete_event(event_id)
    if not result['success']:
        return jsonify({'error': result['error']}), 404
    return jsonify(result), 200


@calendar_bp.get('/calendar/search')
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({'error': 'q parameter required'}), 400
    events = search_events(keyword)
    if events and 'error' in events[0]:
        return jsonify({'error': events[0]['error']}), 500
    return jsonify({'events': events}), 200