# Alfred — Personal AI Operating Assistant

> A portfolio-grade agentic AI assistant: voice output, real tool-calling, persistent memory, and a live agent trace panel.

## Stack
- **Backend**: Python Flask + Flask-SocketIO
- **Agent**: LangGraph + Mistral AI (function calling)
- **Memory**: PostgreSQL + pgvector (Supabase/Neon)
- **Frontend**: React 18 + Vite
- **Scheduler**: APScheduler
- **Deployment**: Railway (backend) + Vercel (frontend)

## Features (v1)
- Conversational chat with streaming responses
- Tool calling: Email, Calendar, Personal Data, Reminders
- Persistent memory with vector similarity recall
- Agent trace panel showing reasoning steps in real time
- Text-to-speech on every assistant reply (browser SpeechSynthesis)
- Proactive notifications via background scheduler

## Status
?? Phase 1 in progress — Core Brain + Voice Output
