/**
 * SISTEMA DE CHAT COMPLETO con eliminación y admin
 */

class CompleteChat {
    constructor(config) {
        this.config = config;
        this.initElements();
        this.setupEventListeners();
        this.loadMessages();

        // Auto-refresh si el evento está en vivo
        if (this.config.isEventLive) {
            this.startPolling();
        }

        console.log('✅ Chat completo inicializado', this.config);
    }

    initElements() {
        this.elements = {
            // Contenedores
            messages: document.getElementById('chat-messages'),
            form: document.getElementById('chat-form'),

            // Inputs y controles
            input: document.getElementById('chat-message-input'),
            charCount: document.getElementById('chat-char-count'),
            errors: document.getElementById('chat-errors'),
            count: document.getElementById('chat-message-count'),
            status: document.getElementById('chat-status'),

            // Botones
            sendBtn: document.getElementById('chat-send-btn'),
            deleteAllBtn: document.getElementById('chat-delete-all-btn'),
            refreshBtn: document.getElementById('chat-refresh-btn'),

            // Admin
            adminPanel: document.getElementById('chat-admin-panel'),
            adminStats: document.getElementById('chat-admin-stats')
        };
    }

    setupEventListeners() {
        // Contador de caracteres
        if (this.elements.input && this.elements.charCount) {
            this.elements.input.addEventListener('input', () => {
                const length = this.elements.input.value.length;
                this.elements.charCount.textContent = `${length}/500`;
                this.elements.charCount.className = length > 500 ? 'text-danger' : 'text-muted';

                // Habilitar/deshabilitar botón de enviar
                if (this.elements.sendBtn) {
                    this.elements.sendBtn.disabled = length === 0 || length > 500;
                }
            });

            // Disparar evento para actualizar estado inicial
            this.elements.input.dispatchEvent(new Event('input'));
        }

        // Enviar mensaje
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Botón eliminar todo (solo para admin1)
        if (this.elements.deleteAllBtn && this.config.isUserAdmin) {
            this.elements.deleteAllBtn.addEventListener('click', () => this.deleteAllMessages());
        }

        // Botón refrescar
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => {
                this.loadMessages();
                this.showToast('Mensajes actualizados', 'info');
            });
        }

        // Delegación para eliminar mensajes individuales
        if (this.elements.messages) {
            this.elements.messages.addEventListener('click', (e) => {
                const deleteBtn = e.target.closest('.delete-message-btn');
                if (deleteBtn) {
                    const messageId = deleteBtn.dataset.messageId;
                    this.deleteMessage(messageId);
                }
            });
        }

        // Mostrar/ocultar panel admin
        if (this.config.isUserAdmin && this.elements.adminPanel) {
            this.elements.adminPanel.style.display = 'block';

            // Botón estadísticas
            if (this.elements.adminStats) {
                this.elements.adminStats.addEventListener('click', () => this.showAdminStats());
            }
        }
    }

    async loadMessages() {
        try {
            this.setStatus('Cargando...');

            const response = await fetch(`/chat/${this.config.eventId}/messages/`);
            const data = await response.json();

            if (data.success) {
                this.renderMessages(data.messages);
                this.updateCount(data.count || data.messages.length);
                this.setStatus(`${data.count || data.messages.length} mensajes`);
            } else {
                this.showError('Error al cargar mensajes: ' + (data.error || ''));
                this.setStatus('Error');
            }
        } catch (error) {
            console.error('Error cargando mensajes:', error);
            this.showError('Error de conexión');
            this.setStatus('Sin conexión');
        }
    }

    renderMessages(messages) {
        if (!this.elements.messages) return;

        if (messages.length === 0) {
            this.elements.messages.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-comments fa-3x mb-3 opacity-25"></i>
                    <h6 class="mb-2">No hay mensajes</h6>
                    <p class="small mb-0">🎉 ¡Sé el primero en escribir!</p>
                </div>
            `;
            return;
        }

        let html = '';

        messages.forEach(msg => {
            const isOwn = msg.is_own_message;
            const isDeleted = msg.is_deleted;
            const canDelete = msg.can_delete && !isDeleted;
            const isAdmin = this.config.isUserAdmin;

            // Estilos según tipo de mensaje
            let messageClass = 'chat-message mb-3 p-3 rounded';
            let borderClass = '';
            let bgClass = '';

            if (isDeleted) {
                bgClass = 'bg-light';
                messageClass += ' opacity-50';
            } else if (isOwn) {
                bgClass = 'bg-primary-subtle';
                borderClass = 'border-primary border-start-4';
            } else {
                bgClass = 'bg-white';
                borderClass = 'border';
            }

            // Icono según tipo
            let icon = 'fa-user';
            if (msg.username === 'sistema') icon = 'fa-robot';
            if (this.config.isUserAdmin && msg.username === 'admin1') icon = 'fa-crown';

            html += `
                <div class="${messageClass} ${bgClass} ${borderClass}" data-message-id="${msg.id}">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="d-flex align-items-center">
                            <i class="fas ${icon} me-2 ${isOwn ? 'text-primary' : 'text-muted'}"></i>
                            <strong class="message-user ${isOwn ? 'text-primary' : ''}">
                                ${this.escapeHtml(msg.display_name)}
                            </strong>
                            ${isOwn ? '<span class="badge bg-primary ms-2">Tú</span>' : ''}
                            ${isDeleted ? '<span class="badge bg-danger ms-2">Eliminado</span>' : ''}
                        </div>
                        <div class="d-flex align-items-center">
                            <small class="message-time text-muted me-2">
                                ${this.escapeHtml(msg.created_at)}
                            </small>
                            ${canDelete ? `
                                <button class="delete-message-btn btn btn-sm btn-outline-danger"
                                        data-message-id="${msg.id}"
                                        title="${isAdmin ? 'Eliminar mensaje (Admin)' : 'Eliminar mi mensaje'}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>

                    <div class="message-content mt-2">
                        ${isDeleted ?
                            `<div class="text-muted fst-italic">
                                <i class="fas fa-ban me-1"></i>
                                ${msg.deleted_info || 'Mensaje eliminado'}
                            </div>`
                            :
                            this.escapeHtml(msg.message)
                        }
                    </div>

                    ${isDeleted && isAdmin ? `
                        <div class="mt-2 small text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            Original: "${this.escapeHtml(msg.original_message)}"
                        </div>
                    ` : ''}
                </div>
            `;
        });

        this.elements.messages.innerHTML = html;

        // Scroll al final
        this.scrollToBottom();
    }

    async handleSubmit(e) {
        e.preventDefault();

        // Verificar autenticación y estado del evento
        if (!this.config.isAuthenticated) {
            this.showError('Debes iniciar sesión para enviar mensajes');
            return;
        }

        if (!this.config.isEventLive) {
            this.showError('El evento no está en directo');
            return;
        }

        const message = this.elements.input.value.trim();

        // Validaciones
        if (!message) {
            this.showError('Escribe un mensaje');
            return;
        }

        if (message.length > 500) {
            this.showError('Máximo 500 caracteres');
            return;
        }

        // Deshabilitar formulario
        this.disableForm(true);
        this.setStatus('Enviando...');

        try {
            const formData = new FormData();
            formData.append('message', message);
            formData.append('csrfmiddlewaretoken', this.config.csrfToken);

            const response = await fetch(`/chat/${this.config.eventId}/send/`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Limpiar input y errores
                this.elements.input.value = '';
                this.elements.input.dispatchEvent(new Event('input'));
                this.clearErrors();

                // Mostrar confirmación
                this.showToast('Mensaje enviado', 'success');

                // Recargar mensajes después de un breve delay
                setTimeout(() => this.loadMessages(), 300);
            } else {
                this.showError(data.error || 'Error al enviar');
            }
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            this.showError('Error de conexión');
        } finally {
            this.disableForm(false);
            this.setStatus('Conectado');
        }
    }

    async deleteMessage(messageId) {
        if (!confirm('¿Estás seguro de eliminar este mensaje?')) {
            return;
        }

        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', this.config.csrfToken);

            const response = await fetch(`/chat/message/${messageId}/delete/`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Mensaje eliminado', 'warning');
                this.loadMessages(); // Recargar para mostrar cambios
            } else {
                alert('Error: ' + (data.error || 'No se pudo eliminar'));
            }
        } catch (error) {
            console.error('Error eliminando mensaje:', error);
            alert('Error de conexión');
        }
    }

    async deleteAllMessages() {
        if (!this.config.isUserAdmin) {
            alert('Solo admin1 puede eliminar todos los mensajes');
            return;
        }

        if (!confirm('⚠️ ¿ELIMINAR TODOS LOS MENSAJES?\n\nEsta acción es irreversible y eliminará TODOS los mensajes del chat.')) {
            return;
        }

        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', this.config.csrfToken);

            const response = await fetch(`/chat/${this.config.eventId}/delete-all/`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showToast(`✅ ${data.message}`, 'danger');
                this.loadMessages();
            } else {
                alert('❌ Error: ' + (data.error || 'No se pudieron eliminar los mensajes'));
            }
        } catch (error) {
            console.error('Error eliminando todos:', error);
            alert('❌ Error de conexión');
        }
    }

    async showAdminStats() {
        if (!this.config.isUserAdmin) return;

        try {
            const response = await fetch(`/chat/${this.config.eventId}/stats/`);
            const data = await response.json();

            if (data.success) {
                const stats = data.stats;
                alert(`📊 ESTADÍSTICAS DEL CHAT\n\n` +
                      `Total mensajes: ${stats.total_messages}\n` +
                      `Mensajes activos: ${stats.active_messages}\n` +
                      `Mensajes eliminados: ${stats.deleted_messages}\n` +
                      `Usuarios únicos: ${stats.unique_users}\n\n` +
                      `Evento: ${data.event.title}`);
            }
        } catch (error) {
            console.error('Error obteniendo estadísticas:', error);
        }
    }

    // Métodos auxiliares
    startPolling() {
        this.pollingInterval = setInterval(() => {
            this.loadMessages();
        }, 3000); // Actualizar cada 3 segundos
    }

    setStatus(text) {
        if (this.elements.status) {
            this.elements.status.textContent = text;
        }
    }

    updateCount(count) {
        if (this.elements.count) {
            this.elements.count.textContent = `${count} mensajes`;
        }
    }

    showError(message) {
        if (this.elements.errors) {
            this.elements.errors.textContent = message;
            setTimeout(() => this.clearErrors(), 5000);
        }
    }

    clearErrors() {
        if (this.elements.errors) {
            this.elements.errors.textContent = '';
        }
    }

    disableForm(disabled) {
        if (this.elements.input) this.elements.input.disabled = disabled;
        if (this.elements.sendBtn) {
            this.elements.sendBtn.disabled = disabled;
            this.elements.sendBtn.innerHTML = disabled ?
                '<i class="fas fa-spinner fa-spin me-1"></i> Enviando...' :
                '<i class="fas fa-paper-plane me-1"></i> Enviar';
        }
    }

    scrollToBottom() {
        if (this.elements.messages) {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        }
    }

    showToast(message, type = 'info') {
        // Crear toast si no existe
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
            document.body.appendChild(toastContainer);
        }

        // Colores según tipo
        const colors = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info',
            'danger': 'bg-danger'
        };

        const toast = document.createElement('div');
        toast.className = `toast show text-white ${colors[type] || 'bg-info'} mb-2`;
        toast.style.cssText = 'min-width: 250px;';
        toast.innerHTML = `
            <div class="toast-body d-flex justify-content-between align-items-center">
                <span>${message}</span>
                <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto-eliminar después de 3 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    if (window.CHAT_CONFIG) {
        window.chatSystem = new CompleteChat(window.CHAT_CONFIG);
    } else {
        console.error('❌ Configuración del chat no encontrada');
    }
});