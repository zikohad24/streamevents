# events/models.py
from django.db import models
from django.conf import settings  # ← AÑADE ESTO
from django.contrib.auth import get_user_model  # ← O ESTO
from django.urls import reverse
from django.utils import timezone
import re

# OPCIÓN 1: Usar get_user_model() (RECOMENDADO)
User = get_user_model()


class Event(models.Model):
    # Opciones para categorías
    CATEGORY_CHOICES = [
        ('gaming', '🎮 Gaming'),
        ('music', '🎵 Música'),
        ('technology', '💻 Tecnologia'),
        ('education', '📚 Educació'),
        ('art', '🎨 Art'),
        ('talk', '💬 Xerrada'),
        ('sports', '⚽ Esports'),
        ('entertainment', '🎭 Entreteniment'),
    ]

    # Opciones para estados
    STATUS_CHOICES = [
        ('draft', 'Esborrany'),
        ('scheduled', 'Programat'),
        ('live', 'En directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]

    # Campos del modelo
    title = models.CharField(max_length=200, verbose_name="Títol")
    description = models.TextField(verbose_name="Descripció")

    # CORREGIDO: Usar get_user_model() o settings.AUTH_USER_MODEL
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← ESTA ES LA FORMA CORRECTA
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Creador"
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='gaming', verbose_name="Categoria")
    scheduled_date = models.DateTimeField(verbose_name="Data i hora programada")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Estat")
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, null=True, verbose_name="Miniatura")
    max_viewers = models.PositiveIntegerField(default=100, verbose_name="Màxim espectadors")
    is_featured = models.BooleanField(default=False, verbose_name="Destacat")
    tags = models.CharField(max_length=255, blank=True, verbose_name="Etiquetes")
    stream_url = models.URLField(max_length=500, verbose_name="URL del stream")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de creació")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data d'actualització")

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Esdeveniment"
        verbose_name_plural = "Esdeveniments"

    # Métodos (se mantienen igual)
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    def get_stream_embed_url(self):
        """Convierte URL de YouTube/Twitch a embed"""
        if not self.stream_url:
            return ""

        if 'youtube.com' in self.stream_url or 'youtu.be' in self.stream_url:
            video_id = None
            patterns = [
                r'youtube\.com/watch\?v=([^&]+)',
                r'youtu\.be/([^?]+)',
                r'youtube\.com/embed/([^?]+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, self.stream_url)
                if match:
                    video_id = match.group(1)
                    break

            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        elif 'twitch.tv' in self.stream_url:
            return self.stream_url.replace('twitch.tv/', 'twitch.tv/embed/')

        return self.stream_url

    def get_tags_list(self):
        """Convierte string de tags a lista"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    @property
    def is_upcoming(self):
        return self.scheduled_date > timezone.now() and self.status == 'scheduled'

    @property
    def is_live_now(self):
        return self.status == 'live'

    @property
    def duration(self):
        return 60

    def __str__(self):
        return self.title