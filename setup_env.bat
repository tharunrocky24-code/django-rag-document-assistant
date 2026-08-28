@echo off
title Django RAG - Setup Environment & Dependencies
echo =========================================================
echo   Setting up Django RAG Environment (Groq + ChromaDB)
echo =========================================================

cd /d "%~dp0\backend"

IF NOT EXIST "venv" (
    echo Creating virtual environment (venv)...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing all required dependencies from requirements.txt...
pip install -r requirements.txt

echo Running Django migrations...
python manage.py makemigrations accounts documents chat
python manage.py migrate

echo.
echo =========================================================
echo   Setup Complete!
echo   Run 'run_server.bat' to start the application.
echo =========================================================
echo.
pause
