# notifiers/factory.py
"""
Factory para crear notificadores basándose en la configuración del .env
"""

import os
import logging
from typing import Optional

from .base import Notifier
from .email import EmailNotifier

logger = logging.getLogger(__name__)

# Registro de notificadores disponibles
NOTIFIERS = {
    'email': EmailNotifier,
    # Futuros notificadores:
    # 'telegram': TelegramNotifier,
    # 'slack': SlackNotifier,
}


def get_notifier() -> Optional[Notifier]:
    """
    Crea y retorna el notificador configurado en las variables de entorno.

    Lee NOTIFICATION_TYPE del .env (default: 'email').
    Si las notificaciones están deshabilitadas, retorna None.

    Returns:
        Notifier configurado o None si está deshabilitado
    """
    # Verificar si las notificaciones están habilitadas
    # Soporta tanto EMAIL_ENABLED (legacy) como NOTIFICATION_ENABLED
    enabled = os.getenv('NOTIFICATION_ENABLED', os.getenv('EMAIL_ENABLED', '0'))

    if enabled != '1':
        logger.info("📧 Notificaciones deshabilitadas (NOTIFICATION_ENABLED != 1)")
        return None

    # Obtener tipo de notificador
    notifier_type = os.getenv('NOTIFICATION_TYPE', 'email').lower()

    if notifier_type not in NOTIFIERS:
        logger.error(f"❌ Tipo de notificador desconocido: {notifier_type}")
        logger.info(f"   Tipos disponibles: {', '.join(NOTIFIERS.keys())}")
        return None

    logger.debug(f"Creando notificador: {notifier_type}")
    return NOTIFIERS[notifier_type]()


def send_notification(consumos: list, cotizacion: float) -> bool:
    """
    Función de conveniencia para enviar notificación.

    Args:
        consumos: Lista de consumos procesados
        cotizacion: Cotización del dólar

    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    notifier = get_notifier()

    if notifier is None:
        return False

    return notifier.send(consumos, cotizacion)

