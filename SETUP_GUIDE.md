# 🤖 JARVIS - Personal AI Assistant Setup Guide

## क्या यह है? | What is this?

JARVIS एक **voice-enabled AI assistant** है जो आपके Gmail और Google Calendar को manage करता है। आप बस **"Hey Jarvis"** कहो और कोई भी command दो!

---

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Google Account (for Gmail & Calendar access)
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## Step 1️⃣ - Google OAuth Setup (सबसे महत्वपूर्ण!)

### 1a. Google Cloud Console में project बनाओ

1. https://console.cloud.google.com/ पर जाओ
2. नया project बनाओ: "JARVIS AI Assistant"
3. लेफ्ट मेन्यू में "APIs & Services" → "OAuth Consent Screen"
4. User Type: "External" चुनो
5. Fill करो:
   - App name: "JARVIS"
   - User support email: आपका email
   - Developer contact: आपका email
6. "Add or remove scopes" में ये scopes add करो:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/calendar`
7. Test users में अपना email add करो

### 1b. OAuth 2.0 Credentials बनाओ

1. "Credentials" → "Create Credentials" → "OAuth client ID"
2. Application type: "Desktop application"
3. Download करो JSON file और save करो

### 1c. credentials.json file place करो

```bash
# Project folder में credentials folder में रखो
jarvis_project/credentials/credentials.json
```

---

## Step 2️⃣ - Project Setup

### Clone या download करो
```bash
# Folder में जाओ जहाँ JARVIS है
cd jarvis_project
```

### Python Virtual Environment बनाओ
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Dependencies install करो
```bash
pip install -r requirements.txt
```

### .env file update करो
```bash
# .env file edit करो
nano .env

# या अपने editor में खोलो
```

Edit करो और यह values set करो:
```
SECRET_KEY=your-super-secret-key-change-this-to-random
DEBUG=True
GROQ_API_KEY=your-groq-api-key-here
WAKE_WORD=hey jarvis
```

### Groq API Key कहाँ से मिलेगी?

1. https://console.groq.com पर जाओ
2. Free account बनाओ
3. API keys section में जाओ
4. Key generate करो और .env में paste करो

---

## Step 3️⃣ - Django Setup

### Database migrate करो
```bash
python manage.py migrate
```

### Static files collect करो
```bash
python manage.py collectstatic --noinput
```

---

## Step 4️⃣ - Run करो! 🚀

```bash
python manage.py runserver
```

**Output होगा कुछ ऐसा:**
```
Starting development server at http://127.0.0.1:8000/
```

### Browser में open करो
```
http://localhost:8000
```

पहली बार Google OAuth popup आएगा - अपना email select करो और allow करो।

---

## 🎤 कमांड्स कैसे दें?

### Voice Commands (सबसे आसान)
```
🎤 "Hey Jarvis, मेरे सभी ईमेल पढ़ो"
🎤 "Hey Jarvis, John को email भेज - Subject: Meeting"
🎤 "Hey Jarvis, मेरे सप्ताह के events दिखाओ"
🎤 "Hey Jarvis, कल 3 PM पर meeting का event बना"
```

### Text Commands (माइक्रोफ़ोन न हो तो)
सीधे text box में type करो:
```
"Read my emails"
"Send email to aparna@example.com about project status"
"Show calendar events for next 10 days"
"Create event tomorrow at 2 PM for dentist appointment"
```

---

## 📧 Gmail Commands

```
✉️ "Read my emails"
✉️ "Show unread emails"
✉️ "Search emails from john@example.com"
✉️ "Send email to [email] - Subject: [subject] - Body: [message]"
✉️ "Search emails about 'meeting'"
```

---

## 📅 Calendar Commands

```
📅 "Show my events"
📅 "What's on my calendar tomorrow?"
📅 "Show events for next 14 days"
📅 "Create event 'Project meeting' on 2024-01-20 at 10:00 AM"
📅 "Search for 'dentist' appointment"
📅 "Delete the meeting at 3 PM"
```

---

## ⚙️ Settings

Browser में settings button दबाओ:
- ✅ Auto-play voice response
- ✅ Show voice transcript
- Change wake word (अभी "Hey Jarvis" है)

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'google'"
```bash
# Dependencies फिर से install करो
pip install -r requirements.txt
```

### "Microphone permission denied"
- Browser settings में microphone permission check करो
- Chrome: Padlock icon → Site settings → Microphone

### "credentials.json not found"
- Google Cloud Console से JSON download करो
- `jarvis_project/credentials/` में रखो (folder नहीं दिख तो बनाओ)

### "GROQ_API_KEY not set"
- https://console.groq.com पर जाओ
- API key generate करो
- .env file में paste करो

### "Google OAuth screen appears but doesn't work"
- Google Cloud Console में redirect URI check करो
- आमतौर पर `http://localhost:8000` होना चाहिए

---

## 📁 Project Structure

```
jarvis_project/
├── manage.py
├── requirements.txt
├── .env
├── db.sqlite3
├── jarvis/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── jarvis_app/
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── app.js
│   │       └── speech.js
│   ├── views.py
│   ├── urls.py
│   ├── agent.py
│   ├── gmail_tool.py
│   ├── calendar_tool.py
│   ├── google_auth.py
│   └── apps.py
└── credentials/
    ├── credentials.json (download करो Google से)
    └── token.json (auto-generated)
```

---

## 🎯 Advanced Usage

### Custom Wake Word

`.env` में change करो:
```
WAKE_WORD=namaste jarvis
```

या
```
WAKE_WORD=jarvis hello
```

---

## 🐛 Debug Mode

Logs देखने के लिए:

```bash
# Terminal में देखो - सभी commands print होंगे
# Browser console (F12) देखो - client-side logs
```

---

## 🔒 Security Notes

- `credentials.json` **कभी** public/GitHub पर upload न करो
- `.env` file को `.gitignore` में रखो
- `SECRET_KEY` production में random value set करो
- `DEBUG=False` करो deployment पर

---

## Production Deployment (Optional)

### Heroku पर deploy करने के लिए:

1. `Procfile` बनाओ:
```
web: gunicorn jarvis.wsgi
```

2. Requirements update करो:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. Heroku account बनाओ और deploy करो

---

## 🆘 Help & Support

अगर कोई issue आए:

1. सभी steps फिर से check करो (specially Google OAuth)
2. Terminal में clear output copy करो
3. Browser console (F12) में errors देखो
4. Ports check करो - 8000 free होना चाहिए

---

## 🎉 Done!

अब आप JARVIS को अपना voice assistant बना सकते हो!

```
"Hey Jarvis, tell me a joke" 😄
```

Happy automation! 🚀

---

**Made with ❤️ for personal productivity**
