@echo off
title Django RAG Assistant - Groq & ChromaDB Server
echo ===================================================
echo   Starting Django RAG Application (Groq + ChromaDB)
echo ===================================================

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running database migrations...
python manage.py migrate --noinput

echo.
echo ===================================================
echo   RAG Application is running at:
echo   http://127.0.0.1:8000/
echo   http://127.0.0.1:8000/chat/
echo   http://127.0.0.1:8000/documents/
echo   http://127.0.0.1:8000/dashboard/
echo ===================================================
echo.

python manage.py runserver 127.0.0.1:8000
pause
