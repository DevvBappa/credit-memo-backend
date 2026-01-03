@echo off
echo Starting Credit Memo Backend Server...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python main.py
pause
