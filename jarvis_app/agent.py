import json
import logging
from datetime import datetime
import pytz
from google import genai
from google.genai import types
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

client = genai.Client(api_key=settings.GEMINI_API_KEY)
IST = pytz.timezone('Asia/Kolkata')

# ── Tool definitions (new SDK format) ───────────────────────────────────────

TOOLS_DEFINITION = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="read_emails",
            description="Read up to 5 unread emails from Gmail inbox",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="send_email",
            description="Send an email",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "to":      types.Schema(type=types.Type.STRING, description="Recipient email address"),
                    "subject": types.Schema(type=types.Type.STRING, description="Email subject"),
                    "body":    types.Schema(type=types.Type.STRING, description="Email content"),
                },
                required=["to", "subject", "body"]
            )
        ),
        types.FunctionDeclaration(
            name="search_emails",
            description="Search emails by query (e.g. 'from:john@example.com')",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING, description="Search query")
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="list_events",
            description="List upcoming calendar events for the next 7 days",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="create_event",
            description="Create a new calendar event",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "title":       types.Schema(type=types.Type.STRING, description="Event title"),
                    "start_time":  types.Schema(type=types.Type.STRING, description="Start time ISO format e.g. 2024-01-15T10:00:00"),
                    "end_time":    types.Schema(type=types.Type.STRING, description="End time ISO format"),
                    "description": types.Schema(type=types.Type.STRING, description="Event description (optional)"),
                },
                required=["title", "start_time", "end_time"]
            )
        ),
        types.FunctionDeclaration(
            name="search_events",
            description="Search calendar events by title or keyword",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING, description="Search query")
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="delete_event",
            description="Delete a calendar event",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "event_id": types.Schema(type=types.Type.STRING, description="ID of the event to delete")
                },
                required=["event_id"]
            )
        ),
    ])
]

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
    """Process user command using Gemini 2.0 Flash (new google-genai SDK)"""

    if conversation_history is None:
        conversation_history = []

    today = datetime.now(IST).strftime('%Y-%m-%d')

    system_prompt = f"""You are JARVIS, a highly intelligent personal AI assistant created exclusively for Aparna. You have access to her Gmail and Google Calendar.

CORE BEHAVIOR:
- Execute tasks immediately without asking for confirmation unless action is irreversible (like deleting)
- Chain multiple actions automatically when needed

LANGUAGE:
- Respond in English, short and friendly

ABOUT APARNA:
- Developer — sharp, busy, doesn't like repeating herself
- Prefers things done first, explained later briefly
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
        # Build contents from history + new message
        contents = []
        for msg in conversation_history:
            if msg["role"] == "user" and isinstance(msg["content"], str):
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=msg["content"])]
                ))
            elif msg["role"] == "assistant" and isinstance(msg["content"], str):
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=msg["content"])]
                ))

        # Add current user message
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        ))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=TOOLS_DEFINITION,
        )

        # First call
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )

        actions = []

        # Check for function calls
        function_calls = []
        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_calls.append(part.function_call)

        if not function_calls:
            assistant_text = response.text
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": assistant_text})
            return {
                "response": assistant_text,
                "history": conversation_history,
                "actions": []
            }

        # Add assistant's tool_call turn to contents
        contents.append(response.candidates[0].content)

        # Execute tools and build function responses
        function_response_parts = []
        for fc in function_calls:
            tool_name = fc.name
            tool_input = dict(fc.args)

            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
            result = execute_tool(tool_name, tool_input)

            actions.append({"tool": tool_name, "input": tool_input, "result": result})

            function_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=tool_name,
                        response={"result": json.dumps(result)}
                    )
                )
            )

        # Add tool results to contents
        contents.append(types.Content(role="user", parts=function_response_parts))

        # Second call — final response
        final_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )

        final_text = final_response.text

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