@echo off
set SCRIPT_PATH=C:\Users\maazk\Desktop\Alfred-Personal-Assistant\backend\clap_listener.py
set PYTHON_PATH=C:\Users\maazk\Desktop\Alfred-Personal-Assistant\backend\venv\Scripts\pythonw.exe
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo Creating Alfred startup shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_DIR%\Alfred-Clap-Listener.lnk'); $s.TargetPath = '%PYTHON_PATH%'; $s.Arguments = '%SCRIPT_PATH%'; $s.WorkingDirectory = 'C:\Users\maazk\Desktop\Alfred-Personal-Assistant\backend'; $s.WindowStyle = 7; $s.Save()"
echo Done. Alfred clap listener will start automatically on boot.
pause