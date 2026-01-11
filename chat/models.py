from django.db import models
from django.conf import settings
from django.utils.timesince import timesince
from events.models import Event

User = settings.AUTH_USER_MODEL


class ChatMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Campos para eliminar mensajes
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.is_deleted:
            return f"Mensaje eliminado (ID: {self.id})"
        return f"{self.user.username}: {self.message[:50]}..."

    def can_delete(self, user):
        """
        Retorna True si l'usuari pot eliminar aquest missatge
        Pot eliminar: el creador del missatge, el creador de l'esdeveniment, o staff
        """
        if not user.is_authenticated:
            return False

        # El creador del missatge
        if self.user == user:
            return True

        # El creador de l'esdeveniment
        if hasattr(self.event, 'creator') and self.event.creator == user:
            return True

        # Staff
        if user.is_staff:
            return True

        return False

    def get_user_display_name(self):
        """Retorna el display_name de l'usuari si existeix, sinó el username"""
        # Si el teu CustomUser té un camp display_name
        if hasattr(self.user, 'display_name') and self.user.display_name:
            return self.user.display_name
        return self.user.username if self.user else "Anònim"

    def get_time_since(self):
        """Retorna el temps transcorregut des de la creació"""
        return f"fa {timesince(self.created_at)}"

    class Meta:
        ordering = ['created_at']  # Més antic primer
        verbose_name = 'Missatge de Xat'
        verbose_name_plural = 'Missatges de Xat'