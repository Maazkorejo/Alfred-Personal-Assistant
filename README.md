# Alfred — Personal AI Operating Assistant

> A portfolio-grade agentic AI assistant inspired by Batman's butler. Built with real tool-calling, persistent memory, Piper TTS voice output, and a Batman-themed React UI.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey) ![React](https://img.shields.io/badge/React-18-61dafb) ![Mistral](https://img.shields.io/badge/LLM-Mistral_AI-orange) ![Supabase](https://img.shields.io/badge/DB-Supabase_PostgreSQL-green)

## Stack

- **Backend**: Python Flask, custom two-LLM-call agentic loop
- **LLM**: Mistral AI (`mistral-large-latest`)
- **Memory**: Supabase PostgreSQL with SQLAlchemy connection pooling
- **Frontend**: React 18 + Vite, Batman-themed with animated black hole canvas
- **Voice Output**: Piper TTS (local, offline) — `en_GB-alan-medium`
- **Voice Input**: Web Speech API (browser STT)
- **Wake Mechanic**: Double-clap detection via FFT spectral analysis (sounddevice)

## Features

- **Conversational chat** with persistent session-based memory
- **Real tool-calling** via custom regex-based function dispatch:
  - Gmail (IMAP) — read, search, count emails
  - Weather — OpenWeatherMap
  - News — NewsAPI
  - Time/timezone — pytz
  - Browser control — open websites, YouTube search
  - App launcher — any installed Windows app including UWP/Store apps
  - File/folder opener
- **Piper TTS voice output** — local, free, fast British butler voice
- **Speech-to-text input** — browser Web Speech API
- **Double-clap wake** — spectral FFT analysis distinguishes claps from speech/coughs
- **Chat history** — session management with past conversation browser
- **Memory panel** — view and clear conversation history
- **Email panel** — browse inbox without chat

## Architecture

Alfred uses a two-LLM-call pattern (no native tool-calling SDK):
User message

↓

Mistral call #1  →  detects TOOL:name:argument via regex

↓

Python executes real tool function

↓

Mistral call #2  →  natural language reply using tool result

↓

Response + Piper TTS audio

## Project Structure
backend/

app/

routes/          # chat, emails, memory, tts endpoints

agent/

mistral_client.py

tts_service.py

tools/         # gmail, weather, news, time, browser, app launcher

memory/db.py     # SQLAlchemy pooled connection, session management

clap_listener.py   # standalone double-clap wake script

frontend/

src/

hooks/           # useAlfred.js (state), useSpeechRecognition.js

components/      # BlackHole, Sidebar, ChatLog, EmailPanel, MemoryPanel, ChatHistoryPanel

## Setup

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the `backend/` folder:
MISTRAL_API_KEY=your_key

DATABASE_URL=your_supabase_url

GMAIL_ADDRESS=your@gmail.com

GMAIL_APP_PASSWORD=your_app_password

NEWS_API_KEY=your_key

WEATHER_API_KEY=your_key

```powershell
python run.py
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Clap-to-wake (optional, separate terminal)

```powershell
cd backend
venv\Scripts\activate
python clap_listener.py
```

## Status

✅ Phase 1 — Core chat + memory  
✅ Phase 2 — Gmail, Weather, News, Time, Browser, App Launcher  
✅ Voice I/O — Piper TTS + Web Speech API  
✅ Clap-to-wake  
✅ Chat history with session management  
🔲 Calendar (local Supabase, planned)  
🔲 Reminders/Tasks  
🔲 Deployment (Railway + Vercel)