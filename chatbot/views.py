from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from django.conf import settings

# In-memory storage for chat sessions
# Structure: {session_id: [{"role": "user/assistant", "content": "message"}, ...]}
CHAT_SESSIONS = {}

def index(request):
    """Main chatbot interface."""
    # Generate a new session ID for this chat session
    session_id = str(uuid.uuid4())
    context = {'session_id': session_id}
    return render(request, 'chatbot/index.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Handle chat messages and return AI responses."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)
        
        # Initialize session if it doesn't exist
        if session_id not in CHAT_SESSIONS:
            CHAT_SESSIONS[session_id] = []
        
        # Add user message to chat history
        CHAT_SESSIONS[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Check if OpenAI API key is configured
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if openai_api_key:
            # Try to use OpenAI API if key is available
            try:
                from openai import OpenAI

                client = OpenAI(api_key=openai_api_key)

                # Prepare messages for OpenAI API (include chat history)
                messages = CHAT_SESSIONS[session_id].copy()
                
                response = client.responses.create(
                    model="gpt-4.1-nano",
                    input=messages,
                )
                
                ai_response = response.output_text
                
            except ImportError:
                ai_response = "OpenAI package is not installed. Please install it with: pip install openai"
            except Exception as e:
                ai_response = f"OpenAI API error: {str(e)}"
        else:
            # Return a mock response with instructions
            ai_response = f"""This is a mock response to: "{user_message}"

To enable real ChatGPT responses:
1. Install the OpenAI package: pip install openai
2. Get an API key from OpenAI (https://platform.openai.com/api-keys)
3. Add OPENAI_API_KEY = 'your-api-key-here' to your Django settings.py

Chat history for this session: {len(CHAT_SESSIONS[session_id])} messages
For now, I'm just echoing your message back with some helpful information!"""
        
        # Add AI response to chat history
        CHAT_SESSIONS[session_id].append({
            "role": "assistant", 
            "content": ai_response
        })
        
        return JsonResponse({
            'response': ai_response,
            'status': 'success',
            'session_id': session_id,
            'message_count': len(CHAT_SESSIONS[session_id])
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_chat_history(request):
    """Get chat history for a specific session."""
    session_id = request.GET.get('session_id', '')
    
    if not session_id:
        return JsonResponse({'error': 'Session ID is required'}, status=400)
    
    chat_history = CHAT_SESSIONS.get(session_id, [])
    
    return JsonResponse({
        'chat_history': chat_history,
        'message_count': len(chat_history),
        'session_id': session_id
    })


@csrf_exempt
@require_http_methods(["POST"])
def clear_chat_history(request):
    """Clear chat history for a specific session."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', '')
        
        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)
        
        if session_id in CHAT_SESSIONS:
            del CHAT_SESSIONS[session_id]
        
        return JsonResponse({
            'status': 'success',
            'message': 'Chat history cleared',
            'session_id': session_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_all_sessions(request):
    """Get information about all active sessions (for debugging)."""
    sessions_info = {}
    for session_id, messages in CHAT_SESSIONS.items():
        sessions_info[session_id] = {
            'message_count': len(messages),
            'last_message': messages[-1]['content'][:50] + '...' if messages else 'No messages'
        }
    
    return JsonResponse({
        'active_sessions': len(CHAT_SESSIONS),
        'sessions': sessions_info
    })
