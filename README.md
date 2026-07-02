<div align="center">

```
░█████╗░██╗░░░░░███████╗██████╗░███████╗██████╗░
██╔══██╗██║░░░░░██╔════╝██╔══██╗██╔════╝██╔══██╗
███████║██║░░░░░█████╗░░██████╔╝█████╗░░██║░░██║
██╔══██║██║░░░░░██╔══╝░░██╔══██╗██╔══╝░░██║░░██║
██║░░██║███████╗██║░░░░░██║░░██║███████╗██████╔╝
╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚═════╝░
```

### *"Not all heroes wear capes. Some deploy Flask."*

**A portfolio-grade personal AI operating assistant inspired by Batman's butler.**  
**Real tool-calling. Persistent memory. Voice I/O. Batman-themed UI.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Mistral AI](https://img.shields.io/badge/Mistral_AI-Large-FF7000?style=for-the-badge)](https://mistral.ai)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Deployed on Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![Deployed on Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.app)

<br/>

[🌐 **Live Demo**](https://alfred-personal-assistant.vercel.app) &nbsp;·&nbsp;
[📁 **GitHub**](https://github.com/Maazkorejo/Alfred-Personal-Assistant) &nbsp;·&nbsp;
[🎥 **Demo Video**](#)

</div>

---

## 🦇 What is Alfred?

Alfred is not a chatbot wrapper. It is a **fully agentic AI operating assistant** that manages real tasks through natural conversation — reading your actual emails, managing your calendar, setting reminders that fire real notifications, controlling your desktop apps, and speaking back responses in a custom British butler voice.

Built entirely from scratch as a **portfolio-grade engineering project** to demonstrate agentic AI design, full-stack integration, prompt engineering, and production deployment — using only free-tier services.

> **Two versions exist:**  
> 🏠 **Local (full)** — runs on my machine, connected to real Gmail, real calendar, real reminders, real voice  
> 🌐 **Demo (public)** — deployed live with mock data so recruiters can experience the UI and conversation flow without exposing personal data

---

## 🎯 Features

### 🤖 Agentic Chat
Natural conversation powered by Mistral AI. Alfred understands intent, decides which tool to use, executes it, and responds naturally — without you needing to use specific commands.

### 📧 Email (Gmail via IMAP)
> *"Alfred, do I have any unread emails?"*  
> *"Show me emails from ali@example.com"*

- Read unread and recent inbox emails
- Search by subject keyword or sender email
- Count unread messages
- No Google OAuth required — uses Gmail App Password (100% free)

### 📅 Calendar
> *"Add a meeting tomorrow at 3pm"*  
> *"What's on my calendar this week?"*

- Add events with titles, times, descriptions
- View today's events or upcoming events by date range
- Delete events by ID
- Search calendar by keyword
- Full calendar panel UI with monthly grid view

### 🔔 Reminders
> *"Remind me to call Ali in 30 minutes"*  
> *"Show my pending reminders"*

- Set reminders with natural language time parsing ("in 30 minutes", "tomorrow at 9am")
- Background checker fires Windows toast notifications when reminders are due
- Mark reminders complete or delete them via chat or UI panel
- Never fires the same reminder twice (tracks `notified` state in DB)

### 🌤 Weather
> *"What's the weather in Karachi?"*

- Real-time weather via OpenWeatherMap
- Temperature, condition, humidity, wind speed

### 📰 News
> *"Show me tech headlines"*  
> *"Search news about AI"*

- Top headlines by category (technology, sports, business, general)
- Worldwide keyword search via NewsAPI

### 🕐 Time & Timezone
> *"What time is it in Tokyo?"*

- Current time and date for any city worldwide
- Powered by `pytz` with full timezone support

### 🌐 Browser Control
> *"Open YouTube"*  
> *"Search for Python tutorials"*

- Opens websites, YouTube searches, Google queries
- Smart routing (known sites → direct URL, unknown → Google search)

### 💻 App Launcher
> *"Open Spotify"*  
> *"Launch VS Code"*

- Launches any installed Windows app including UWP/Store apps (LinkedIn, Xbox, etc.)
- Dynamic discovery via PowerShell `Get-StartApps` — no hardcoded app list needed

### 📂 File & Folder Opener
> *"Open my Desktop folder"*  
> *"Open C:\Users\maazk\Documents\report.pdf"*

- Opens any file or folder by absolute path via `os.startfile`

### 🎙 Voice I/O
- **Speech output:** Piper TTS (local, offline, free) — British butler voice (`en_GB-alan-medium`)
- **Speech input:** Browser Web Speech API (no backend required)
- Automatic fallback to browser TTS if Piper is unavailable

### 👏 Clap-to-Wake
- Listens to microphone continuously via `sounddevice`
- **Real spectral analysis** (FFT) to distinguish claps from speech/coughs:
  - Claps: broadband high-frequency energy burst (>3kHz ratio), near-instant attack (<5ms)
  - Speech/coughs: vocal resonance-dominated, mostly <3kHz, slower onset
- Double clap → Alfred focuses existing window or launches everything if not running

### 🧠 Persistent Memory
- Every conversation stored in Supabase PostgreSQL
- Session-based history (each "New Chat" gets its own UUID session)
- Memory panel shows full history with stats
- Chat History panel lets you browse and reload past conversations
- Clear all memory with confirmation step

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER INPUT                        │
│            (text or voice via STT)                  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              FLASK BACKEND (Python)                 │
│                                                     │
│  1. Load conversation history from Postgres         │
│  2. Build prompt with CURRENT DATE/TIME injected    │
│  3. Mistral call #1 → detects TOOL:name:argument    │
│  4. Python executes real tool function              │
│  5. Mistral call #2 → natural language reply        │
│  6. Save messages to Postgres (parallel threads)    │
└─────────────────────┬───────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌─────────────────┐    ┌──────────────────────┐
│   TOOL LAYER    │    │   PIPER TTS SERVICE  │
│                 │    │                      │
│ • Gmail IMAP    │    │ Generates .wav file  │
│ • OpenWeather   │    │ Served via /api/tts  │
│ • NewsAPI       │    │ Played in browser    │
│ • pytz time     │    └──────────────────────┘
│ • Browser ctrl  │
│ • App launcher  │
│ • Calendar DB   │
│ • Reminders DB  │
└─────────────────┘
```

### Two-LLM-Call Pattern
Alfred uses a **custom regex-based tool-calling system** rather than native Mistral tool-calling — built from scratch to understand agentic patterns at the implementation level:

```
User message + history
        ↓
  Mistral call #1
        ↓
  Response matches TOOL:name:argument ?
        ↓ YES                    ↓ NO
Python executes tool      Return response directly
        ↓
  Tool result injected
        ↓
  Mistral call #2
        ↓
  Natural language reply
        ↓
  Piper TTS → Audio response
```

---

## 🗂 Project Structure

```
Alfred-Personal-Assistant/
│
├── backend/
│   ├── run.py                          # Flask app entry point
│   ├── requirements.txt                # Python dependencies
│   ├── Procfile                        # Gunicorn start command
│   ├── Dockerfile                      # Docker build for deployment
│   ├── clap_listener.py                # Clap-to-wake (spectral FFT v3)
│   ├── tray.py                         # System tray icon launcher
│   ├── add_to_startup.bat              # Adds tray + clap to Windows startup
│   │
│   └── app/
│       ├── __init__.py                 # App factory, blueprint registration
│       ├── config.py                   # Flask config (dev/prod)
│       ├── reminder_checker.py         # Background reminder notification thread
│       │
│       ├── routes/
│       │   ├── chat.py                 # Main agent endpoint + tool dispatch
│       │   ├── emails.py               # Email panel REST API
│       │   ├── calendar.py             # Calendar REST API
│       │   ├── reminders.py            # Reminders REST API
│       │   ├── memory.py               # History + session REST API
│       │   ├── tts.py                  # TTS generate + serve audio
│       │   ├── spotify.py              # Spotify OAuth + playback (WIP)
│       │   └── health.py               # Health check endpoint
│       │
│       ├── agent/
│       │   ├── mistral_client.py       # Mistral API wrapper
│       │   ├── tts_service.py          # Piper TTS subprocess + audio management
│       │   ├── demo_responses.py       # Mock responses for demo mode
│       │   │
│       │   └── tools/
│       │       ├── gmail_tool.py       # IMAP email operations
│       │       ├── weather_tool.py     # OpenWeatherMap API
│       │       ├── news_tool.py        # NewsAPI headlines + search
│       │       ├── time_tool.py        # pytz timezone lookup
│       │       ├── system_tool.py      # Browser/URL control
│       │       ├── app_launcher_tool.py # Windows app launching
│       │       ├── calendar_tool.py    # Supabase calendar operations
│       │       ├── reminder_tool.py    # Supabase reminder operations
│       │       └── spotify_tool.py     # Spotify Web API (WIP)
│       │
│       └── memory/
│           └── db.py                   # SQLAlchemy pooled engine + all DB functions
│
├── frontend/
│   └── src/
│       ├── App.jsx                     # Root component, panel routing
│       ├── config.js                   # Centralized API URL (env-var driven)
│       │
│       ├── hooks/
│       │   ├── useAlfred.js            # Central state, sendMessage, TTS, session
│       │   └── useSpeechRecognition.js # Browser STT wrapper
│       │
│       └── components/
│           ├── BlackHole.jsx           # Animated canvas centerpiece
│           ├── Sidebar.jsx             # Nav with state pill
│           ├── TopBar.jsx              # Mic button + status
│           ├── InputBar.jsx            # Chat input
│           ├── ChatLog.jsx             # Message renderer (react-markdown)
│           ├── EmailPanel.jsx          # Inbox browser UI
│           ├── CalendarPanel.jsx       # Monthly grid + event management
│           ├── RemindersPanel.jsx      # Reminder list + add form
│           ├── MemoryPanel.jsx         # History viewer + clear
│           └── ChatHistoryPanel.jsx    # Session browser + loader
│
├── start_alfred.bat                    # One-click local launcher
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Mistral AI (`mistral-large-latest`) | Cost-effective, strong instruction following |
| Backend | Python Flask | Lightweight, easy blueprint architecture |
| Database | Supabase PostgreSQL | Free hosted Postgres, no infra management |
| ORM | SQLAlchemy + connection pooling | Singleton engine pattern for low latency |
| Frontend | React 18 + Vite | Fast dev, component-based UI |
| Voice Output | Piper TTS (local) | Free, offline, fast, natural voice |
| Voice Input | Web Speech API | Zero cost, browser-native |
| Email | Gmail IMAP + App Password | Avoids Google OAuth billing requirement |
| Weather | OpenWeatherMap Free Tier | Reliable, free |
| News | NewsAPI Free Tier | Global headlines + keyword search |
| Wake Detection | sounddevice + numpy FFT | Custom spectral analysis, no cloud needed |
| Deployment | Railway (backend) + Vercel (frontend) | Free tiers, GitHub-connected |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Supabase account (free)
- Mistral AI API key (free tier available)

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
MISTRAL_API_KEY=your_mistral_key
DATABASE_URL=your_supabase_postgresql_url
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweathermap_key
FRONTEND_URL=http://localhost:5173
SECRET_KEY=any-random-secret
```

```powershell
python run.py
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### One-click Start (Windows)

Double-click `start_alfred.bat` from the project root — opens both terminals and launches the browser automatically.

### Supabase Tables

Run these in your Supabase SQL Editor:

```sql
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    session_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE alfred_calendar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    due_at TIMESTAMPTZ NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reminders_due_at ON reminders (due_at);
CREATE INDEX idx_reminders_completed ON reminders (completed);
```

---

## 🌐 Demo Deployment

The public demo runs in `DEMO_MODE=true` with mocked responses — no real credentials needed.

| Service | Platform | Branch |
|---------|----------|--------|
| Backend | Railway (Dockerfile) | `demo` |
| Frontend | Vercel | `demo` |

Demo limitations vs local version:
- ❌ No real Gmail access (mock email data)
- ❌ No Piper TTS (falls back to browser TTS)
- ❌ No reminder notifications
- ❌ No desktop app/file control
- ✅ Full UI, animations, all panels visible
- ✅ Realistic Alfred butler conversation responses
- ✅ Calendar and Reminder panels browseable

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Git commits | 70+ granular commits |
| Backend files | 20+ Python modules |
| Frontend components | 10+ React components |
| Tools integrated | 14 callable tools |
| Lines of code | ~3,500+ |
| APIs used | Mistral, Gmail IMAP, OpenWeatherMap, NewsAPI, Supabase |
| Cost to run | ~$0/month (all free tiers) |

---

## 🗺 Roadmap

- [x] Core chat with persistent memory.
- [x] Gmail integration (IMAP)
- [x] Weather, News, Time tools
- [x] Browser and app control
- [x] Piper TTS voice output
- [x] Web Speech API input
- [x] Clap-to-wake (FFT spectral detection)
- [x] Calendar (Supabase)
- [x] Reminders with background notifications
- [x] Chat history with session management
- [x] Demo mode for public deployment
- [x] Railway + Vercel deployment
- [ ] Spotify playback control (OAuth blocked, WIP)
- [ ] Wake word detection ("Hey Alfred")
- [ ] Recurring reminders
- [ ] Email compose and reply

---

## 👨‍💻 Built By

**Muhammad Maaz Korejo**  
3rd-year BS IT student, Pakistan  
Aspiring AI Developer / Backend Engineer

[![GitHub](https://img.shields.io/badge/GitHub-Maazkorejo-181717?style=for-the-badge&logo=github)](https://github.com/Maazkorejo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/your-profile)

---

<div align="center">

*"The strength of Batman is not the suit. It's Alfred."*

⭐ **Star this repo if Alfred impressed you** ⭐

</div>