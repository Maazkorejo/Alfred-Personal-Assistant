"""
Demo mode responses — realistic mock data for recruiter demo.
No real API keys or personal data used.
"""

import random
from datetime import datetime, timedelta

def get_demo_response(message: str) -> str:
    msg = message.lower().strip()

    # Greetings
    if any(w in msg for w in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
        greetings = [
            "Good day, sir. Alfred at your service. How may I assist you today?",
            "Welcome back. All systems are operational and ready for your command.",
            "Good evening. I trust you are well. What can I do for you today?",
        ]
        return random.choice(greetings)

    # Weather
    if 'weather' in msg:
        cities = {'karachi': ('32', 'Partly cloudy'), 'lahore': ('28', 'Sunny'), 'islamabad': ('24', 'Clear skies')}
        city = 'Karachi'
        temp, condition = '32', 'Partly cloudy'
        for c, data in cities.items():
            if c in msg:
                city = c.title()
                temp, condition = data
        return (
            f"Current weather in {city}:\n\n"
            f"Temperature: {temp}°C (feels like {int(temp)-2}°C)\n"
            f"Condition: {condition}\n"
            f"Humidity: 65%\n"
            f"Wind: 3.2 m/s"
        )

    # Time
    if any(w in msg for w in ['time', 'date', 'today']):
        now = datetime.now()
        return (
            f"It is currently {now.strftime('%I:%M %p')} in Karachi.\n"
            f"Today is {now.strftime('%A, %B %d, %Y')}."
        )

    # Emails
    if any(w in msg for w in ['email', 'inbox', 'mail', 'unread']):
        return (
            "You have 3 unread emails:\n\n"
            "1. From: hr@techcorp.com\n"
            "   Subject: Interview Invitation — Backend Engineer Role\n"
            "   Preview: We were impressed by your profile and would like to schedule...\n\n"
            "2. From: github@notifications.com\n"
            "   Subject: New star on Alfred-Personal-Assistant\n"
            "   Preview: Someone starred your repository Alfred-Personal-Assistant...\n\n"
            "3. From: newsletter@aiweekly.com\n"
            "   Subject: This week in AI — GPT updates, new models and more\n"
            "   Preview: Welcome to this week's AI digest. Here's what happened..."
        )

    # News
    if any(w in msg for w in ['news', 'headlines', 'latest']):
        return (
            "Here are today's top headlines:\n\n"
            "1. **OpenAI announces new reasoning model** (TechCrunch)\n"
            "   The latest model shows significant improvements in coding and math tasks.\n\n"
            "2. **Pakistan tech sector sees record investment** (Dawn)\n"
            "   Foreign investment in Pakistani startups hits an all-time high this quarter.\n\n"
            "3. **Anthropic releases Claude 4** (The Verge)\n"
            "   The new model outperforms competitors on key benchmarks.\n\n"
            "4. **Global AI regulation framework proposed** (BBC)\n"
            "   World leaders agree on preliminary guidelines for AI development.\n\n"
            "5. **Electric vehicle sales surge in Asia** (Reuters)\n"
            "   EV adoption accelerates across Southeast Asia and South Asia."
        )

    # Calendar
    if any(w in msg for w in ['calendar', 'schedule', 'event', 'meeting']):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A, %B %d')
        return (
            f"Your upcoming events:\n\n"
            f"1. **Team Standup** — Today at 10:00 AM\n"
            f"2. **Code Review Session** — Today at 2:00 PM\n"
            f"3. **Interview Prep** — {tomorrow} at 11:00 AM\n"
            f"4. **Project Demo** — {tomorrow} at 3:00 PM\n\n"
            f"You have a busy day ahead, sir."
        )

    # Reminders
    if any(w in msg for w in ['reminder', 'remind']):
        return (
            "Your pending reminders:\n\n"
            "• [1] **Submit project report** — Due today at 5:00 PM\n"
            "• [2] **Call mentor** — Due tomorrow at 10:00 AM\n"
            "• [3] **Update portfolio** — Due Friday at 6:00 PM\n\n"
            "Shall I mark any of these as complete, sir?"
        )

    # Open app/browser
    if any(w in msg for w in ['open', 'launch', 'play', 'spotify', 'youtube', 'chrome']):
        if 'spotify' in msg:
            return "Opening Spotify now, sir. Enjoy the music."
        if 'youtube' in msg:
            return "Opening YouTube in your browser now."
        if 'chrome' in msg:
            return "Launching Chrome for you."
        return "Opening that for you now, sir."

    # Compliments / thanks
    if any(w in msg for w in ['thank', 'thanks', 'good job', 'well done', 'great']):
        return "Always a pleasure to be of service, sir."

    # Who are you
    if any(w in msg for w in ['who are you', 'what are you', 'introduce']):
        return (
            "I am Alfred, your personal AI operating assistant. "
            "Inspired by Batman's trusted butler, I am here to manage your emails, "
            "calendar, reminders, news, weather, and much more — "
            "all through natural conversation. How may I assist you today, sir?"
        )

    # Capabilities
    if any(w in msg for w in ['what can you do', 'capabilities', 'features', 'help']):
        return (
            "I am capable of the following, sir:\n\n"
            "📧 **Email** — Read, search, and manage your inbox\n"
            "📅 **Calendar** — Add and view events\n"
            "🔔 **Reminders** — Set and manage reminders\n"
            "🌤 **Weather** — Current conditions for any city\n"
            "📰 **News** — Top headlines and topic search\n"
            "🕐 **Time** — Current time in any timezone\n"
            "🌐 **Browser** — Open websites and search\n"
            "💻 **Apps** — Launch any installed application\n\n"
            "Simply ask me naturally and I shall take care of it."
        )

    # Default
    defaults = [
        "Understood, sir. Consider it done.",
        "Right away, sir. Is there anything else you need?",
        "Of course. I'll take care of that immediately.",
        "Noted, sir. Anything else I can assist you with?",
        "Very well. Is there anything else on your agenda today?",
    ]
    return random.choice(defaults)