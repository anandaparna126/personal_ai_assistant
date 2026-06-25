#!/bin/bash

# JARVIS AI Assistant - Quick Start Script for macOS/Linux

echo ""
echo "========================================"
echo "  🤖 JARVIS AI Assistant"
echo "  Quick Start Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 नहीं है! | Python3 not found!"
    echo "macOS: brew install python3"
    echo "Linux: sudo apt-get install python3 python3-venv"
    exit 1
fi

echo "✓ Python3 found"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Virtual Environment बना रहे हैं..."
    python3 -m venv venv
    echo "✓ Virtual Environment created"
fi

# Activate venv
echo ""
echo "🔌 Virtual Environment activate करते हैं..."
source venv/bin/activate

# Install requirements
echo ""
echo "📦 Dependencies install करते हैं..."
pip install -r requirements.txt

# Run migrations
echo ""
echo "🗄️ Database setup करते हैं..."
python manage.py migrate

# Collect static
echo ""
echo "📁 Static files collect करते हैं..."
python manage.py collectstatic --noinput

# Start server
echo ""
echo "========================================="
echo "✓ Setup complete!"
echo ""
echo "🚀 Server start हो रहा है..."
echo ""
echo "👉 Browser में खोलो: http://localhost:8000"
echo ""
echo "📖 पूरे setup guide के लिए देखो: SETUP_GUIDE.md"
echo "========================================="
echo ""

python manage.py runserver
