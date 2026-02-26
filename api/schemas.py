# api/schemas.py
"""
Esquemas Pydantic para la API REST.
Define los modelos de request y response para los endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# =============================================================================
# SCHEMAS DE CONSUMOS
# =============================================================================

class ConsumoBase(BaseModel):
    """Esquema base para un consumo."""
    fecha: str = Field(..., description="Fecha del consumo (formato DD.MM.YY)")
    descripcion: str = Field(..., description="Descripción del consumo")
    monto: float = Field(..., description="Monto del consumo")
    moneda: str = Field(..., description="Moneda del consumo (ARS, USD, BRL)")
    tarjeta: str = Field(..., description="Tipo de tarjeta (VISA, Mastercard)")
    numero_tarjeta: Optional[str] = Field(None, description="Número de tarjeta")
    banco: Optional[str] = Field(None, description="Banco emisor")
    categoria: str = Field(..., description="Categoría del consumo")


class ConsumoResponse(ConsumoBase):
    """Esquema de respuesta para un consumo."""
    monto_ars: Optional[float] = Field(None, description="Monto pesificado (solo para USD)")
    duplicado: str = Field(default="NO", description="Indicador de duplicado")
    archivo: Optional[str] = Field(None, description="Archivo de origen")


class ConsumoListResponse(BaseModel):
    """Respuesta con lista de consumos."""
    success: bool
    message: str
    total: int
    cotizacion_dolar: Optional[float] = None
    fecha_proceso: str
    consumos: List[ConsumoResponse]


# =============================================================================
# SCHEMAS DE REPORTE
# =============================================================================

class ReporteRequest(BaseModel):
    """Request para generar un reporte."""
    enviar_email: bool = Field(default=False, description="Enviar reporte por email al finalizar")


class ResumenCategoria(BaseModel):
    """Resumen de consumos por categoría."""
    categoria: str
    cantidad: int
    monto_total: float
    porcentaje: float


class ReporteResponse(BaseModel):
    """Respuesta de generación de reporte."""
    success: bool
    message: str
    total_consumos: int
    total_archivos_procesados: int
    archivos_con_error: List[str] = []
    cotizacion_dolar: Optional[float] = None
    fecha_proceso: str
    resumen_por_categoria: List[ResumenCategoria] = []
    resumen_por_moneda: dict = {}


# =============================================================================
# SCHEMAS DE ARCHIVOS
# =============================================================================

class ArchivoInfo(BaseModel):
    """Información de un archivo PDF."""
    nombre: str
    tamaño_kb: float
    fecha_modificacion: str


class ArchivoListResponse(BaseModel):
    """Respuesta con lista de archivos."""
    success: bool
    total: int
    archivos: List[ArchivoInfo]


class UploadResponse(BaseModel):
    """Respuesta de carga de archivo."""
    success: bool
    message: str
    archivo: str
    tamaño_kb: float


# =============================================================================
# SCHEMAS DE COTIZACIÓN
# =============================================================================

class CotizacionResponse(BaseModel):
    """Respuesta de cotización del dólar."""
    success: bool
    cotizacion_venta: Optional[float] = None
    cotizacion_compra: Optional[float] = None
    fuente: str = "dolarapi.com"
    fecha_consulta: str


# =============================================================================
# SCHEMAS DE NOTIFICACIÓN
# =============================================================================

class NotificacionRequest(BaseModel):
    """Request para enviar notificación."""
    tipo: str = Field(default="email", description="Tipo de notificación (email)")


class PreferenciasNotificacionRequest(BaseModel):
    """Request para configurar preferencias de notificación."""
    habilitado: bool = Field(default=True, description="Habilitar/deshabilitar notificaciones")
    tipo: str = Field(default="email", description="Tipo de notificación (email)")
    email_destino: Optional[str] = Field(None, description="Email de destino")
    envio_automatico: bool = Field(default=False, description="Enviar automáticamente después de generar reporte")
    incluir_resumen: bool = Field(default=True, description="Incluir resumen por categorías")
    incluir_detalle: bool = Field(default=True, description="Incluir detalle de consumos")


class PreferenciasNotificacionResponse(BaseModel):
    """Respuesta con preferencias de notificación."""
    success: bool
    message: str
    preferencias: dict


class NotificacionResponse(BaseModel):
    """Respuesta de envío de notificación."""
    success: bool
    message: str
    tipo: str
    destinatario: Optional[str] = None


# =============================================================================
# SCHEMAS DE CATEGORÍAS
# =============================================================================

class CategoriaInfo(BaseModel):
    """Información de una categoría."""
    nombre: str
    palabras_clave: List[str]


class CategoriaListResponse(BaseModel):
    """Respuesta con lista de categorías."""
    success: bool
    total: int
    categorias: List[CategoriaInfo]


class ConsumosPorCategoriaResponse(BaseModel):
    """Respuesta con consumos agrupados por categoría."""
    success: bool
    message: str
    categoria: str
    total_consumos: int
    monto_total: float
    monto_total_pesificado: Optional[float] = None
    porcentaje_del_total: float
    consumos: List[ConsumoResponse]


class ResumenCategoriasResponse(BaseModel):
    """Respuesta con resumen de todas las categorías."""
    success: bool
    message: str
    total_consumos: int
    monto_total_general: float
    cotizacion_dolar: Optional[float] = None
    fecha_consulta: str
    categorias: List[dict]


# =============================================================================
# SCHEMAS GENERALES
# =============================================================================

class HealthResponse(BaseModel):
    """Respuesta del health check."""
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Respuesta de error."""
    success: bool = False
    error: str
    detail: Optional[str] = None

