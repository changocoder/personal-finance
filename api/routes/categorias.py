# api/routes/categorias.py
"""
Endpoints para gestión de categorías de consumos.
"""

from fastapi import APIRouter
import logging

from api.schemas import CategoriaListResponse, CategoriaInfo
from api.services import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorías"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=CategoriaListResponse,
    summary="Listar categorías",
    description="Lista todas las categorías disponibles para clasificación de consumos."
)
async def listar_categorias():
    """
    Lista todas las categorías de consumos disponibles.

    Las categorías son:
    - **Utilities**: Servicios (streaming, telecomunicaciones, seguros)
    - **Investment**: Inversiones (cripto, fondos, bolsa)
    - **Food**: Alimentación (restaurantes, supermercados, delivery)
    - **Household**: Hogar (construcción, electrodomésticos, muebles)
    - **Discretionary**: Gastos discrecionales (ropa, e-commerce, entretenimiento)
    - **Other**: Otros (consumos no clasificados)
    """
    logger.info("API: Listando categorías de consumos")
    service = CategoriaService()
    categorias = service.listar_categorias()

    return CategoriaListResponse(
        success=True,
        total=len(categorias),
        categorias=[CategoriaInfo(**c) for c in categorias]
    )

