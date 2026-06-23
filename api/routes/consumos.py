# api/routes/consumos.py
"""
Endpoints para consulta de consumos.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

from api.schemas import (
    ConsumoListResponse,
    ConsumoResponse,
    ErrorResponse,
    ConsumosPorCategoriaResponse,
    ResumenCategoriasResponse
)
from api.services import ConsumosService, CotizacionService
from constants import CATEGORIAS_ORDEN

router = APIRouter(prefix="/consumos", tags=["Consumos"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=ConsumoListResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Obtener consumos",
    description="Obtiene los consumos del último reporte generado con filtros opcionales."
)
async def obtener_consumos(
    moneda: Optional[str] = Query(None, description="Filtrar por moneda (ARS, USD)"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría")
):
    """
    Obtiene los consumos del último reporte generado.

    Parámetros de filtro opcionales:
    - **moneda**: Filtrar por moneda (ARS, USD)
    - **categoria**: Filtrar por categoría (Utilities, Food, etc.)

    Retorna la lista de consumos con la cotización del dólar utilizada.
    """
    try:
        logger.info(f"API: Consultando consumos (moneda={moneda}, categoria={categoria})")

        service = ConsumosService()
        consumos = service.obtener_consumos(moneda=moneda, categoria=categoria)

        if not consumos:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron consumos. Genere un reporte primero."
            )

        # Obtener cotización actual
        cot_service = CotizacionService()
        cot_result = cot_service.obtener_cotizacion_dolar()
        cotizacion = cot_result.get('cotizacion_venta')

        return ConsumoListResponse(
            success=True,
            message=f"Se encontraron {len(consumos)} consumos",
            total=len(consumos),
            cotizacion_dolar=cotizacion,
            fecha_proceso=datetime.now().isoformat(),
            consumos=[ConsumoResponse(**c) for c in consumos]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo consumos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/resumen",
    summary="Resumen de consumos",
    description="Obtiene un resumen estadístico de los consumos."
)
async def resumen_consumos():
    """
    Obtiene un resumen estadístico de los consumos.

    Incluye:
    - Total de consumos por moneda
    - Total de consumos por categoría
    - Montos totales
    """
    try:
        logger.info("API: Consultando resumen de consumos")

        service = ConsumosService()
        consumos = service.obtener_consumos()

        if not consumos:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron consumos. Genere un reporte primero."
            )

        # Calcular resumen por moneda
        por_moneda = {}
        for c in consumos:
            moneda = c.get('moneda', 'ARS')
            if moneda not in por_moneda:
                por_moneda[moneda] = {'cantidad': 0, 'monto_total': 0}
            por_moneda[moneda]['cantidad'] += 1
            por_moneda[moneda]['monto_total'] += c['monto']

        # Calcular resumen por categoría
        por_categoria = {}
        for c in consumos:
            cat = c.get('categoria', 'Other')
            if cat not in por_categoria:
                por_categoria[cat] = {'cantidad': 0, 'monto_total': 0}
            por_categoria[cat]['cantidad'] += 1
            por_categoria[cat]['monto_total'] += c['monto']

        # Redondear montos
        for k in por_moneda:
            por_moneda[k]['monto_total'] = round(por_moneda[k]['monto_total'], 2)
        for k in por_categoria:
            por_categoria[k]['monto_total'] = round(por_categoria[k]['monto_total'], 2)

        return {
            "success": True,
            "total_consumos": len(consumos),
            "por_moneda": por_moneda,
            "por_categoria": por_categoria,
            "fecha_consulta": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo resumen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/categorias",
    response_model=ResumenCategoriasResponse,
    summary="Resumen de consumos por categorías",
    description="Obtiene un resumen de consumos agrupados por todas las categorías."
)
async def resumen_por_categorias():
    """
    Obtiene un resumen de consumos agrupados por categoría.

    Incluye:
    - Cantidad de consumos por categoría
    - Monto total por categoría
    - Porcentaje del total
    """
    try:
        logger.info("API: Consultando resumen por categorías")

        service = ConsumosService()
        consumos = service.obtener_consumos()

        if not consumos:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron consumos. Genere un reporte primero."
            )

        # Obtener cotización
        cot_service = CotizacionService()
        cot_result = cot_service.obtener_cotizacion_dolar()
        cotizacion = cot_result.get('cotizacion_venta')

        # Calcular totales por categoría
        total_general = sum(c['monto'] for c in consumos)
        categorias_resumen = []

        for categoria in CATEGORIAS_ORDEN:
            consumos_cat = [c for c in consumos if c.get('categoria') == categoria]
            if consumos_cat:
                monto_total = sum(c['monto'] for c in consumos_cat)
                porcentaje = (monto_total / total_general * 100) if total_general > 0 else 0
                categorias_resumen.append({
                    'categoria': categoria,
                    'cantidad': len(consumos_cat),
                    'monto_total': round(monto_total, 2),
                    'porcentaje': round(porcentaje, 2)
                })

        return ResumenCategoriasResponse(
            success=True,
            message=f"Resumen de {len(categorias_resumen)} categorías",
            total_consumos=len(consumos),
            monto_total_general=round(total_general, 2),
            cotizacion_dolar=cotizacion,
            fecha_consulta=datetime.now().isoformat(),
            categorias=categorias_resumen
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo resumen por categorías: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/categorias/{categoria}",
    response_model=ConsumosPorCategoriaResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Consumos por categoría específica",
    description="Obtiene todos los consumos de una categoría específica."
)
async def consumos_por_categoria(
    categoria: str,
    moneda: Optional[str] = Query(None, description="Filtrar por moneda (ARS, USD)")
):
    """
    Obtiene los consumos de una categoría específica.

    Parámetros:
    - **categoria**: Nombre de la categoría (Utilities, Food, etc.)
    - **moneda**: Filtro opcional por moneda

    Retorna la lista de consumos con el total y porcentaje.
    """
    try:
        # Normalizar nombre de categoría
        categoria_normalizada = categoria.capitalize()
        if categoria_normalizada not in CATEGORIAS_ORDEN:
            raise HTTPException(
                status_code=400,
                detail=f"Categoría '{categoria}' no válida. Categorías disponibles: {', '.join(CATEGORIAS_ORDEN)}"
            )

        logger.info(f"API: Consultando consumos de categoría '{categoria_normalizada}' (moneda={moneda})")

        service = ConsumosService()
        todos_consumos = service.obtener_consumos()

        if not todos_consumos:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron consumos. Genere un reporte primero."
            )

        # Filtrar por categoría
        consumos_categoria = [c for c in todos_consumos if c.get('categoria') == categoria_normalizada]

        # Filtrar por moneda si se especificó
        if moneda:
            consumos_categoria = [c for c in consumos_categoria if c.get('moneda', '').upper() == moneda.upper()]

        if not consumos_categoria:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron consumos para la categoría '{categoria_normalizada}'"
            )

        # Calcular totales
        total_general = sum(c['monto'] for c in todos_consumos)
        monto_categoria = sum(c['monto'] for c in consumos_categoria)
        porcentaje = (monto_categoria / total_general * 100) if total_general > 0 else 0

        # Calcular monto pesificado (para USD)
        monto_pesificado = None
        consumos_usd = [c for c in consumos_categoria if c.get('moneda') == 'USD']
        if consumos_usd:
            cot_service = CotizacionService()
            cot_result = cot_service.obtener_cotizacion_dolar()
            cotizacion = cot_result.get('cotizacion_venta')
            if cotizacion:
                monto_usd = sum(c['monto'] for c in consumos_usd)
                monto_ars = sum(c['monto'] for c in consumos_categoria if c.get('moneda') == 'ARS')
                monto_pesificado = round(monto_ars + (monto_usd * cotizacion), 2)

        return ConsumosPorCategoriaResponse(
            success=True,
            message=f"Se encontraron {len(consumos_categoria)} consumos en '{categoria_normalizada}'",
            categoria=categoria_normalizada,
            total_consumos=len(consumos_categoria),
            monto_total=round(monto_categoria, 2),
            monto_total_pesificado=monto_pesificado,
            porcentaje_del_total=round(porcentaje, 2),
            consumos=[ConsumoResponse(**c) for c in consumos_categoria]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo consumos por categoría: {e}")
        raise HTTPException(status_code=500, detail=str(e))


