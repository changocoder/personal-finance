# notifiers/__init__.py
"""
Módulo de notificaciones para Personal Finance App.
Soporta múltiples tipos de notificadores mediante el patrón Protocol.
"""
from .base import Notifier
from .factory import get_notifier, send_notification
from .email import EmailNotifier
__all__ = ['Notifier', 'get_notifier', 'send_notification', 'EmailNotifier']
