from flask import Blueprint, jsonify, request
from app.agent.tools.gmail_tool import get_unread_emails, get_all_recent_emails

emails_bp = Blueprint('emails', __name__)


@emails_bp.get('/emails')
def list_emails():
    """Return recent emails for the Email panel."""
    mode = request.args.get('mode', 'unread')
    limit = int(request.args.get('limit', 15))

    if mode == 'unread':
        emails = get_unread_emails(limit=limit)
    else:
        emails = get_all_recent_emails(limit=limit)

    if emails and 'error' in emails[0]:
        return jsonify({'error': emails[0]['error']}), 500

    return jsonify({'emails': emails}), 200