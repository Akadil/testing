from django.shortcuts import render

def index(request):
    """Home page view that displays navigation to different projects."""
    context = {
        'projects': [
            {
                'name': 'ChatGPT Chatbot',
                'description': 'An intelligent chatbot powered by ChatGPT API with a beautiful interface',
                'url': '/chatbot/',
                'status': 'Active'
            },
            # Add more projects here as you create them
        ]
    }
    return render(request, 'home/index.html', context)
