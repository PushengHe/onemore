@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
	echo Python was not found. Please install Python 3.10 or newer and add it to PATH.
	echo Download: https://www.python.org/downloads/
	pause
	exit /b 1
)
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if errorlevel 1 (
	echo A working Python 3.10 or newer installation is required.
	echo Download: https://www.python.org/downloads/
	pause
	exit /b 1
)
python -c "import ctypes; ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)"
python main.py
if errorlevel 1 (
	python -c "import ctypes; ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 5)"
	pause
)