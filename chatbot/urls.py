from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('history/', views.get_chat_history, name='get_chat_history'),
    path('clear/', views.clear_chat_history, name='clear_chat_history'),
    path('sessions/', views.get_all_sessions, name='get_all_sessions'),
]
