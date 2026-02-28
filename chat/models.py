from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    """
    Modelo para mensajes del chat
    """
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Evento'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario'
    )

    message = models.TextField(
        max_length=500,
        verbose_name='Mensaje'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    is_deleted = models.BooleanField(
        default=False,
        verbose_name='¿Eliminado?'
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de eliminación'
    )

    deleted_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Eliminado por'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mensaje del chat'
        verbose_name_plural = 'Mensajes del chat'

    def __str__(self):
        username = self.user.username if self.user else 'Anónimo'
        message_preview = self.message[:50] + '...' if len(self.message) > 50 else self.message
        status = " [ELIMINADO]" if self.is_deleted else ""
        return f"{username}: {message_preview}{status}"