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
    logger.debug("Verificando configuración de notificaciones...")

    # Verificar si las notificaciones están habilitadas
    # Soporta tanto EMAIL_ENABLED (legacy) como NOTIFICATION_ENABLED
    enabled = os.getenv('NOTIFICATION_ENABLED', os.getenv('EMAIL_ENABLED', '0'))

    if enabled != '1':
        logger.info("🔕 Notificaciones deshabilitadas (NOTIFICATION_ENABLED != 1)")
        return None

    # Obtener tipo de notificador
    notifier_type = os.getenv('NOTIFICATION_TYPE', 'email').lower()
    logger.info(f"🔔 Notificaciones habilitadas - Tipo: {notifier_type.upper()}")

    if notifier_type not in NOTIFIERS:
        logger.error(f"❌ Tipo de notificador desconocido: '{notifier_type}'")
        logger.info(f"   Tipos disponibles: {', '.join(NOTIFIERS.keys())}")
        return None

    logger.debug(f"Instanciando notificador: {notifier_type}")
    notifier = NOTIFIERS[notifier_type]()
    logger.debug(f"✓ Notificador {notifier_type} creado exitosamente")

    return notifier


def send_notification(consumos: list, cotizacion: float) -> bool:
    """
    Función de conveniencia para enviar notificación.

    Args:
        consumos: Lista de consumos procesados
        cotizacion: Cotización del dólar

    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    logger.debug(f"Iniciando proceso de notificación - Consumos: {len(consumos)}, Cotización: {cotizacion}")

    notifier = get_notifier()

    if notifier is None:
        return False

    logger.info(f"📊 Enviando reporte con {len(consumos)} consumos...")
    result = notifier.send(consumos, cotizacion)

    if result:
        logger.info("✅ Notificación enviada exitosamente")
    else:
        logger.error("❌ Error al enviar notificación")

    return result

