@echo off
title Alfred - Personal AI Assistant
echo.
echo  ╔═══════════════════════════════════════╗
echo  ║        ALFRED - AI ASSISTANT          ║
echo  ║         Initializing systems...       ║
echo  ╚═══════════════════════════════════════╝
echo.

:: Start backend
start "Alfred Backend" cmd /k "cd /d C:\Users\maazk\Desktop\Alfred-Personal-Assistant\backend && call venv\Scripts\activate.bat && python run.py"

:: Wait for backend + DB pool warmup
echo  Waiting for backend to initialize...
timeout /t 6 /nobreak > nul

:: Start frontend
start "Alfred Frontend" cmd /k "cd /d C:\Users\maazk\Desktop\Alfred-Personal-Assistant\frontend && npm run dev"

:: Wait for Vite to compile
echo  Waiting for frontend to compile...
timeout /t 4 /nobreak > nul

:: Open browser
start http://localhost:5173

echo.
echo  Alfred is ready.
pause