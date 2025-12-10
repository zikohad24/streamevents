from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm

User = get_user_model()

def event_list_view(request):
    # Obtener todos los eventos
    events = Event.objects.all().order_by('-scheduled_date')

    # Crear formulario simple
    search_form = EventSearchForm(request.GET or None)

    # Filtrar manualmente (sin depender de form.is_valid())
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )

    if category:
        events = events.filter(category=category)

    if status:
        events = events.filter(status=status)

    # Paginar
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto simple
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }

    return render(request, 'events/event_list.html', context)



def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    try:
        creator = event.creator
    except ObjectDoesNotExist:
        creator = None

    is_creator = request.user.is_authenticated and request.user == creator

    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_creator': is_creator,
        'creator': creator,
    })


@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            messages.success(request, f'Esdeveniment "{event.title}" creat correctament!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventCreationForm()

    context = {'form': form}
    return render(request, 'events/event_form.html', context)


@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.creator != request.user:
        messages.error(request, 'No tens permisos per editar aquest esdeveniment.')
        return redirect('events:event_detail', pk=event.pk)

    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Esdeveniment "{event.title}" actualitzat correctament!')
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventUpdateForm(instance=event, user=request.user)

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.creator != request.user:
        messages.error(request, 'No tens permisos per eliminar aquest esdeveniment.')
        return redirect('events:event_detail', pk=event.pk)

    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Esdeveniment "{event_title}" eliminat correctament!')
        return redirect('events:event_list')

    context = {'event': event}
    return render(request, 'events/event_confirm_delete.html', context)


@login_required
def my_events_view(request):
    events = Event.objects.filter(creator=request.user).select_related('creator')

    status_filter = request.GET.get('status', '')
    if status_filter:
        events = events.filter(status=status_filter)

    total_events = events.count()
    live_events = events.filter(status='live').count()
    scheduled_events = events.filter(status='scheduled').count()

    context = {
        'events': events,
        'total_events': total_events,
        'live_events': live_events,
        'scheduled_events': scheduled_events,
        'current_status_filter': status_filter,
    }
    return render(request, 'events/my_events.html', context)


def events_by_category_view(request, category):
    valid_categories = [choice[0] for choice in Event.CATEGORY_CHOICES]
    if category not in valid_categories:
        messages.error(request, 'Categoria no vàlida.')
        return redirect('events:event_list')

    events = Event.objects.filter(category=category).select_related('creator')
    category_name = dict(Event.CATEGORY_CHOICES)[category]

    context = {
        'events': events,
        'category': category,
        'category_name': category_name,
    }
    return render(request, 'events/events_by_category.html', context)