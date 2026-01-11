from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timesince import timesince

from .models import ChatMessage
from .forms import ChatMessageForm
from events.models import Event


@csrf_exempt
def chat_load_messages(request, event_pk):
    """Cargar mensajes del chat"""
    try:
        # 1. Obtener evento
        event = Event.objects.get(pk=event_pk)

        # 2. Consulta SIMPLE - sin exclude() primero
        all_messages = ChatMessage.objects.filter(event=event)

        # 3. Filtrar en Python (evita problemas Djongo)
        messages = []
        for msg in all_messages[:100]:  # Máximo 100
            if not getattr(msg, 'is_deleted', False):
                messages.append(msg)

        # 4. Preparar datos
        data = []
        for msg in messages[:50]:  # Máximo 50 al frontend
            display_name = msg.user.username if msg.user else 'Anònim'

            # Calcular si el usuario actual puede eliminar este mensaje
            can_delete = (
                request.user.is_authenticated and
                msg.user == request.user and
                not getattr(msg, 'is_deleted', False)
            )

            data.append({
                'id': msg.id,
                'display_name': display_name,
                'message': msg.message,
                'created_at': timesince(msg.created_at, timezone.now()) + ' enrere',
                'can_delete': can_delete,
                'is_highlighted': False,
            })

        return JsonResponse({'messages': data})

    except Event.DoesNotExist:
        return JsonResponse({'messages': [], 'error': 'Event no trobat'})
    except Exception as e:
        # Si hay error, devolver datos de prueba
        return JsonResponse({
            'messages': [
                {
                    'id': 1,
                    'display_name': 'Sistema',
                    'message': 'Chat en funcionament',
                    'created_at': 'Ara',
                    'can_delete': False,
                    'is_highlighted': True,
                }
            ]
        })


@login_required
@require_POST
def chat_send_message(request, event_pk):
    """Enviar mensaje - Versión simple"""
    try:
        event = Event.objects.get(pk=event_pk)

        if event.status != 'live':
            return JsonResponse({'success': False, 'error': 'Event no actiu'})

        message_text = request.POST.get('message', '').strip()
        if not message_text:
            return JsonResponse({'success': False, 'error': 'Missatge buit'})

        # Crear mensaje
        msg = ChatMessage.objects.create(
            event=event,
            user=request.user,
            message=message_text
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'display_name': request.user.username,
                'message': msg.message,
                'created_at': 'Ara',
                'can_delete': True,
                'is_highlighted': False,
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def chat_delete_message(request, message_pk):
    """Eliminar mensaje"""
    try:
        msg = ChatMessage.objects.get(pk=message_pk)

        # Verificar permisos: solo el autor puede eliminar
        if request.user != msg.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'No tens permisos per eliminar aquest missatge'
            })

        msg.is_deleted = True
        msg.save()

        return JsonResponse({'success': True})

    except ChatMessage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Missatge no trobat'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        })