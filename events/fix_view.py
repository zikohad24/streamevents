# events/fix_view.py - SOLUCIÓN TEMPORAL
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db import connection
from collections import namedtuple

def get_events_safe():
    '''Obtener eventos sin campos problemáticos'''
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, description, scheduled_date, 
                   location, category, status, created_at,
                   organizer_id, image, tags, is_featured,
                   max_attendees, current_attendees
            FROM events_event
        """)
        
        columns = [col[0] for col in cursor.description]
        EventTuple = namedtuple('EventTuple', columns)
        
        return [EventTuple(*row) for row in cursor.fetchall()]

def event_list_view_fixed(request):
    '''Versión fija de la vista de eventos'''
    events_data = get_events_safe()
    
    # Convertir a objetos similares a Event
    class SimpleEvent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def get_absolute_url(self):
            return f'/events/{self.id}/'
    
    events = []
    for data in events_data:
        event_dict = {
            'id': data.id,
            'title': data.title,
            'description': data.description,
            'scheduled_date': data.scheduled_date,
            'location': data.location,
            'category': data.category,
            'status': data.status,
            'created_at': data.created_at,
            'organizer_id': data.organizer_id,
            'image': data.image,
            'tags': data.tags,
            'is_featured': data.is_featured,
            'max_attendees': data.max_attendees,
            'current_attendees': data.current_attendees,
        }
        events.append(SimpleEvent(**event_dict))
    
    # Paginación
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Eventos destacados
    featured_events = [e for e in events if getattr(e, 'is_featured', False)][:3]
    
    context = {
        'page_obj': page_obj,
        'featured_events': featured_events,
    }
    
    return render(request, 'events/event_list.html', context)
