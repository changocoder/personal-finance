# api/routes/reportes.py
"""
Endpoints para generación de reportes.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import os

from api.schemas import ReporteRequest, ReporteResponse, ErrorResponse, ResumenCategoria
from api.services import ReporteService

router = APIRouter(prefix="/reportes", tags=["Reportes"])
logger = logging.getLogger(__name__)


@router.post(
    "/generar",
    response_model=ReporteResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Generar reporte de consumos",
    description="Procesa todos los PDFs y genera el reporte de consumos."
)
async def generar_reporte(request: ReporteRequest = ReporteRequest()):
    """
    Genera un reporte procesando todos los PDFs en la carpeta de resúmenes.

    Parámetros:
    - **enviar_email**: Si es True, envía el reporte por email al finalizar

    Retorna el resumen del procesamiento incluyendo:
    - Total de consumos extraídos
    - Archivos procesados y con error
    - Cotización del dólar utilizada
    - Resumen por categoría y moneda
    """
    try:
        logger.info(f"API: Solicitud de generación de reporte (enviar_email={request.enviar_email})")

        service = ReporteService()
        resultado = service.generar_reporte(enviar_email=request.enviar_email)

        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['message'])

        # Convertir resumen de categorías al schema
        resumen_categorias = [
            ResumenCategoria(**cat) for cat in resultado.get('resumen_por_categoria', [])
        ]

        return ReporteResponse(
            success=resultado['success'],
            message=resultado['message'],
            total_consumos=resultado['total_consumos'],
            total_archivos_procesados=resultado['total_archivos_procesados'],
            archivos_con_error=resultado.get('archivos_con_error', []),
            cotizacion_dolar=resultado.get('cotizacion_dolar'),
            fecha_proceso=resultado.get('fecha_proceso', datetime.now().isoformat()),
            resumen_por_categoria=resumen_categorias,
            resumen_por_moneda=resultado.get('resumen_por_moneda', {})
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/ultimo",
    summary="Obtener último reporte",
    description="Obtiene información del último reporte generado."
)
async def obtener_ultimo_reporte():
    """
    Obtiene información del último reporte generado.

    Retorna:
    - Fecha de generación
    - Cantidad de consumos
    - Archivo CSV generado
    """
    archivo_csv = 'consumos_totales.csv'

    if not os.path.exists(archivo_csv):
        raise HTTPException(
            status_code=404,
            detail="No se encontró ningún reporte. Genere uno primero con POST /reportes/generar"
        )

    try:
        stat = os.stat(archivo_csv)
        fecha_modificacion = datetime.fromtimestamp(stat.st_mtime)

        # Contar líneas (consumos)
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            lineas = [l for l in f.readlines() if not l.startswith('#') and l.strip()]
            # Restar 1 por el header
            total_consumos = max(0, len(lineas) - 1)

        return {
            "success": True,
            "archivo": archivo_csv,
            "tamaño_kb": round(stat.st_size / 1024, 2),
            "fecha_generacion": fecha_modificacion.isoformat(),
            "total_consumos": total_consumos
        }

    except Exception as e:
        logger.error(f"Error obteniendo último reporte: {e}")
        raise HTTPException(status_code=500, detail=str(e))

