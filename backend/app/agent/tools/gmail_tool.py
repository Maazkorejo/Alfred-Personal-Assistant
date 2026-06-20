import imaplib
import email
import os
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')


def connect_imap():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    return mail


def decode_str(s):
    if s is None:
        return ''
    parts = decode_header(s)
    result = ''
    for decoded, encoding in parts:
        if isinstance(decoded, bytes):
            result += decoded.decode(encoding or 'utf-8', errors='ignore')
        else:
            result += str(decoded)
    return result


def get_body(msg):
    """Extract plain text body from email."""
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    body = body[:300].strip()
                except:
                    pass
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            body = body[:300].strip()
        except:
            pass
    return body


def fetch_emails_from_folder(folder='INBOX', criteria='UNSEEN', limit=5):
    """Generic function to fetch emails from any folder."""
    try:
        mail = connect_imap()
        mail.select(folder)

        _, message_ids = mail.search(None, criteria)
        ids = message_ids[0].split()

        if not ids:
            mail.logout()
            return []

        recent_ids = ids[-limit:]
        emails = []

        for msg_id in reversed(recent_ids):
            _, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            emails.append({
                'subject': decode_str(msg.get('Subject', '(No Subject)')),
                'from': decode_str(msg.get('From', '')),
                'to': decode_str(msg.get('To', '')),
                'date': msg.get('Date', ''),
                'snippet': get_body(msg),
            })

        mail.logout()
        return emails

    except Exception as e:
        return [{'error': str(e)}]


def get_unread_emails(limit=5):
    """Fetch unread emails from inbox."""
    return fetch_emails_from_folder('INBOX', 'UNSEEN', limit)


def get_sent_emails(limit=5):
    """Fetch recently sent emails."""
    return fetch_emails_from_folder('"[Gmail]/Sent Mail"', 'ALL', limit)


def get_all_recent_emails(limit=5):
    """Fetch recent emails from inbox regardless of read status."""
    return fetch_emails_from_folder('INBOX', 'ALL', limit)


def get_email_count():
    """Get count of unread emails in inbox."""
    try:
        mail = connect_imap()
        mail.select('INBOX')
        _, message_ids = mail.search(None, 'UNSEEN')
        count = len(message_ids[0].split()) if message_ids[0] else 0
        mail.logout()
        return count
    except Exception as e:
        return -1


def search_emails(query, limit=5, folder='INBOX'):
    """Search emails by subject keyword in any folder."""
    try:
        # Sanitize query — IMAP search breaks on special chars in raw strings
        clean_query = query.replace('"', '').replace("'", '').strip()

        mail = connect_imap()
        mail.select(folder)

        # Use literal syntax instead of quoted string to avoid escaping issues
        query_bytes = clean_query.encode('utf-8')
        _, message_ids = mail.search(None, 'SUBJECT', query_bytes)
        ids = message_ids[0].split()

        if not ids:
            # Fallback: try searching just the first significant word
            first_word = clean_query.split()[0] if clean_query.split() else clean_query
            _, message_ids = mail.search(None, 'SUBJECT', first_word.encode('utf-8'))
            ids = message_ids[0].split()

        if not ids and folder == 'INBOX':
            # Also try sent folder
            mail.select('"[Gmail]/Sent Mail"')
            _, message_ids = mail.search(None, 'SUBJECT', query_bytes)
            ids = message_ids[0].split()

        if not ids:
            mail.logout()
            return []

        recent_ids = ids[-limit:]
        emails = []

        for msg_id in reversed(recent_ids):
            _, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            emails.append({
                'subject': decode_str(msg.get('Subject', '')),
                'from': decode_str(msg.get('From', '')),
                'to': decode_str(msg.get('To', '')),
                'date': msg.get('Date', ''),
                'snippet': get_body(msg),
            })

        mail.logout()
        return emails

    except Exception as e:
        return [{'error': str(e)}]

def search_by_sender(sender_email, limit=5, folder='INBOX'):
    """Search emails by sender's email address."""
    try:
        clean_sender = sender_email.strip()

        mail = connect_imap()
        mail.select(folder)

        sender_bytes = clean_sender.encode('utf-8')
        _, message_ids = mail.search(None, 'FROM', sender_bytes)
        ids = message_ids[0].split()

        if not ids and folder == 'INBOX':
            mail.select('"[Gmail]/All Mail"')
            _, message_ids = mail.search(None, 'FROM', sender_bytes)
            ids = message_ids[0].split()

        if not ids:
            mail.logout()
            return []

        recent_ids = ids[-limit:]
        emails = []

        for msg_id in reversed(recent_ids):
            _, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            emails.append({
                'subject': decode_str(msg.get('Subject', '')),
                'from': decode_str(msg.get('From', '')),
                'to': decode_str(msg.get('To', '')),
                'date': msg.get('Date', ''),
                'snippet': get_body(msg),
            })

        mail.logout()
        return emails

    except Exception as e:
        return [{'error': str(e)}]        