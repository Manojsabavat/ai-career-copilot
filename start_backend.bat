@echo off
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo Create the virtual environment and install requirements first:
  echo python -m venv .venv
  echo .venv\Scripts\activate
  echo pip install -r requirements.txt
  pause
  exit /b 1
)
call .venv\Scripts\activate
python -m uvicorn main:app --reload
