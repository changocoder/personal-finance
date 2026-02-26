# api/routes/cotizacion.py
"""
Endpoints para cotización del dólar.
"""

from fastapi import APIRouter, HTTPException
import logging

from api.schemas import CotizacionResponse, ErrorResponse
from api.services import CotizacionService

router = APIRouter(prefix="/cotizacion", tags=["Cotización"])
logger = logging.getLogger(__name__)


@router.get(
    "/dolar",
    response_model=CotizacionResponse,
    summary="Obtener cotización del dólar",
    description="Obtiene la cotización actual del dólar oficial (venta) desde dolarapi.com"
)
async def obtener_cotizacion_dolar():
    """
    Obtiene la cotización actual del dólar oficial.

    Retorna:
    - Cotización de venta (la más alta, usada para pesificar)
    - Fuente de la información
    - Fecha/hora de consulta
    """
    try:
        logger.info("API: Consultando cotización del dólar")
        service = CotizacionService()
        resultado = service.obtener_cotizacion_dolar()

        return CotizacionResponse(**resultado)

    except Exception as e:
        logger.error(f"Error obteniendo cotización: {e}")
        raise HTTPException(status_code=500, detail=str(e))

