# chatbot/urls.py 또는 config/urls.py
from django.urls import path
from chatbot.views import chatbot_view

urlpatterns = [
    path('chatbot/', chatbot_view, name='chatbot'),
]