import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .agent import process_command
from django.contrib.sessions.models import Session

logger = logging.getLogger(__name__)


def index(request):
    """Render main interface"""
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def process_voice_command(request):
    """Process voice command and return AI response"""
    try:
        data = json.loads(request.body)
        command = data.get('command', '').strip()
        
        if not command:
            return JsonResponse({
                "status": "error",
                "message": "कोई कमांड नहीं मिला | No command provided"
            }, status=400)
        
        logger.info(f"Processing command: {command}")
        
        # Get conversation history from session
        conversation_history = request.session.get('conversation_history', [])
        
        # Process command with agent
        result = process_command(command, conversation_history)
        
        # Update session with new history
        request.session['conversation_history'] = result['history']
        request.session.modified = True
        
        return JsonResponse({
            "status": "success",
            "response": result['response'],
            "actions": result['actions']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON format"
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clear_conversation(request):
    """Clear conversation history"""
    request.session['conversation_history'] = []
    request.session.modified = True
    
    return JsonResponse({
        "status": "success",
        "message": "बातचीत साफ़ की गई | Conversation cleared"
    })


@require_http_methods(["GET"])
def get_status(request):
    """Get system status"""
    return JsonResponse({
        "status": "online",
        "message": "JARVIS सक्रिय है | JARVIS is active",
        "wake_word": "hey jarvis"
    })
