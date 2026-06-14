from flask import Blueprint, request, jsonify
from app.agent.mistral_client import chat_completion
from app.memory.db import save_message, get_recent_history

chat_bp = Blueprint('chat', __name__)

SYSTEM_PROMPT = '''You are Alfred, a personal AI operating assistant.
You are helpful, concise, and professional.
You help with tasks like email, calendar, reminders, and answering questions.
Always address the user respectfully and get straight to the point.'''


@chat_bp.post('/chat')
def chat():
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': "Missing 'message' field"}), 400

    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Load recent history for context
    history = get_recent_history(limit=10)

    # Build messages list with system prompt + history + new message
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_message})

    # Get Mistral response
    response = chat_completion(messages)

    # Save both turns to Postgres
    save_message('user', user_message)
    save_message('assistant', response)

    return jsonify({
        'response': response,
        'tool_calls': [],
        'trace': []
    }), 200
