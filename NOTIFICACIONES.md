# 🔔 Sistema de Notificaciones
## Descripción
El sistema de notificaciones usa el patrón **Protocol** de Python para permitir múltiples tipos de notificadores de forma flexible y extensible.
## Arquitectura
```
notifiers/
├── __init__.py      # Exports públicos del módulo
├── base.py          # Protocol Notifier (interfaz)
├── email.py         # EmailNotifier (Resend + SMTP)
└── factory.py       # Factory para crear notificadores
```
## Cómo Funciona
### Protocol (Duck Typing)
```python
from typing import Protocol
class Notifier(Protocol):
    def send(self, consumos: list, cotizacion: float) -> bool:
        ...
```
Cualquier clase que implemente el método `send` con esta firma es un `Notifier` válido.
### Factory Pattern
```python
from notifiers import send_notification
# El factory lee NOTIFICATION_TYPE del .env y crea el notificador correcto
send_notification(consumos, cotizacion)
```
## Configuración
```env
# Habilitar notificaciones
NOTIFICATION_ENABLED=1
# Tipo de notificador (actualmente: email)
NOTIFICATION_TYPE=email
# Configuración específica del notificador...
```
## Notificadores Disponibles
### Email (`NOTIFICATION_TYPE=email`)
Soporta dos proveedores:
| Proveedor | Variable | Descripción |
|-----------|----------|-------------|
| Resend | `EMAIL_PROVIDER=resend` | API moderna, recomendado |
| SMTP | `EMAIL_PROVIDER=smtp` | Gmail, Outlook, etc. |
Ver [EMAIL.md](EMAIL.md) para configuración detallada.
## Agregar Nuevo Notificador
Para agregar un nuevo tipo de notificador (ej: Telegram):
### 1. Crear el notificador
```python
# notifiers/telegram.py
class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
    def send(self, consumos: list, cotizacion: float) -> bool:
        # Implementación...
        return True
```
### 2. Registrar en el factory
```python
# notifiers/factory.py
from .telegram import TelegramNotifier
NOTIFIERS = {
    'email': EmailNotifier,
    'telegram': TelegramNotifier,  # Agregar aquí
}
```
### 3. Documentar variables de entorno
```env
NOTIFICATION_TYPE=telegram
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```
## Ventajas de esta Arquitectura
1. **Extensible**: Fácil agregar nuevos notificadores
2. **Desacoplado**: Cada notificador es independiente
3. **Testeable**: Se pueden crear mocks fácilmente
4. **Duck Typing**: No requiere herencia explícita
