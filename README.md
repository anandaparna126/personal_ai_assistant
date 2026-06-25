# 🤖 JARVIS - Voice-Controlled AI Assistant

**एक personal AI assistant जो आपकी Gmail और Google Calendar को manage करता है - सिर्फ अपनी आवाज़ से!**

---

## ⚡ Quick Start (3 Steps)

### 1️⃣ Clone/Download करो
```bash
# या तो code download करो या
cd jarvis_project
```

### 2️⃣ Setup Script run करो
```bash
# Windows
run.bat

# macOS / Linux
chmod +x run.sh
./run.sh
```

### 3️⃣ Google OAuth Setup करो
- https://console.cloud.google.com पर जाओ
- `credentials.json` download करो
- `jarvis_project/credentials/` में रखो
- `.env` में Groq API key add करो

### 🎉 Done!
```
Browser में: http://localhost:8000
बस "Hey Jarvis" बोलो!
```

---

## 🎤 कमांड Examples

### Gmail
```
"Hey Jarvis, मेरे unread emails पढ़ो"
"Hey Jarvis, John को email भेज - Subject: Project Status"
"Hey Jarvis, 'meeting' के बारे में emails search करो"
```

### Calendar
```
"Hey Jarvis, मेरा calendar दिखाओ"
"Hey Jarvis, कल 3 PM पर meeting का event बना"
"Hey Jarvis, dentist appointment search करो"
```

---

## 📦 Features

✅ **Voice Commands** - "Hey Jarvis" से कमांड दो  
✅ **Gmail Integration** - Read, Send, Search emails  
✅ **Calendar Management** - View, Create, Update, Delete events  
✅ **AI-Powered** - Groq LLM से smart responses  
✅ **Hindi + English** - Hinglish support  
✅ **Offline-Ready** - सब कुछ locally run होता है  

---

## 🛠️ Tech Stack

- **Backend**: Django 4.2
- **LLM**: Groq (Free API)
- **Google APIs**: Gmail & Calendar
- **Frontend**: HTML5, CSS3, JavaScript (Web Speech API)
- **Database**: SQLite (local)

---

## 📖 Full Setup Guide

सभी details के लिए देखो: `SETUP_GUIDE.md`

---

## 🔧 Troubleshooting

**Microphone नहीं काम कर रहा?**
- Browser settings में microphone permission check करो
- Chrome/Firefox में site permissions देखो

**Credentials issue?**
- Google Cloud Console से `credentials.json` फिर से download करो
- `jarvis_project/credentials/` में रखो

**API Key issue?**
- `.env` file में GROQ_API_KEY set है?
- https://console.groq.com पर check करो

---

## 🚀 Usage

### Voice Interface
1. 🎤 बटन पर click करो
2. "Hey Jarvis" बोलो
3. अपनी command बोलो
4. Response सुनो!

### Text Interface
- Text box में type करो
- या 📝 button से text भेज सकते हो

---

## 📁 Project Structure

```
jarvis_project/
├── SETUP_GUIDE.md          ← 👈 पूरी guide
├── requirements.txt        ← Dependencies
├── .env                    ← Configuration
├── manage.py              ← Django command
├── run.bat / run.sh       ← Quick start scripts
├── jarvis/                ← Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── jarvis_app/            ← Main app
│   ├── agent.py           ← AI agent logic
│   ├── gmail_tool.py      ← Gmail operations
│   ├── calendar_tool.py   ← Calendar operations
│   ├── google_auth.py     ← Google OAuth
│   ├── views.py           ← Django views
│   ├── urls.py
│   └── templates/
│       └── index.html     ← Frontend
└── credentials/           ← Google credentials (download करो)
    └── credentials.json
```

---

## 🔒 Security

- ✅ Local execution (सब locally run होता है)
- ✅ OAuth2 authentication (Google से secure)
- ✅ CSRF protection (Django built-in)
- ⚠️ `credentials.json` कभी public न करो
- ⚠️ `.env` को `.gitignore` में रखो

---

## 💡 Advanced

### Custom Wake Word
`.env` में change करो:
```
WAKE_WORD=hello assistant
```

### Change Language
`speech.js` में change करो:
```javascript
recognition.language = 'hi-IN';  // Hindi
recognition.language = 'en-US';  // English
```

### Production Deployment
1. `DEBUG=False` करो settings में
2. Gunicorn या uWSGI use करो
3. HTTPS setup करो
4. Proper database use करो (PostgreSQL)

---

## 🆘 Help

अगर कोई issue हो:
1. `SETUP_GUIDE.md` पढ़ो
2. Browser console (F12) में errors देखो
3. Terminal output check करो
4. Ports available हैं (8000)?

---

## 📝 Features Roadmap

- [ ] WhatsApp integration
- [ ] SMS support
- [ ] Weather alerts
- [ ] News briefing
- [ ] Task management
- [ ] Voice memory (notes)
- [ ] Multi-language support (improved)

---

## 📄 License

Personal use के लिए free! 
Commercial use के लिए permission चाहिए।

---

## 🎯 Made with ❤️

**Aparna का personal AI assistant**

For automation, productivity, and just having fun! 

```
🎤 "Hey Jarvis, सब कुछ ठीक है?" 
✅ "हाँ! सब ready है। कोई कमांड दो!"
```

---

Happy automating! 🚀

**Questions?** Check `SETUP_GUIDE.md` for detailed troubleshooting.
