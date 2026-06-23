# api/routes/archivos.py
"""
Endpoints para gestión de archivos PDF.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import logging

from api.schemas import ArchivoListResponse, ArchivoInfo, UploadResponse, ErrorResponse
from api.services import ArchivoService

router = APIRouter(prefix="/archivos", tags=["Archivos"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=ArchivoListResponse,
    summary="Listar archivos PDF",
    description="Lista todos los archivos PDF disponibles en la carpeta de resúmenes."
)
async def listar_archivos():
    """
    Lista todos los archivos PDF cargados.

    Retorna información de cada archivo:
    - Nombre del archivo
    - Tamaño en KB
    - Fecha de modificación
    """
    logger.info("API: Listando archivos PDF")
    service = ArchivoService()
    archivos = service.listar_archivos()

    return ArchivoListResponse(
        success=True,
        total=len(archivos),
        archivos=[ArchivoInfo(**a) for a in archivos]
    )


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Cargar archivo PDF",
    description="Carga un archivo PDF de resumen de tarjeta."
)
async def cargar_archivo(archivo: UploadFile = File(...)):
    """
    Carga un archivo PDF de resumen de tarjeta.

    El archivo debe ser un PDF válido.
    """
    try:
        logger.info(f"API: Cargando archivo {archivo.filename}")

        if not archivo.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

        service = ArchivoService()
        success, message, tamaño = await service.guardar_archivo(archivo, archivo.filename)

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return UploadResponse(
            success=True,
            message=message,
            archivo=archivo.filename,
            tamaño_kb=tamaño
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cargando archivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/upload-multiple",
    summary="Cargar múltiples archivos PDF",
    description="Carga múltiples archivos PDF de resúmenes de tarjetas."
)
async def cargar_multiples_archivos(archivos: List[UploadFile] = File(...)):
    """
    Carga múltiples archivos PDF de resúmenes de tarjetas.
    """
    resultados = []
    service = ArchivoService()

    for archivo in archivos:
        try:
            if not archivo.filename.lower().endswith('.pdf'):
                resultados.append({
                    "archivo": archivo.filename,
                    "success": False,
                    "message": "No es un archivo PDF"
                })
                continue

            success, message, tamaño = await service.guardar_archivo(archivo, archivo.filename)
            resultados.append({
                "archivo": archivo.filename,
                "success": success,
                "message": message,
                "tamaño_kb": tamaño if success else 0
            })

        except Exception as e:
            resultados.append({
                "archivo": archivo.filename,
                "success": False,
                "message": str(e)
            })

    exitosos = sum(1 for r in resultados if r['success'])
    return {
        "success": exitosos > 0,
        "total_procesados": len(archivos),
        "exitosos": exitosos,
        "fallidos": len(archivos) - exitosos,
        "resultados": resultados
    }


@router.delete(
    "/{nombre}",
    summary="Eliminar archivo PDF",
    description="Elimina un archivo PDF de la carpeta de resúmenes."
)
async def eliminar_archivo(nombre: str):
    """
    Elimina un archivo PDF.

    Parámetros:
    - **nombre**: Nombre del archivo a eliminar
    """
    logger.info(f"API: Eliminando archivo {nombre}")
    service = ArchivoService()
    success, message = service.eliminar_archivo(nombre)

    if not success:
        raise HTTPException(status_code=404, detail=message)

    return {"success": True, "message": message}

