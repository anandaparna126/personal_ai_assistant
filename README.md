# JARVIS - Personal AI Assistant

Voice-controlled AI assistant for Gmail and Google Calendar.

## Setup

```bash
git clone https://github.com/anandaparna126/personal_ai_assistant.git
cd jarvis_project
pip install -r requirements.txt
```

Add a `.env` file:
```
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
```

Get Google credentials from [console.cloud.google.com](https://console.cloud.google.com), download `credentials.json` and place it in `credentials/`.

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://localhost:8000`

## Commands

```
"read my emails"
"send email to john@example.com about the meeting"
"show my calendar"
"schedule a meeting tomorrow at 3pm"
```

## Stack

- Django 4.2 + SQLite
- Gemini 2.0 Flash (free)
- Gmail & Google Calendar API
- Web Speech API

## Notes

- Never push `.env` or `credentials/` to GitHub
- First run will open a Google OAuth browser window