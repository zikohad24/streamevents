from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Rutas ESSENCIALES
    path('<int:event_pk>/messages/', views.chat_load_messages, name='chat_load_messages'),
    path('<int:event_pk>/send/', views.chat_send_message, name='chat_send_message'),
    path('message/<int:message_pk>/delete/', views.chat_delete_message, name='chat_delete_message'),

    # Rutas para admin1
    path('<int:event_pk>/delete-all/', views.chat_delete_all_messages, name='chat_delete_all'),
    path('<int:event_pk>/stats/', views.chat_admin_stats, name='chat_stats'),
]