from django.urls import path
from . import views

urlpatterns = [
    path('<int:event_pk>/messages/', views.chat_load_messages, name='chat_load_messages'),
    path('<int:event_pk>/send/', views.chat_send_message, name='chat_send_message'),
    path('message/<int:message_pk>/delete/', views.chat_delete_message, name='chat_delete_message'),  # Esta debe existir
]