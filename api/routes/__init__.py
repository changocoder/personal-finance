# api/routes/__init__.py
"""
Rutas de la API REST.
"""

from .reportes import router as reportes_router
from .archivos import router as archivos_router
from .cotizacion import router as cotizacion_router
from .notificaciones import router as notificaciones_router
from .categorias import router as categorias_router
from .consumos import router as consumos_router

__all__ = [
    'reportes_router',
    'archivos_router',
    'cotizacion_router',
    'notificaciones_router',
    'categorias_router',
    'consumos_router'
]

