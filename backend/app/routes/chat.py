from datetime import datetime
import time
import re
from flask import Blueprint, request, jsonify
from app.agent.mistral_client import chat_completion
from app.memory.db import save_message, get_recent_history
import uuid
from concurrent.futures import ThreadPoolExecutor
from app.agent.tools.gmail_tool import get_unread_emails, get_sent_emails, get_all_recent_emails, get_email_count, search_emails, search_by_sender
from app.agent.tools.news_tool import get_top_headlines, search_news
from app.agent.tools.weather_tool import get_weather
from app.agent.tools.time_tool import get_current_time
from app.agent.tools.system_tool import open_website
from app.agent.tools.app_launcher_tool import open_app, open_path
from app.agent.tools.calendar_tool import add_event, get_today_events, get_upcoming_events, delete_event, search_events
from app.agent.tools.reminder_tool import create_reminder, list_reminders, complete_reminder, delete_reminder, parse_relative_time

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
- add_event: add a calendar event (argument format: "title|YYYY-MM-DD HH:MM" or "title|YYYY-MM-DD HH:MM|YYYY-MM-DD HH:MM" for end time, or "title|YYYY-MM-DD HH:MM|none|description")
- today_events: get all events scheduled for today (argument: none)
- upcoming_events: get events in the next N days (argument: number of days, e.g. 7)
- delete_event: delete a calendar event by ID (argument: event UUID)
- search_calendar: search calendar events by keyword (argument: keyword)
- set_reminder: set a reminder (argument format: "title|YYYY-MM-DD HH:MM")
- list_reminders: show all pending reminders (argument: none)
- complete_reminder: mark a reminder as done (argument: reminder ID number)
- delete_reminder: delete a reminder (argument: reminder ID number)

TOOL CALL EXAMPLES (respond with ONLY this, no other text):
TOOL:check_emails:5
TOOL:get_weather:Karachi
TOOL:get_time:Tokyo
TOOL:open_browser:youtube
TOOL:open_app:spotify
TOOL:open_app:linkedin
TOOL:open_path:C:\\Users\\maazk\\Desktop
TOOL:add_event:Team meeting|2025-01-15 14:00
TOOL:add_event:Doctor appointment|2025-01-16 10:00|2025-01-16 11:00
TOOL:add_event:Call with Ali|2025-01-17 15:00|none|Discuss project updates
TOOL:today_events:none
TOOL:upcoming_events:7
TOOL:delete_event:uuid-here
TOOL:search_calendar:meeting
TOOL:set_reminder:Call Ali|2025-01-15 14:00
TOOL:set_reminder:Take medicine|2025-01-15 08:00
TOOL:list_reminders:none
TOOL:complete_reminder:3
TOOL:delete_reminder:3

RULES:
- If the user mentions an email address (@), use search_by_sender.
- If asked for general/world news, use top_news:general.
- If asked about weather/time without a city, default to Jamshoro.
- If asked to open/launch/watch/search something on the web, use open_browser.
- If asked to open a DESKTOP APP (Spotify, Notepad, Discord, LinkedIn, VS Code), use open_app — NOT open_browser.
- If the user asks to open a specific file or folder by path, use open_path.
- For calendar events and reminders, parse the date and time naturally using the CURRENT DATE AND TIME provided below.
- If user says "tomorrow at 3pm", convert to the correct YYYY-MM-DD HH:MM format. If user says "in 30 minutes", calculate from current time.
- Always use 24-hour format when constructing datetime strings for tool calls (e.g. 16:30 not 4:30pm).
- Always confirm the event or reminder details naturally after adding.
- If user asks what's on their calendar, use today_events or upcoming_events.
- If user asks about reminders, use list_reminders.
- NEVER say you will use a tool without actually outputting the TOOL: format. If you mean to call a tool, your full response must be JUST the TOOL: line — no narration, no explanation, no "let me check" before it.
- If a tool result contains "error", be honest about the failure. NEVER fabricate data.
- After a tool result is given to you, respond in natural language ONLY — never output TOOL: syntax in your final answer to the user.
- For anything else, respond naturally as Alfred.
- Address the user by whatever name they request.

REMEMBER: Tool calls must be EXACTLY "TOOL:name:argument" with absolutely no extra words, explanation, or narration before or after. Not even "Let me check that for you" — just the TOOL: line by itself.'''


def format_datetime(dt_str: str) -> str:
    """Format a datetime string nicely for display."""
    if not dt_str or dt_str == 'None':
        return ''
    try:
        dt = datetime.fromisoformat(dt_str.replace('+00:00', '').strip())
        return dt.strftime('%a, %b %d at %I:%M %p')
    except:
        return dt_str


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

        elif tool_name == 'add_event':
            parts_event = argument.split('|')
            if len(parts_event) < 2:
                return "Please provide event title and date/time."
            title = parts_event[0].strip()
            start = parts_event[1].strip()
            end = parts_event[2].strip() if len(parts_event) > 2 and parts_event[2].strip() != 'none' else None
            description = parts_event[3].strip() if len(parts_event) > 3 else None
            result = add_event(title, start, end, description)
            if not result['success']:
                return f"Calendar error: {result['error']}"
            return f"Event added: {result['message']}"

        elif tool_name == 'today_events':
            events = get_today_events()
            if not events:
                return "You have no events scheduled for today."
            if 'error' in events[0]:
                return f"Calendar error: {events[0]['error']}"
            result = f"Your events for today:\n\n"
            for i, e in enumerate(events, 1):
                result += f"{i}. **{e['title']}**\n"
                result += f"   {format_datetime(e['start_datetime'])}"
                if e['end_datetime']:
                    result += f" → {format_datetime(e['end_datetime'])}"
                result += "\n"
                if e['description']:
                    result += f"   {e['description']}\n"
                result += f"   ID: {e['id']}\n\n"
            return result.strip()

        elif tool_name == 'upcoming_events':
            days = int(argument) if argument.isdigit() else 7
            events = get_upcoming_events(days)
            if not events:
                return f"No events in the next {days} days."
            if 'error' in events[0]:
                return f"Calendar error: {events[0]['error']}"
            result = f"Upcoming events (next {days} days):\n\n"
            for i, e in enumerate(events, 1):
                result += f"{i}. **{e['title']}**\n"
                result += f"   {format_datetime(e['start_datetime'])}"
                if e['end_datetime']:
                    result += f" → {format_datetime(e['end_datetime'])}"
                result += "\n"
                if e['description']:
                    result += f"   {e['description']}\n"
                result += f"   ID: {e['id']}\n\n"
            return result.strip()

        elif tool_name == 'delete_event':
            event_id = argument.strip()
            if not event_id or event_id == 'none':
                return "Please provide the event ID to delete."
            result = delete_event(event_id)
            if not result['success']:
                return f"Delete error: {result['error']}"
            return "Event deleted successfully."

        elif tool_name == 'search_calendar':
            keyword = argument if argument != 'none' else ''
            if not keyword:
                return "Please specify a search keyword."
            events = search_events(keyword)
            if not events:
                return f"No events found matching '{keyword}'."
            if 'error' in events[0]:
                return f"Calendar error: {events[0]['error']}"
            result = f"Found {len(events)} event(s) matching '{keyword}':\n\n"
            for i, e in enumerate(events, 1):
                result += f"{i}. **{e['title']}**\n"
                result += f"   {format_datetime(e['start_datetime'])}\n"
                result += f"   ID: {e['id']}\n\n"
            return result.strip()

        elif tool_name == 'set_reminder':
            parts_rem = argument.split('|')
            if len(parts_rem) < 2:
                return "Please provide reminder title and date/time."
            title = parts_rem[0].strip()
            due_str = parts_rem[1].strip()
            try:
                due_at = parse_relative_time(due_str) or datetime.fromisoformat(due_str)
            except ValueError:
                return f"I couldn't parse the time '{due_str}'. Please use a format like '2025-01-15 14:00'."
            result = create_reminder(title, due_at)
            if not result['success']:
                return f"Reminder error: {result['error']}"
            return f"Reminder set: \"{title}\" at {due_str}"

        elif tool_name == 'list_reminders':
            reminders = list_reminders(include_completed=False)
            if not reminders:
                return "You have no pending reminders."
            if 'error' in reminders[0]:
                return f"Reminder error: {reminders[0]['error']}"
            result = "Your pending reminders:\n\n"
            for r in reminders:
                result += f"• [{r['id']}] **{r['title']}**\n"
                result += f"  Due: {format_datetime(r['due_at'])}\n\n"
            return result.strip()

        elif tool_name == 'complete_reminder':
            try:
                rid = int(argument.strip())
            except ValueError:
                return "Please provide a valid reminder ID number."
            result = complete_reminder(rid)
            if not result['success']:
                return f"Error: {result['error']}"
            return "Reminder marked as complete."

        elif tool_name == 'delete_reminder':
            try:
                rid = int(argument.strip())
            except ValueError:
                return "Please provide a valid reminder ID number."
            result = delete_reminder(rid)
            if not result['success']:
                return f"Error: {result['error']}"
            return "Reminder deleted."

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

    session_id = data.get('session_id') or str(uuid.uuid4())

    t1 = time.time()
    history = get_recent_history(limit=10, session_id=session_id)
    t2 = time.time()
    print(f"[TIMING] get_recent_history: {t2 - t1:.2f}s")

    now = datetime.now()
    today_str = now.strftime('%A, %B %d, %Y')
    time_str = now.strftime('%I:%M %p')
    dynamic_prompt = SYSTEM_PROMPT + f'\n\nCURRENT DATE AND TIME: Today is {today_str} and the current time is {time_str} (Pakistan Standard Time). Use this when calculating dates and times like "tomorrow", "in 30 minutes", "at 4:30pm", etc. Always use 24-hour format when constructing datetime strings for tool calls.'

    messages = [{'role': 'system', 'content': dynamic_prompt}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_message})

    t3 = time.time()
    response = chat_completion(messages)
    t4 = time.time()
    print(f"[TIMING] first mistral call: {t4 - t3:.2f}s")

    tool_match = re.search(r'TOOL:([a-z_]+):([^\n]+)', response)

    if tool_match:
        tool_call_str = f"TOOL:{tool_match.group(1)}:{tool_match.group(2)}"
        print(f"[TOOL] Calling: {tool_call_str}")

        t5 = time.time()
        tool_result = handle_tool_call(tool_call_str)
        t6 = time.time()
        print(f"[TIMING] tool execution ({tool_match.group(1)}): {t6 - t5:.2f}s")

        if tool_result:
            messages.append({'role': 'assistant', 'content': response})
            messages.append({'role': 'user', 'content': f'[TOOL RESULT] {tool_result}. Now respond naturally to the user in plain language — do not output TOOL: syntax.'})

            t7 = time.time()
            final_response = chat_completion(messages)
            t8 = time.time()
            print(f"[TIMING] second mistral call: {t8 - t7:.2f}s")
        else:
            final_response = response
    else:
        final_response = response

    t9 = time.time()
    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(save_message, 'user', user_message, session_id)
        f2 = executor.submit(save_message, 'assistant', final_response, session_id)
        f1.result()
        f2.result()
    t10 = time.time()
    print(f"[TIMING] save_message x2 (parallel): {t10 - t9:.2f}s")

    print(f"[TIMING] TOTAL: {t10 - t0:.2f}s")

    return jsonify({
        'response': final_response,
        'tool_calls': [],
        'trace': [],
        'session_id': session_id
    }), 200