import time
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
    t0 = time.time()
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': "Missing 'message' field"}), 400

    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    t1 = time.time()
    history = get_recent_history(limit=10)
    t2 = time.time()
    print(f"[TIMING] get_recent_history: {t2 - t1:.2f}s")

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_message})

    t3 = time.time()
    response = chat_completion(messages)
    t4 = time.time()
    print(f"[TIMING] mistral_completion: {t4 - t3:.2f}s")

    t5 = time.time()
    save_message('user', user_message)
    save_message('assistant', response)
    t6 = time.time()
    print(f"[TIMING] save_message x2: {t6 - t5:.2f}s")

    print(f"[TIMING] TOTAL: {t6 - t0:.2f}s")

    return jsonify({
        'response': response,
        'tool_calls': [],
        'trace': []
    }), 200