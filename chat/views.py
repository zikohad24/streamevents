from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import time
from datetime import datetime

# Almacenamiento TEMPORAL en memoria (para pruebas)
TEMPORAL_MESSAGES = []


@csrf_exempt
def chat_load_messages(request, event_pk):
    """
    Cargar mensajes - VERSIÓN CORREGIDA
    """
    print(f"📡 Cargando mensajes para evento: {event_pk}")

    # Filtrar mensajes para este evento
    event_messages = [m for m in TEMPORAL_MESSAGES if m.get('event_id') == event_pk]

    print(f"📡 Encontrados {len(event_messages)} mensajes")

    # Preparar respuesta
    current_user = request.user.username if request.user.is_authenticated else None
    is_admin = (current_user == 'admin1')

    messages_to_send = []

    for msg in event_messages:
        # Determinar si el usuario actual puede eliminar este mensaje
        can_delete = False

        # Caso 1: Es admin1
        if is_admin:
            can_delete = True

        # Caso 2: Es el usuario que creó el mensaje Y el mensaje no está eliminado
        elif current_user and msg.get('username') == current_user and not msg.get('is_deleted', False):
            can_delete = True

        # Solo mostrar mensaje si NO está eliminado (excepto para admin)
        if not msg.get('is_deleted', False) or is_admin:
            messages_to_send.append({
                'id': msg.get('id'),
                'username': msg.get('username'),
                'display_name': msg.get('display_name'),
                'message': msg.get('message') if not msg.get('is_deleted', False) else '[Missatge eliminat]',
                'created_at': msg.get('created_at'),
                'can_delete': can_delete,
                'is_own_message': current_user and msg.get('username') == current_user,
                'is_deleted': msg.get('is_deleted', False),
                'deleted_info': msg.get('deleted_info', ''),
                'is_admin': is_admin,
            })

    # Si no hay mensajes, crear uno de bienvenida


    return JsonResponse({
        'success': True,
        'messages': messages_to_send,
        'count': len(messages_to_send),
    })

@login_required
@csrf_exempt
def chat_send_message(request, event_pk):
    """
    Enviar mensaje - VERSIÓN DE EMERGENCIA
    """
    print(f"🚨 [CHAT-EMERGENCIA] Enviando mensaje para evento: {event_pk}")
    print(f"🚨 [CHAT-EMERGENCIA] Usuario: {request.user.username}")

    try:
        # Obtener mensaje
        message_text = ""

        if request.POST:
            message_text = request.POST.get('message', '').strip()
        else:
            try:
                body = request.body.decode('utf-8')
                if body:
                    data = json.loads(body)
                    message_text = data.get('message', '').strip()
            except:
                pass

        print(f"🚨 [CHAT-EMERGENCIA] Mensaje recibido: '{message_text}'")

        if not message_text:
            return JsonResponse({'success': False, 'error': 'Mensaje vacío'})

        # Crear nuevo mensaje
        new_message = {
            'id': int(time.time() * 1000),  # ID único basado en tiempo
            'event_id': int(event_pk),
            'username': request.user.username,
            'display_name': request.user.username,
            'message': message_text,
            'created_at': 'Ara mateix',
            'can_delete': True,
            'is_own_message': True,
            'is_deleted': False,
            'deleted_info': '',
            'is_admin': request.user.username == 'admin1' or request.user.is_staff,
        }

        # Añadir a memoria
        TEMPORAL_MESSAGES.append(new_message)

        # Limitar a 100 mensajes máximo
        if len(TEMPORAL_MESSAGES) > 100:
            TEMPORAL_MESSAGES.pop(0)

        print(f"🚨 [CHAT-EMERGENCIA] ✅ Mensaje guardado en memoria")
        print(f"🚨 [CHAT-EMERGENCIA]   Total mensajes en memoria: {len(TEMPORAL_MESSAGES)}")

        return JsonResponse({
            'success': True,
            'message': 'Mensaje enviado',
            'message_data': new_message,
            'debug': {
                'stored_in': 'MEMORY',
                'total_messages': len(TEMPORAL_MESSAGES)
            }
        })

    except Exception as e:
        print(f"🚨 [CHAT-EMERGENCIA] ❌ Error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


# Las otras funciones las dejamos simples
@login_required
@csrf_exempt
def chat_delete_message(request, message_pk):
    """Eliminar mensaje - versión simple"""
    try:
        # Buscar mensaje en memoria
        for msg in TEMPORAL_MESSAGES:
            if str(msg.get('id')) == str(message_pk):
                msg['is_deleted'] = True
                msg['deleted_info'] = f"Eliminat per {request.user.username}"
                return JsonResponse({'success': True, 'message': 'Eliminat'})

        return JsonResponse({'success': False, 'error': 'Missatge no trobat'})
    except:
        return JsonResponse({'success': False, 'error': 'Error'})


@csrf_exempt
def chat_delete_all_messages(request, event_pk):
    """Eliminar todos - solo admin1"""
    if request.user.username != 'admin1':
        return JsonResponse({'success': False, 'error': 'Solo admin1'})

    # Marcar como eliminados
    deleted = 0
    for msg in TEMPORAL_MESSAGES:
        if msg.get('event_id') == int(event_pk) and not msg.get('is_deleted'):
            msg['is_deleted'] = True
            msg['deleted_info'] = f"Eliminat per {request.user.username}"
            deleted += 1

    return JsonResponse({
        'success': True,
        'message': f'{deleted} mensajes eliminados',
        'count': deleted
    })


@login_required
def chat_admin_stats(request, event_pk):
    """
    Estadísticas para admin1 - VERSIÓN SIMPLE
    """
    try:
        user = request.user

        # Solo admin1 puede ver estadísticas
        if user.username != 'admin1' and not user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'No autorizado.'
            })

        # Contar mensajes en memoria
        event_messages = [m for m in TEMPORAL_MESSAGES if m.get('event_id') == event_pk]
        total_messages = len(event_messages)
        active_messages = len([m for m in event_messages if not m.get('is_deleted', False)])
        deleted_messages = len([m for m in event_messages if m.get('is_deleted', False)])

        # Usuarios únicos
        unique_users = len(set(m.get('username') for m in event_messages if m.get('username')))

        return JsonResponse({
            'success': True,
            'event': {
                'id': event_pk,
                'title': f'Evento {event_pk}',
            },
            'stats': {
                'total_messages': total_messages,
                'active_messages': active_messages,
                'deleted_messages': deleted_messages,
                'unique_users': unique_users,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })