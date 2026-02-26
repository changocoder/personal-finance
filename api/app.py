# api/app.py
"""
Aplicación principal de la API REST.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from api.schemas import HealthResponse
from api.routes import (
    reportes_router,
    archivos_router,
    cotizacion_router,
    notificaciones_router,
    categorias_router,
    consumos_router
)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Versión de la API
API_VERSION = "1.0.0"

# Crear aplicación FastAPI
app = FastAPI(
    title="Personal Finance API",
    description="""
## API REST para procesamiento de resúmenes de tarjetas de crédito

Esta API permite:

* 📄 **Cargar resúmenes**: Subir archivos PDF de resúmenes de tarjetas
* 📊 **Generar reportes**: Procesar los PDFs y extraer consumos
* 💰 **Consultar cotización**: Obtener cotización del dólar oficial
* 📧 **Enviar notificaciones**: Enviar reportes por email
* 🏷️ **Categorizar gastos**: Clasificación automática de consumos

### Flujo típico de uso:

1. Cargar resúmenes PDF (`POST /archivos/upload`)
2. Generar reporte (`POST /reportes/generar`)
3. Consultar consumos (`GET /consumos`)
4. Enviar por email (`POST /notificaciones/enviar`)

### Autores
- Personal Finance App Team
    """,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Reportes", "description": "Generación y consulta de reportes de consumos"},
        {"name": "Archivos", "description": "Gestión de archivos PDF de resúmenes"},
        {"name": "Consumos", "description": "Consulta de consumos procesados"},
        {"name": "Cotización", "description": "Cotización del dólar oficial"},
        {"name": "Notificaciones", "description": "Envío de reportes por email"},
        {"name": "Categorías", "description": "Categorías de clasificación de consumos"},
    ]
)

# Configurar CORS para permitir acceso desde cualquier origen (ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(reportes_router)
app.include_router(archivos_router)
app.include_router(consumos_router)
app.include_router(cotizacion_router)
app.include_router(notificaciones_router)
app.include_router(categorias_router)


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz con información básica de la API."""
    return {
        "name": "Personal Finance API",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Verifica que la API esté funcionando correctamente.
    """
    logger.debug("Health check solicitado")
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        timestamp=datetime.now().isoformat()
    )


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación."""
    logger.info(f"🚀 Personal Finance API v{API_VERSION} iniciada")
    logger.info("📚 Documentación disponible en /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación."""
    logger.info("👋 Personal Finance API cerrada")

