document.addEventListener('DOMContentLoaded', () => {
    const messagesBox = document.getElementById('chat-messages');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-message-input');
    const counter = document.getElementById('message-count');
    const errorsBox = document.getElementById('chat-errors');

    // Función para obtener el token CSRF
    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Función para escapar HTML (seguridad)
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Función para eliminar mensaje
    function deleteMessage(messageId, button) {
        if (!confirm('¿Estàs segur de voler eliminar aquest missatge?')) {
            return;
        }

        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        fetch(`/chat/message/${messageId}/delete/`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Encontrar el mensaje y marcarlo como eliminado
                const messageElement = button.closest('.chat-message');
                if (messageElement) {
                    // Cambiar el contenido del mensaje
                    const contentElement = messageElement.querySelector('.message-content');
                    if (contentElement) {
                        contentElement.innerHTML = '<em class="text-muted">Missatge eliminat</em>';
                    }

                    // Ocultar el botón de eliminar
                    button.style.display = 'none';

                    // Opcional: agregar clase CSS para mensaje eliminado
                    messageElement.classList.add('message-deleted');
                }

                // Reducir contador
                if (counter && counter.textContent) {
                    const currentCount = parseInt(counter.textContent) || 0;
                    if (currentCount > 0) {
                        counter.textContent = currentCount - 1;
                    }
                }
            } else {
                alert('Error: ' + (data.error || 'No es pot eliminar el missatge'));
            }
        })
        .catch(err => {
            console.error('Error eliminando mensaje:', err);
            alert('Error de connexió al servidor');
        });
    }

    // Cargar mensajes
    function loadMessages() {
        fetch(`/chat/${eventId}/messages/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.messages && data.messages.length > 0) {
                    // Guardar posición actual de scroll
                    const isScrolledToBottom =
                        messagesBox.scrollHeight - messagesBox.clientHeight <= messagesBox.scrollTop + 1;

                    // Limpiar contenedor
                    messagesBox.innerHTML = '';

                    // Actualizar contador
                    if (counter) {
                        counter.textContent = data.messages.length;
                    }

                    // Crear mensajes
                    data.messages.forEach(msg => {
                        const div = document.createElement('div');
                        div.className = 'chat-message';
                        div.dataset.id = msg.id;
                        div.dataset.canDelete = msg.can_delete;

                        if (msg.is_highlighted) {
                            div.classList.add('highlighted');
                        }

                        // Contenido del mensaje
                        let messageContent = escapeHtml(msg.message);

                        // Botón de eliminar (solo si can_delete es true)
                        let deleteButton = '';
                        if (msg.can_delete) {
                            deleteButton = `
                                <button class="btn btn-sm btn-outline-danger delete-btn ms-2"
                                        onclick="deleteMessage(${msg.id}, this)"
                                        title="Eliminar missatge">
                                    🗑️
                                </button>
                            `;
                        }

                        div.innerHTML = `
                            <div class="message-header">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div class="flex-grow-1">
                                        <strong class="message-user">${escapeHtml(msg.display_name)}</strong>
                                        <small class="message-time text-muted ms-2">${escapeHtml(msg.created_at)}</small>
                                    </div>
                                    ${deleteButton}
                                </div>
                            </div>
                            <div class="message-content mt-2">
                                ${messageContent}
                            </div>
                        `;

                        messagesBox.appendChild(div);
                    });

                    // Scroll al final si estaba abajo
                    if (isScrolledToBottom) {
                        messagesBox.scrollTop = messagesBox.scrollHeight;
                    }

                } else if (data.messages && data.messages.length === 0) {
                    // Solo mostrar "no hay mensajes" si realmente está vacío
                    if (!messagesBox.querySelector('.no-messages')) {
                        messagesBox.innerHTML = `
                            <div class="no-messages text-center text-muted p-5">
                                <i class="fas fa-comments fa-2x mb-3"></i>
                                <p class="mb-0">No hi ha missatges encara.<br>Sigues el primer a escriure!</p>
                            </div>`;
                    }
                    if (counter) {
                        counter.textContent = '0';
                    }
                }

                // Si hay error, mostrarlo
                if (data.error) {
                    console.error('Error del servidor:', data.error);
                }
            })
            .catch(err => {
                console.error('Error cargando mensajes:', err);
                // Solo mostrar error si no hay contenido
                if (messagesBox.children.length === 0) {
                    messagesBox.innerHTML = `
                        <div class="text-danger text-center p-3">
                            <i class="fas fa-exclamation-triangle"></i>
                            Error carregant missatges. Torna a intentar-ho.
                        </div>`;
                }
            });
    }

    // Enviar mensaje
    if (form) {
        form.addEventListener('submit', e => {
            e.preventDefault();

            // Limpiar errores
            if (errorsBox) {
                errorsBox.textContent = '';
                errorsBox.className = 'text-danger small';
            }

            const message = input.value.trim();
            if (!message) {
                if (errorsBox) {
                    errorsBox.textContent = 'El missatge no pot estar buit';
                }
                return;
            }

            if (message.length > 500) {
                if (errorsBox) {
                    errorsBox.textContent = 'El missatge és massa llarg (màxim 500 caràcters)';
                }
                return;
            }

            const formData = new FormData();
            formData.append('message', message);
            formData.append('csrfmiddlewaretoken', getCSRFToken());

            // Deshabilitar el botón mientras se envía
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviant...';
            }

            fetch(`/chat/${eventId}/send/`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Limpiar input
                    input.value = '';

                    // Recargar mensajes después de enviar
                    loadMessages();

                    // Enfocar de nuevo en el input
                    input.focus();
                } else {
                    // Mostrar error
                    if (errorsBox) {
                        errorsBox.textContent = data.error || 'Error enviant el missatge';
                    }
                }
            })
            .catch(err => {
                console.error('Error enviando mensaje:', err);
                if (errorsBox) {
                    errorsBox.textContent = 'Error de connexió amb el servidor';
                }
            })
            .finally(() => {
                // Rehabilitar el botón
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            });
        });
    }

    // Hacer la función deleteMessage disponible globalmente
    window.deleteMessage = deleteMessage;

    // Cargar mensajes al inicio
    loadMessages();

    // Recargar automáticamente cada 3 segundos
    setInterval(loadMessages, 3000);
});