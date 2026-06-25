import json
import logging
from datetime import datetime
import pytz
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from django.conf import settings
from .gmail_tool import (
    read_emails, send_email, search_emails,
    mark_as_read, delete_email
)
from .calendar_tool import (
    list_events, create_event, update_event,
    delete_event, search_events
)

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
IST = pytz.timezone('Asia/Kolkata')

# ── Gemini tool definitions ──────────────────────────────────────────────────

read_emails_fn = FunctionDeclaration(
    name="read_emails",
    description="Read up to 5 unread emails from Gmail inbox",
    parameters={"type": "object", "properties": {}}
)

send_email_fn = FunctionDeclaration(
    name="send_email",
    description="Send an email",
    parameters={
        "type": "object",
        "properties": {
            "to":      {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body":    {"type": "string", "description": "Email content"},
        },
        "required": ["to", "subject", "body"]
    }
)

search_emails_fn = FunctionDeclaration(
    name="search_emails",
    description="Search emails by query (e.g. 'from:john@example.com', 'subject:meeting')",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    }
)

list_events_fn = FunctionDeclaration(
    name="list_events",
    description="List upcoming calendar events for the next 7 days",
    parameters={"type": "object", "properties": {}}
)

create_event_fn = FunctionDeclaration(
    name="create_event",
    description="Create a new calendar event",
    parameters={
        "type": "object",
        "properties": {
            "title":       {"type": "string", "description": "Event title"},
            "start_time":  {"type": "string", "description": "Start time in ISO format (e.g. 2024-01-15T10:00:00)"},
            "end_time":    {"type": "string", "description": "End time in ISO format"},
            "description": {"type": "string", "description": "Event description (optional)"},
        },
        "required": ["title", "start_time", "end_time"]
    }
)

search_events_fn = FunctionDeclaration(
    name="search_events",
    description="Search calendar events by title or keyword",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    }
)

delete_event_fn = FunctionDeclaration(
    name="delete_event",
    description="Delete a calendar event",
    parameters={
        "type": "object",
        "properties": {
            "event_id": {"type": "string", "description": "ID of the event to delete"}
        },
        "required": ["event_id"]
    }
)

TOOLS = Tool(function_declarations=[
    read_emails_fn, send_email_fn, search_emails_fn,
    list_events_fn, create_event_fn, search_events_fn, delete_event_fn
])

# ── Tool executor ────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict):
    if tool_name == "read_emails":
        return read_emails(5)
    elif tool_name == "send_email":
        return send_email(tool_input['to'], tool_input['subject'], tool_input['body'])
    elif tool_name == "search_emails":
        return search_emails(tool_input['query'], 5)
    elif tool_name == "list_events":
        return list_events(7)
    elif tool_name == "create_event":
        return create_event(
            tool_input['title'],
            tool_input['start_time'],
            tool_input['end_time'],
            tool_input.get('description', '')
        )
    elif tool_name == "search_events":
        return search_events(tool_input['query'])
    elif tool_name == "delete_event":
        return delete_event(tool_input['event_id'])
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

# ── Main process function ────────────────────────────────────────────────────

def process_command(user_message: str, conversation_history: list = None):
    """Process user command and return response using Gemini 2.0 Flash"""

    if conversation_history is None:
        conversation_history = []

    today = datetime.now(IST).strftime('%Y-%m-%d')

    system_prompt = f"""You are JARVIS, a highly intelligent personal AI assistant created exclusively for Aparna. You have access to her Gmail and Google Calendar.

CORE BEHAVIOR:
- Execute tasks immediately without asking for confirmation unless the action is irreversible (like deleting)
- Chain multiple actions automatically when needed

LANGUAGE:
- Respond in English, short and friendly

ABOUT APARNA:
- She is a developer — sharp, busy, doesn't like repeating herself
- Prefers things done first, explained later (briefly)
- If she seems stressed, acknowledge it warmly before helping

DATE & TIME:
- Today is {today}, timezone Asia/Kolkata (IST, UTC+5:30)
- "tomorrow" = next day in IST
- "evening" = 6 PM, "morning" = 9 AM, "afternoon" = 2 PM (defaults)
- Always use complete ISO datetime for tool calls

CALENDAR:
- Always add Google Meet link for meeting/interview/call events
- Default duration = 1 hour
- Show Meet link clearly after creating"""

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt,
            tools=[TOOLS]
        )

        # Convert stored history to Gemini format
        gemini_history = []
        for msg in conversation_history:
            if msg["role"] == "user" and isinstance(msg["content"], str):
                gemini_history.append({
                    "role": "user",
                    "parts": [{"text": msg["content"]}]
                })
            elif msg["role"] == "assistant" and isinstance(msg["content"], str):
                gemini_history.append({
                    "role": "model",
                    "parts": [{"text": msg["content"]}]
                })

        # Start chat with history
        chat = model.start_chat(history=gemini_history)

        # Send current message
        response = chat.send_message(user_message)

        actions = []

        # Check for function calls
        function_calls = []
        for part in response.parts:
            if hasattr(part, 'function_call') and part.function_call.name:
                function_calls.append(part.function_call)

        if not function_calls:
            # Direct text reply
            assistant_text = response.text

            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": assistant_text})

            return {
                "response": assistant_text,
                "history": conversation_history,
                "actions": []
            }

        # Execute all tool calls
        function_responses = []
        for fc in function_calls:
            tool_name = fc.name
            tool_input = dict(fc.args)

            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

            result = execute_tool(tool_name, tool_input)

            actions.append({
                "tool": tool_name,
                "input": tool_input,
                "result": result
            })

            function_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": json.dumps(result)}
                    )
                )
            )

        # Send tool results back to get final response
        final_response = chat.send_message(function_responses)
        final_text = final_response.text

        # Save to history
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": final_text})

        return {
            "response": final_text,
            "history": conversation_history,
            "actions": actions
        }

    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        error_response = f"Kuch error aa gayi 😕 | {str(e)}"
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": error_response})
        return {"response": error_response, "history": conversation_history, "actions": []}