import time
from flask import Blueprint, request, jsonify
from app.agent.mistral_client import chat_completion
from app.memory.db import save_message, get_recent_history
from app.agent.tools.gmail_tool import get_unread_emails, get_sent_emails, get_all_recent_emails, get_email_count, search_emails, search_by_sender
from app.agent.tools.news_tool import get_top_headlines, search_news
from app.agent.tools.weather_tool import get_weather

chat_bp = Blueprint('chat', __name__)

SYSTEM_PROMPT = '''You are Alfred, a personal AI operating assistant for Maaz Korejo.
You are helpful, concise, and professional like a butler.
You have access to the following tools — use them when relevant:

- check_emails: fetch unread emails from inbox
- check_sent: fetch recently sent emails
- recent_emails: fetch recent inbox emails (read and unread)
- search_emails: find emails by subject keyword
- search_by_sender: find emails from a specific email address
- email_count: get count of unread emails
- top_news: fetch top news headlines (argument is category like "technology", "sports", "business", "general", or "world" for global news)
- search_news: search news worldwide by keyword/topic
- get_weather: fetch current weather for a city (argument is city name, default "Jamshoro" if user doesn't specify)

When you decide to use a tool, respond with EXACTLY this format and nothing else:
TOOL:tool_name:argument

Examples:
TOOL:check_emails:5
TOOL:check_sent:5
TOOL:recent_emails:5
TOOL:search_emails:invoice
TOOL:search_by_sender:arousa@theeduassist.com
TOOL:email_count:none
TOOL:top_news:general
TOOL:top_news:technology
TOOL:search_news:artificial intelligence
TOOL:get_weather:Karachi
TOOL:get_weather:Jamshoro

If the user mentions an email address (containing @), always use search_by_sender instead of search_emails.
If the user asks for "world news" or general news without a topic, use top_news:general.
If the user asks about a specific topic in the news, use search_news.
If the user asks about weather without specifying a city, use get_weather:Jamshoro.

Otherwise just respond naturally as Alfred.
Always address the user as Mr. Maaz.'''


def handle_tool_call(tool_response: str) -> str:
    """Parse and execute a tool call from the LLM."""
    try:
        parts = tool_response.strip().split(':')
        if len(parts) < 3:
            return None

        tool_name = parts[1].strip()
        argument = ':'.join(parts[2:]).strip()

        if tool_name == 'check_emails':
            limit = int(argument) if argument.isdigit() else 5
            emails = get_unread_emails(limit=limit)
            if not emails:
                return "You have no unread emails, Mr. Maaz."
            result = f"You have {len(emails)} unread email(s), Mr. Maaz:\n\n"
            for i, e in enumerate(emails, 1):
                if 'error' in e:
                    return f"Error reading emails: {e['error']}"
                result += f"{i}. From: {e['from']}\n"
                result += f"   Subject: {e['subject']}\n"
                result += f"   Preview: {e['snippet'][:100]}...\n\n"
            return result.strip()

        elif tool_name == 'check_sent':
            limit = int(argument) if argument.isdigit() else 5
            emails = get_sent_emails(limit=limit)
            if not emails:
                return "No sent emails found, Mr. Maaz."
            result = f"Your {len(emails)} most recently sent email(s):\n\n"
            for i, e in enumerate(emails, 1):
                if 'error' in e:
                    return f"Error: {e['error']}"
                result += f"{i}. To: {e['to']}\n"
                result += f"   Subject: {e['subject']}\n"
                result += f"   Preview: {e['snippet'][:100]}...\n\n"
            return result.strip()

        elif tool_name == 'recent_emails':
            limit = int(argument) if argument.isdigit() else 5
            emails = get_all_recent_emails(limit=limit)
            if not emails:
                return "No recent emails found, Mr. Maaz."
            result = f"Your {len(emails)} most recent email(s):\n\n"
            for i, e in enumerate(emails, 1):
                if 'error' in e:
                    return f"Error: {e['error']}"
                result += f"{i}. From: {e['from']}\n"
                result += f"   Subject: {e['subject']}\n"
                result += f"   Preview: {e['snippet'][:100]}...\n\n"
            return result.strip()

        elif tool_name == 'email_count':
            count = get_email_count()
            if count == -1:
                return "I was unable to connect to your inbox, Mr. Maaz."
            return f"You have {count} unread emails in your inbox, Mr. Maaz."

        elif tool_name == 'search_emails':
            query = argument if argument != 'none' else ''
            if not query:
                return "Please specify what to search for, Mr. Maaz."
            emails = search_emails(query, limit=5)
            if not emails:
                return f"No emails found matching '{query}', Mr. Maaz."
            result = f"Found {len(emails)} email(s) matching '{query}':\n\n"
            for i, e in enumerate(emails, 1):
                if 'error' in e:
                    return f"Search error: {e['error']}"
                result += f"{i}. From: {e['from']}\n"
                result += f"   Subject: {e['subject']}\n\n"
            return result.strip()

        elif tool_name == 'search_by_sender':
            sender = argument if argument != 'none' else ''
            if not sender:
                return "Please specify the sender's email address, Mr. Maaz."
            emails = search_by_sender(sender, limit=5)
            if not emails:
                return f"No emails found from '{sender}', Mr. Maaz."
            result = f"Found {len(emails)} email(s) from '{sender}':\n\n"
            for i, e in enumerate(emails, 1):
                if 'error' in e:
                    return f"Search error: {e['error']}"
                result += f"{i}. Subject: {e['subject']}\n"
                result += f"   Date: {e['date']}\n"
                result += f"   Preview: {e['snippet'][:150]}...\n\n"
            return result.strip()

        elif tool_name == 'top_news':
            category = argument if argument not in ('none', 'world') else None
            articles = get_top_headlines(country='us', category=category, limit=5)
            if not articles:
                return "No news available right now, Mr. Maaz."
            if 'error' in articles[0]:
                return f"News error: {articles[0]['error']}"
            result = f"Here are today's top headlines, Mr. Maaz:\n\n"
            for i, a in enumerate(articles, 1):
                result += f"{i}. **{a['title']}** ({a['source']})\n"
                if a['description']:
                    result += f"   {a['description']}\n"
                result += "\n"
            return result.strip()

        elif tool_name == 'search_news':
            query = argument if argument != 'none' else ''
            if not query:
                return "Please specify a news topic, Mr. Maaz."
            articles = search_news(query, limit=5)
            if not articles:
                return f"No news found about '{query}', Mr. Maaz."
            if 'error' in articles[0]:
                return f"News error: {articles[0]['error']}"
            result = f"Latest news on '{query}', Mr. Maaz:\n\n"
            for i, a in enumerate(articles, 1):
                result += f"{i}. **{a['title']}** ({a['source']})\n"
                if a['description']:
                    result += f"   {a['description']}\n"
                result += "\n"
            return result.strip()

        elif tool_name == 'get_weather':
            city = argument if argument not in ('none', '') else 'Jamshoro'
            weather = get_weather(city)
            if 'error' in weather:
                return f"Weather error: {weather['error']}"
            return (
                f"Current weather in {weather['city']}, {weather['country']}, Mr. Maaz:\n\n"
                f"Temperature: {weather['temp']}°C (feels like {weather['feels_like']}°C)\n"
                f"Condition: {weather['condition'].title()}\n"
                f"Humidity: {weather['humidity']}%\n"
                f"Wind: {weather['wind_speed']} m/s"
            )

    except Exception as ex:
        return f"Tool execution error: {str(ex)}"

    return None


@chat_bp.post('/chat')
def chat():
    t0 = time.time()
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': "Missing 'message' field"}), 400

    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    history = get_recent_history(limit=10)

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_message})

    response = chat_completion(messages)

    if response.strip().startswith('TOOL:'):
        print(f"[TOOL] Calling: {response.strip()}")
        tool_result = handle_tool_call(response.strip())

        if tool_result:
            messages.append({'role': 'assistant', 'content': response})
            messages.append({'role': 'user', 'content': f'[TOOL RESULT] {tool_result}'})
            final_response = chat_completion(messages)
        else:
            final_response = response
    else:
        final_response = response

    save_message('user', user_message)
    save_message('assistant', final_response)

    t1 = time.time()
    print(f"[TIMING] TOTAL: {t1 - t0:.2f}s")

    return jsonify({
        'response': final_response,
        'tool_calls': [],
        'trace': []
    }), 200