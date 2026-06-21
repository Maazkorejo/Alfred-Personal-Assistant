import time
from flask import Blueprint, request, jsonify
from app.agent.mistral_client import chat_completion
from app.memory.db import save_message, get_recent_history
from app.agent.tools.gmail_tool import get_unread_emails, get_sent_emails, get_all_recent_emails, get_email_count, search_emails, search_by_sender
from app.agent.tools.news_tool import get_top_headlines, search_news
from app.agent.tools.weather_tool import get_weather
from app.agent.tools.time_tool import get_current_time
from app.agent.tools.system_tool import open_website
from app.agent.tools.app_launcher_tool import open_app, open_path

chat_bp = Blueprint('chat', __name__)

SYSTEM_PROMPT = '''CRITICAL RULE: When you need to use a tool, your ENTIRE response must be ONLY this format, nothing else, no explanation before or after:
TOOL:tool_name:argument

You are Alfred, a personal AI operating assistant for Maaz Korejo. You are helpful, concise, and professional like a butler.

AVAILABLE TOOLS:
- check_emails: fetch unread emails from inbox
- check_sent: fetch recently sent emails
- recent_emails: fetch recent inbox emails (read and unread)
- search_emails: find emails by subject keyword
- search_by_sender: find emails from a specific email address
- email_count: get count of unread emails
- top_news: fetch top news headlines (argument is category like "technology", "sports", "business", "general", or "world")
- search_news: search news worldwide by keyword/topic
- get_weather: fetch current weather for a city (argument is city name, default "Jamshoro")
- get_time: get current time/date for a location (argument is city name, default "Jamshoro")
- open_browser: open a website (argument is site name, URL, or search query)
- open_app: open any installed desktop or Windows Store application by name (e.g. "spotify", "notepad", "discord", "linkedin", "chrome")
- open_path: open a specific file or folder by its full path (argument is the absolute path, e.g. "C:\\Users\\maazk\\Desktop" or "C:\\Users\\maazk\\Documents\\report.pdf")

TOOL CALL EXAMPLES (respond with ONLY this, no other text):
TOOL:check_emails:5
TOOL:get_weather:Karachi
TOOL:get_time:Tokyo
TOOL:open_browser:youtube
TOOL:open_app:spotify
TOOL:open_app:linkedin
TOOL:open_path:C:\\Users\\maazk\\Desktop

RULES:
- If the user mentions an email address (@), use search_by_sender.
- If asked for general/world news, use top_news:general.
- If asked about weather/time without a city, default to Jamshoro.
- If asked to open/launch/watch/search something on the web, use open_browser.
- If asked to open a DESKTOP APP (Spotify, Notepad, Discord, LinkedIn, VS Code), use open_app — NOT open_browser.
- If the user asks to open a specific file or folder by path, use open_path.
- NEVER say you will use a tool without actually outputting the TOOL: format. If you mean to call a tool, your full response must be JUST the TOOL: line.
- If a tool result contains "error", be honest about the failure. NEVER fabricate data.
- After a tool result is given to you, respond in natural language ONLY — never output TOOL: syntax in your final answer to the user.
- For anything else, respond naturally as Alfred.
- Address the user by whatever name they request.

REMEMBER: Tool calls must be EXACTLY "TOOL:name:argument" with no extra words before or after.'''


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
                return "You have no unread emails."
            result = f"You have {len(emails)} unread email(s):\n\n"
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
                return "No sent emails found."
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
                return "No recent emails found."
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
                return "I was unable to connect to your inbox."
            return f"You have {count} unread emails in your inbox."

        elif tool_name == 'search_emails':
            query = argument if argument != 'none' else ''
            if not query:
                return "Please specify what to search for."
            emails = search_emails(query, limit=5)
            if not emails:
                return f"No emails found matching '{query}'."
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
                return "Please specify the sender's email address."
            emails = search_by_sender(sender, limit=5)
            if not emails:
                return f"No emails found from '{sender}'."
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
                return "No news available right now."
            if 'error' in articles[0]:
                return f"News error: {articles[0]['error']}"
            result = f"Here are today's top headlines:\n\n"
            for i, a in enumerate(articles, 1):
                result += f"{i}. **{a['title']}** ({a['source']})\n"
                if a['description']:
                    result += f"   {a['description']}\n"
                result += "\n"
            return result.strip()

        elif tool_name == 'search_news':
            query = argument if argument != 'none' else ''
            if not query:
                return "Please specify a news topic."
            articles = search_news(query, limit=5)
            if not articles:
                return f"No news found about '{query}'."
            if 'error' in articles[0]:
                return f"News error: {articles[0]['error']}"
            result = f"Latest news on '{query}':\n\n"
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
                f"Current weather in {weather['city']}, {weather['country']}:\n\n"
                f"Temperature: {weather['temp']}°C (feels like {weather['feels_like']}°C)\n"
                f"Condition: {weather['condition'].title()}\n"
                f"Humidity: {weather['humidity']}%\n"
                f"Wind: {weather['wind_speed']} m/s"
            )

        elif tool_name == 'get_time':
            location = argument if argument not in ('none', '') else 'Jamshoro'
            time_data = get_current_time(location)
            if 'error' in time_data:
                return f"Time error: {time_data['error']}"
            return (
                f"It is currently {time_data['time']} in {time_data['location']}.\n"
                f"Today is {time_data['date']}."
            )

        elif tool_name == 'open_browser':
            site = argument if argument not in ('none', '') else ''
            if not site:
                return "Please specify what to open."
            result = open_website(site)
            if not result['success']:
                return f"Browser error: {result['error']}"
            return f"Opened: {result['url']}"

        elif tool_name == 'open_app':
            app_name = argument if argument not in ('none', '') else ''
            if not app_name:
                return "Please specify which app to open."
            result = open_app(app_name)
            if not result['success']:
                return f"App launch error: {result['error']}"
            return f"Opening {app_name} now."

        elif tool_name == 'open_path':
            path = argument if argument not in ('none', '') else ''
            if not path:
                return "Please specify the file or folder path."
            result = open_path(path)
            if not result['success']:
                return f"Path error: {result['error']}"
            return f"Opened: {result['path']}"

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
            messages.append({'role': 'user', 'content': f'[TOOL RESULT] {tool_result}. Now respond naturally to the user in plain language — do not output TOOL: syntax.'})
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