from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'category', 'status', 'scheduled_date', 'is_featured', 'created_at']
    list_filter = ['category', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Informació Bàsica', {
            'fields': ('title', 'description', 'creator', 'category')
        }),
        ('Programació', {
            'fields': ('scheduled_date', 'status', 'max_viewers')
        }),
        ('Multimèdia', {
            'fields': ('thumbnail', 'stream_url')
        }),
        ('Metadades', {
            'fields': ('tags', 'is_featured', 'created_at', 'updated_at')
        }),
    )