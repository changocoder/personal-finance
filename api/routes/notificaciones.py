# api/routes/notificaciones.py
"""
Endpoints para envío de notificaciones.
"""

from fastapi import APIRouter, HTTPException
import logging
import os
import json

from api.schemas import (
    NotificacionRequest,
    NotificacionResponse,
    ErrorResponse,
    PreferenciasNotificacionRequest,
    PreferenciasNotificacionResponse
)
from api.services import NotificacionService

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])
logger = logging.getLogger(__name__)

# Archivo para persistir preferencias
PREFERENCIAS_FILE = 'preferencias_notificaciones.json'


@router.post(
    "/enviar",
    response_model=NotificacionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Enviar reporte por email",
    description="Envía el último reporte generado por email."
)
async def enviar_notificacion(request: NotificacionRequest = NotificacionRequest()):
    """
    Envía el reporte de consumos por email.

    - **tipo**: Tipo de notificación (actualmente solo 'email' disponible)

    Requisitos:
    - Debe existir un reporte generado previamente (consumos_totales.csv)
    - Las variables de entorno EMAIL_* deben estar configuradas
    - NOTIFICATION_ENABLED debe ser '1'
    """
    try:
        logger.info(f"API: Solicitud de envío de notificación (tipo={request.tipo})")

        if request.tipo.lower() != 'email':
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de notificación '{request.tipo}' no soportado. Use 'email'."
            )

        service = NotificacionService()
        resultado = service.enviar_email()

        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['message'])

        return NotificacionResponse(**resultado)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/estado",
    summary="Estado de las notificaciones",
    description="Verifica si las notificaciones están habilitadas y configuradas."
)
async def estado_notificaciones():
    """
    Verifica el estado de la configuración de notificaciones.

    Retorna información sobre:
    - Si las notificaciones están habilitadas
    - Tipo de notificador configurado
    - Email de destino (parcialmente oculto)
    """
    import os

    enabled = os.getenv('NOTIFICATION_ENABLED', os.getenv('EMAIL_ENABLED', '0')) == '1'
    tipo = os.getenv('NOTIFICATION_TYPE', 'email')
    email_to = os.getenv('EMAIL_TO', '')

    # Ocultar parcialmente el email
    if email_to and '@' in email_to:
        partes = email_to.split('@')
        email_oculto = f"{partes[0][:3]}***@{partes[1]}"
    else:
        email_oculto = "No configurado"

    return {
        "habilitado": enabled,
        "tipo": tipo,
        "destinatario": email_oculto,
        "configurado": bool(email_to and os.getenv('RESEND_API_KEY'))
    }


def _cargar_preferencias() -> dict:
    """Carga las preferencias de notificación desde archivo."""
    if os.path.exists(PREFERENCIAS_FILE):
        try:
            with open(PREFERENCIAS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando preferencias: {e}")

    # Preferencias por defecto
    return {
        'habilitado': os.getenv('NOTIFICATION_ENABLED', '0') == '1',
        'tipo': os.getenv('NOTIFICATION_TYPE', 'email'),
        'email_destino': os.getenv('EMAIL_TO', ''),
        'envio_automatico': False,
        'incluir_resumen': True,
        'incluir_detalle': True
    }


def _guardar_preferencias(preferencias: dict) -> bool:
    """Guarda las preferencias de notificación en archivo."""
    try:
        with open(PREFERENCIAS_FILE, 'w') as f:
            json.dump(preferencias, f, indent=2)
        logger.info("Preferencias de notificación guardadas")
        return True
    except Exception as e:
        logger.error(f"Error guardando preferencias: {e}")
        return False


@router.get(
    "/preferencias",
    response_model=PreferenciasNotificacionResponse,
    summary="Obtener preferencias de notificación",
    description="Obtiene las preferencias actuales de notificación."
)
async def obtener_preferencias():
    """
    Obtiene las preferencias actuales de notificación.

    Retorna:
    - Estado de habilitación
    - Tipo de notificación
    - Email de destino (parcialmente oculto)
    - Configuración de envío automático
    """
    try:
        logger.info("API: Consultando preferencias de notificación")
        preferencias = _cargar_preferencias()

        # Ocultar parcialmente el email
        email = preferencias.get('email_destino', '')
        if email and '@' in email:
            partes = email.split('@')
            preferencias['email_destino_display'] = f"{partes[0][:3]}***@{partes[1]}"
        else:
            preferencias['email_destino_display'] = "No configurado"

        return PreferenciasNotificacionResponse(
            success=True,
            message="Preferencias obtenidas correctamente",
            preferencias=preferencias
        )
    except Exception as e:
        logger.error(f"Error obteniendo preferencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/preferencias",
    response_model=PreferenciasNotificacionResponse,
    summary="Actualizar preferencias de notificación",
    description="Actualiza las preferencias de notificación."
)
async def actualizar_preferencias(request: PreferenciasNotificacionRequest):
    """
    Actualiza las preferencias de notificación.

    Parámetros:
    - **habilitado**: Habilitar/deshabilitar notificaciones
    - **tipo**: Tipo de notificación (email)
    - **email_destino**: Email de destino
    - **envio_automatico**: Enviar automáticamente después de generar reporte
    - **incluir_resumen**: Incluir resumen por categorías
    - **incluir_detalle**: Incluir detalle de consumos
    """
    try:
        logger.info(f"API: Actualizando preferencias de notificación")

        preferencias = {
            'habilitado': request.habilitado,
            'tipo': request.tipo,
            'email_destino': request.email_destino or os.getenv('EMAIL_TO', ''),
            'envio_automatico': request.envio_automatico,
            'incluir_resumen': request.incluir_resumen,
            'incluir_detalle': request.incluir_detalle
        }

        if not _guardar_preferencias(preferencias):
            raise HTTPException(status_code=500, detail="Error guardando preferencias")

        logger.info(f"Preferencias actualizadas: habilitado={request.habilitado}, tipo={request.tipo}")

        return PreferenciasNotificacionResponse(
            success=True,
            message="Preferencias actualizadas correctamente",
            preferencias=preferencias
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando preferencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/suscribir",
    response_model=PreferenciasNotificacionResponse,
    summary="Suscribirse a notificaciones",
    description="Activa las notificaciones con la configuración actual."
)
async def suscribir_notificaciones():
    """
    Activa las notificaciones con la configuración actual.

    Equivale a habilitar las notificaciones manteniendo el resto de la configuración.
    """
    try:
        logger.info("API: Suscribiendo a notificaciones")

        preferencias = _cargar_preferencias()
        preferencias['habilitado'] = True

        if not _guardar_preferencias(preferencias):
            raise HTTPException(status_code=500, detail="Error guardando preferencias")

        return PreferenciasNotificacionResponse(
            success=True,
            message="Suscrito a notificaciones correctamente",
            preferencias=preferencias
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suscribiendo a notificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/desuscribir",
    response_model=PreferenciasNotificacionResponse,
    summary="Desuscribirse de notificaciones",
    description="Desactiva las notificaciones."
)
async def desuscribir_notificaciones():
    """
    Desactiva las notificaciones.

    Equivale a deshabilitar las notificaciones manteniendo el resto de la configuración.
    """
    try:
        logger.info("API: Desuscribiendo de notificaciones")

        preferencias = _cargar_preferencias()
        preferencias['habilitado'] = False

        if not _guardar_preferencias(preferencias):
            raise HTTPException(status_code=500, detail="Error guardando preferencias")

        return PreferenciasNotificacionResponse(
            success=True,
            message="Desuscrito de notificaciones correctamente",
            preferencias=preferencias
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error desuscribiendo de notificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


