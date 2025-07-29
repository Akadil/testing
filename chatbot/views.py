from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings

def index(request):
    """Main chatbot interface."""
    return render(request, 'chatbot/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Handle chat messages and return AI responses."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Check if OpenAI API key is configured
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if openai_api_key:
            # Try to use OpenAI API if key is available
            try:
                from openai import OpenAI

                client = OpenAI(api_key=openai_api_key)

                response = client.responses.create(
                    model="gpt-4.1-nano",
                    input=user_message,
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

For now, I'm just echoing your message back with some helpful information!"""
        
        return JsonResponse({
            'response': ai_response,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
