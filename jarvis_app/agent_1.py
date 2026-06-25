import json
import logging
from datetime import datetime
import pytz
from django.conf import settings
from groq import Groq
from .gmail_tool import (
    read_emails, send_email, search_emails, 
    mark_as_read, delete_email
)
from .calendar_tool import (
    list_events, create_event, update_event, 
    delete_event, search_events
)

logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)
IST = pytz.timezone('Asia/Kolkata')

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Read up to 5 unread emails from Gmail inbox",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email content"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Search emails by query (e.g., 'from:john@example.com', 'subject:meeting')",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_events",
            "description": "List upcoming calendar events for the next 7 days",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Create a new calendar event",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "start_time": {"type": "string", "description": "Start time in ISO format (e.g., 2024-01-15T10:00:00)"},
                    "end_time": {"type": "string", "description": "End time in ISO format"},
                    "description": {"type": "string", "description": "Event description (optional)"}
                },
                "required": ["title", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": "Search calendar events by title or keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g., 'meeting', 'project')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Delete a calendar event",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID of the event to delete"}
                },
                "required": ["event_id"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_input: dict):
    """Execute a tool based on name and input"""
    
    if tool_name == "read_emails":
        return read_emails(5)
    
    elif tool_name == "send_email":
        return send_email(
            tool_input['to'],
            tool_input['subject'],
            tool_input['body']
        )
    
    elif tool_name == "search_emails":
        return search_emails(
            tool_input['query'],
            5
        )
    
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


def process_command(user_message: str, conversation_history: list = None):
    """Process user voice command and return response"""
    
    if conversation_history is None:
        conversation_history = []
    
    today = datetime.now(IST).strftime('%Y-%m-%d')
    
    # system_prompt = f"""You are JARVIS, a personal AI assistant. You help users with their Gmail and Google Calendar tasks.
    
    # Instructions:
    # - Respond in Hindi when user speaks in Hindi, English when in English
    # - Be helpful and efficient
    # - Always confirm actions before executing complex operations
    # - Use appropriate tools to complete tasks
    # - Provide clear, concise responses
    # - Numbers, dates, and times: use ISO format when calling tools
    # - When creating calendar events, always use complete ISO datetime format
    # - Today's date is {today} and timezone is Asia/Kolkata (IST, UTC+5:30)
    # - When user says 'tomorrow', calculate the next day based on today's IST date
    # - When creating calendar events, always mention the Google Meet link from the tool result
    
    # Available tools: read_emails, send_email, search_emails, list_events, create_event, search_events, delete_event"""

    system_prompt = f"""You are JARVIS, a highly intelligent personal AI assistant created exclusively for Aparna. You have access to her Gmail and Google Calendar.

    CORE BEHAVIOR:
    - You are proactive and autonomous — execute tasks immediately without asking for confirmation unless the action is irreversible (like deleting emails or events)
    - When user says "schedule a meeting", just do it. Don't ask "shall I proceed?"
    - When user says "add a reminder", create the calendar event right away
    - Chain multiple actions automatically when needed (e.g., schedule meeting + add reminder = two create_event calls, done silently)

    LANGUAGE:
    - Respond in English.
    - Keep responses short and friendly, not robotic or formal

    ABOUT APARNA (remember this always):
    - She is a developer — sharp, busy, and doesn't like repeating herself
    - She prefers things to be done first, explained later (briefly)
    - She is working on multiple projects simultaneously and values efficiency
    - Be her supportive assistant — encouraging, calm, and always on her side
    - If she seems stressed or overwhelmed, acknowledge it warmly before helping
    - Remember context from earlier in the conversation and refer back to it naturally

    DATE & TIME:
    - Today's date is {today}, timezone is Asia/Kolkata (IST, UTC+5:30)
    - "tomorrow" = {today} + 1 day in IST
    - "evening" = 6:00 PM IST, "morning" = 9:00 AM IST, "afternoon" = 2:00 PM IST (use these as defaults if no time given)
    - Always use complete ISO datetime format for tool calls

    CALENDAR EVENTS:
    - Always add Google Meet link when creating any meeting/interview/call event
    - Default event duration = 1 hour unless specified
    - After creating event, show the Meet link clearly

    AVAILABLE TOOLS: read_emails, send_email, search_emails, list_events, create_event, search_events, delete_event"""
    
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + conversation_history,
            tools=TOOLS_DEFINITION,
            tool_choice="auto",
            max_tokens=1024,
        )
        
        assistant_message = ""
        tool_calls = []
        
        for choice in response.choices:
            if choice.message.content:
                assistant_message += choice.message.content
            
            if choice.message.tool_calls:
                tool_calls.extend(choice.message.tool_calls)
        
        if not tool_calls:
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            return {
                "response": assistant_message,
                "history": conversation_history,
                "actions": []
            }
        
        # ✅ FIX: tool_calls ko plain dict mein convert karo (JSON serializable)
        serializable_tool_calls = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in tool_calls
        ]
        
        actions = []
        tool_results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            
            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
            
            result = execute_tool(tool_name, tool_input)
            actions.append({
                "tool": tool_name,
                "input": tool_input,
                "result": result
            })
            
            tool_results.append({
                "type": "tool",
                "name": tool_name,
                "content": json.dumps(result)
            })
        
        # ✅ FIX: serializable_tool_calls use karo, SDK objects nahi
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message,
            "tool_calls": serializable_tool_calls
        })
        
        for i, tool_result in enumerate(tool_results):
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_calls[i].id,
                "name": tool_calls[i].function.name,
                "content": tool_result["content"]
            })
        
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + conversation_history,
            max_tokens=512,
        )
        
        final_message = final_response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": final_message
        })
        
        return {
            "response": final_message,
            "history": conversation_history,
            "actions": actions
        }
    
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        
        # ✅ Rate limit error — short message
        if 'rate_limit_exceeded' in str(e) or '429' in str(e):
            error_response = "टोकन्स खत्म हो गए हैं 🙁 | Free limit reach ho gayi — thodi der baad try karo ya plan upgrade karo."
        else:
            error_response = f"माफ़ी चाहता हूँ, एक त्रुटि हुई | Sorry, an error occurred: {str(e)}"
        
        conversation_history.append({
            "role": "assistant",
            "content": error_response
        })
        return {
            "response": error_response,
            "history": conversation_history,
            "actions": []
        }