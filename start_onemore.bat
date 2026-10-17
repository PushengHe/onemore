@echo off
cd /d "%~dp0"
set "PYTHON=%~1"

"%PYTHON%" -c "import ctypes; ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)"
"%PYTHON%" main.py
if errorlevel 1 (
	"%PYTHON%" -c "import ctypes; ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)"
	pause
)