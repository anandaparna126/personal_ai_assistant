@echo off
REM JARVIS AI Assistant - Quick Start Script for Windows

echo.
echo ========================================
echo   🤖 JARVIS AI Assistant
echo   Quick Start Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python नहीं है! | Python not found!
    echo https://python.org से download करो
    pause
    exit /b 1
)

echo ✓ Python found

REM Check if venv folder exists
if not exist "venv" (
    echo.
    echo 🔧 Virtual Environment बना रहे हैं...
    python -m venv venv
    echo ✓ Virtual Environment created
)

REM Activate venv
echo.
echo 🔌 Virtual Environment activate करते हैं...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo 📦 Dependencies install करते हैं...
pip install -r requirements.txt

REM Run migrations
echo.
echo 🗄️ Database setup करते हैं...
python manage.py migrate

REM Collect static
echo.
echo 📁 Static files collect करते हैं...
python manage.py collectstatic --noinput

REM Start server
echo.
echo =========================================
echo ✓ Setup complete!
echo.
echo 🚀 Server start हो रहा है...
echo.
echo 👉 Browser में खोलो: http://localhost:8000
echo.
echo 📖 पूरे setup guide के लिए देखो: SETUP_GUIDE.md
echo =========================================
echo.

python manage.py runserver

pause
