@echo off
set BASE=C:\Users\maazk\Desktop\Alfred-Personal-Assistant\backend
set PYTHON=C:\Users\maazk\Desktop\Alfred-Personal-Assistant\backend\venv\Scripts\pythonw.exe
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo Creating Alfred Clap Listener shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP%\Alfred-Clap-Listener.lnk'); $s.TargetPath = '%PYTHON%'; $s.Arguments = '%BASE%\clap_listener.py'; $s.WorkingDirectory = '%BASE%'; $s.WindowStyle = 7; $s.Save()"

echo Creating Alfred Tray shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP%\Alfred-Tray.lnk'); $s.TargetPath = '%PYTHON%'; $s.Arguments = '%BASE%\tray.py'; $s.WorkingDirectory = '%BASE%'; $s.WindowStyle = 7; $s.Save()"

echo Done. Both Alfred clap listener and tray icon will start on boot.
pause