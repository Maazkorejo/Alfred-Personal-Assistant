from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)


@chat_bp.post('/chat')
def chat():
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': "Missing 'message' field"}), 400

    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    return jsonify({
        'response': f'[Echo] {user_message}',
        'tool_calls': [],
        'trace': []
    }), 200
