# api/services.py
"""
Servicios de negocio para la API REST.
Encapsula la lógica del procesamiento de resúmenes de tarjetas.
"""

import os
import csv
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from constants import (
    CARPETA_RESUMENES,
    CATEGORIAS_CONSUMOS,
    CATEGORIAS_ORDEN,
    CATEGORIA_DEFAULT
)

# Importar funciones del módulo principal
import main as processor

logger = logging.getLogger(__name__)


class ReporteService:
    """Servicio para generación de reportes."""

    def __init__(self):
        self.carpeta_resumenes = CARPETA_RESUMENES
        self.password_pdf = os.getenv('PDF_PASSWORD', '30311931')

    def generar_reporte(self, enviar_email: bool = False) -> Dict:
        """
        Genera el reporte procesando todos los PDFs en la carpeta de resúmenes.

        Args:
            enviar_email: Si es True, envía el reporte por email al finalizar

        Returns:
            Dict con el resultado del procesamiento
        """
        logger.info("Iniciando generación de reporte via API...")

        # Validar que existe la carpeta de resúmenes
        if not os.path.exists(self.carpeta_resumenes):
            logger.error(f"Carpeta de resúmenes no encontrada: {self.carpeta_resumenes}")
            return {
                'success': False,
                'message': f"Carpeta de resúmenes no encontrada: {self.carpeta_resumenes}",
                'total_consumos': 0,
                'total_archivos_procesados': 0,
                'archivos_con_error': [],
                'cotizacion_dolar': None,
                'fecha_proceso': datetime.now().isoformat(),
                'resumen_por_categoria': [],
                'resumen_por_moneda': {}
            }

        # Preparar carpeta temporal para debug
        carpeta_tmp = os.path.join(self.carpeta_resumenes, 'tmp_debug')
        os.makedirs(carpeta_tmp, exist_ok=True)

        # Buscar archivos PDF
        archivos_pdf = [f for f in os.listdir(self.carpeta_resumenes) if f.lower().endswith('.pdf')]
        logger.info(f"Se encontraron {len(archivos_pdf)} archivos PDF")

        if not archivos_pdf:
            return {
                'success': False,
                'message': "No se encontraron archivos PDF para procesar",
                'total_consumos': 0,
                'total_archivos_procesados': 0,
                'archivos_con_error': [],
                'cotizacion_dolar': None,
                'fecha_proceso': datetime.now().isoformat(),
                'resumen_por_categoria': [],
                'resumen_por_moneda': {}
            }

        # Procesar cada PDF
        consumos_totales = []
        archivos_procesados = 0
        archivos_con_error = []

        for nombre_archivo in archivos_pdf:
            ruta_completa = os.path.join(self.carpeta_resumenes, nombre_archivo)
            try:
                consumos = processor.procesar_archivo_pdf(
                    ruta_completa, nombre_archivo, self.password_pdf, carpeta_tmp
                )
                if consumos:
                    consumos_totales.extend(consumos)
                    archivos_procesados += 1
                else:
                    archivos_con_error.append(nombre_archivo)
            except Exception as e:
                logger.error(f"Error procesando {nombre_archivo}: {e}")
                archivos_con_error.append(nombre_archivo)

        # Obtener cotización del dólar
        cotizacion_dolar = processor.obtener_cotizacion_dolar_oficial()

        # Procesar duplicados
        if consumos_totales:
            unique_consumos = processor.procesar_duplicados(consumos_totales)
            consumos_a_guardar = [r for r in unique_consumos if r.get('duplicado') != 'ERROR_DUPLICADO_ARCHIVO']

            # Guardar CSV
            processor.guardar_csv(consumos_a_guardar, cotizacion_dolar)

            # Calcular resumen por categoría
            resumen_categorias = self._calcular_resumen_categorias(consumos_a_guardar)
            resumen_monedas = self._calcular_resumen_monedas(consumos_a_guardar)

            # Enviar email si se solicitó
            if enviar_email:
                from notifiers import send_notification
                send_notification(consumos_a_guardar, cotizacion_dolar)

            # Limpiar archivos temporales
            if os.path.exists(carpeta_tmp):
                shutil.rmtree(carpeta_tmp)

            return {
                'success': True,
                'message': f"Reporte generado exitosamente con {len(consumos_a_guardar)} consumos",
                'total_consumos': len(consumos_a_guardar),
                'total_archivos_procesados': archivos_procesados,
                'archivos_con_error': archivos_con_error,
                'cotizacion_dolar': cotizacion_dolar,
                'fecha_proceso': datetime.now().isoformat(),
                'resumen_por_categoria': resumen_categorias,
                'resumen_por_moneda': resumen_monedas
            }

        return {
            'success': False,
            'message': "No se encontraron consumos para procesar",
            'total_consumos': 0,
            'total_archivos_procesados': archivos_procesados,
            'archivos_con_error': archivos_con_error,
            'cotizacion_dolar': cotizacion_dolar,
            'fecha_proceso': datetime.now().isoformat(),
            'resumen_por_categoria': [],
            'resumen_por_moneda': {}
        }

    def _calcular_resumen_categorias(self, consumos: List[Dict]) -> List[Dict]:
        """Calcula el resumen de consumos por categoría."""
        categorias_count = {}
        categorias_monto = {}
        total_monto = sum(c['monto'] for c in consumos)

        for row in consumos:
            cat = row.get('categoria', CATEGORIA_DEFAULT)
            categorias_count[cat] = categorias_count.get(cat, 0) + 1
            categorias_monto[cat] = categorias_monto.get(cat, 0) + row['monto']

        resumen = []
        for cat in CATEGORIAS_ORDEN:
            count = categorias_count.get(cat, 0)
            monto = categorias_monto.get(cat, 0)
            porcentaje = (monto / total_monto * 100) if total_monto > 0 else 0
            resumen.append({
                'categoria': cat,
                'cantidad': count,
                'monto_total': round(monto, 2),
                'porcentaje': round(porcentaje, 2)
            })

        return resumen

    def _calcular_resumen_monedas(self, consumos: List[Dict]) -> Dict:
        """Calcula el resumen de consumos por moneda."""
        resumen = {'ARS': {'cantidad': 0, 'monto': 0}, 'USD': {'cantidad': 0, 'monto': 0}}

        for row in consumos:
            moneda = row.get('moneda', 'ARS')
            if moneda not in resumen:
                resumen[moneda] = {'cantidad': 0, 'monto': 0}
            resumen[moneda]['cantidad'] += 1
            resumen[moneda]['monto'] += row['monto']

        # Redondear montos
        for moneda in resumen:
            resumen[moneda]['monto'] = round(resumen[moneda]['monto'], 2)

        return resumen


class ArchivoService:
    """Servicio para gestión de archivos PDF."""

    def __init__(self):
        self.carpeta_resumenes = CARPETA_RESUMENES

    def listar_archivos(self) -> List[Dict]:
        """Lista todos los archivos PDF en la carpeta de resúmenes."""
        if not os.path.exists(self.carpeta_resumenes):
            return []

        archivos = []
        for nombre in os.listdir(self.carpeta_resumenes):
            if nombre.lower().endswith('.pdf'):
                ruta = os.path.join(self.carpeta_resumenes, nombre)
                stat = os.stat(ruta)
                archivos.append({
                    'nombre': nombre,
                    'tamaño_kb': round(stat.st_size / 1024, 2),
                    'fecha_modificacion': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        return archivos

    async def guardar_archivo(self, archivo, nombre: str) -> Tuple[bool, str, float]:
        """
        Guarda un archivo PDF en la carpeta de resúmenes.

        Args:
            archivo: Archivo subido (UploadFile de FastAPI)
            nombre: Nombre del archivo

        Returns:
            Tuple (success, message, tamaño_kb)
        """
        # Asegurar que existe la carpeta
        os.makedirs(self.carpeta_resumenes, exist_ok=True)

        # Validar extensión
        if not nombre.lower().endswith('.pdf'):
            return False, "El archivo debe ser un PDF", 0

        ruta_destino = os.path.join(self.carpeta_resumenes, nombre)

        try:
            contenido = await archivo.read()
            with open(ruta_destino, 'wb') as f:
                f.write(contenido)

            tamaño_kb = round(len(contenido) / 1024, 2)
            logger.info(f"Archivo guardado: {nombre} ({tamaño_kb} KB)")
            return True, f"Archivo {nombre} guardado exitosamente", tamaño_kb

        except Exception as e:
            logger.error(f"Error guardando archivo {nombre}: {e}")
            return False, f"Error guardando archivo: {str(e)}", 0

    def eliminar_archivo(self, nombre: str) -> Tuple[bool, str]:
        """
        Elimina un archivo PDF de la carpeta de resúmenes.

        Args:
            nombre: Nombre del archivo a eliminar

        Returns:
            Tuple (success, message)
        """
        ruta = os.path.join(self.carpeta_resumenes, nombre)

        if not os.path.exists(ruta):
            return False, f"Archivo no encontrado: {nombre}"

        if not nombre.lower().endswith('.pdf'):
            return False, "Solo se pueden eliminar archivos PDF"

        try:
            os.remove(ruta)
            logger.info(f"Archivo eliminado: {nombre}")
            return True, f"Archivo {nombre} eliminado exitosamente"
        except Exception as e:
            logger.error(f"Error eliminando archivo {nombre}: {e}")
            return False, f"Error eliminando archivo: {str(e)}"


class CotizacionService:
    """Servicio para obtener cotizaciones."""

    def obtener_cotizacion_dolar(self) -> Dict:
        """Obtiene la cotización actual del dólar oficial."""
        try:
            cotizacion = processor.obtener_cotizacion_dolar_oficial()
            return {
                'success': True,
                'cotizacion_venta': cotizacion,
                'cotizacion_compra': None,  # Podría extenderse para obtener compra
                'fuente': 'dolarapi.com',
                'fecha_consulta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo cotización: {e}")
            return {
                'success': False,
                'cotizacion_venta': None,
                'cotizacion_compra': None,
                'fuente': 'dolarapi.com',
                'fecha_consulta': datetime.now().isoformat()
            }


class NotificacionService:
    """Servicio para envío de notificaciones."""

    def enviar_email(self, consumos: List[Dict] = None, cotizacion: float = None) -> Dict:
        """
        Envía el reporte por email.

        Si no se proporcionan consumos, intenta leer del CSV existente.
        """
        from notifiers import send_notification

        # Si no hay consumos, intentar leer del CSV
        if consumos is None:
            consumos = self._leer_consumos_csv()

        if not consumos:
            return {
                'success': False,
                'message': "No hay consumos para enviar. Genere un reporte primero.",
                'tipo': 'email',
                'destinatario': None
            }

        # Obtener cotización si no se proporcionó
        if cotizacion is None:
            cotizacion = processor.obtener_cotizacion_dolar_oficial()

        # Enviar notificación
        result = send_notification(consumos, cotizacion)
        destinatario = os.getenv('EMAIL_TO', 'No configurado')

        return {
            'success': result,
            'message': "Email enviado exitosamente" if result else "Error enviando email",
            'tipo': 'email',
            'destinatario': destinatario if result else None
        }

    def _leer_consumos_csv(self) -> List[Dict]:
        """Lee los consumos del archivo CSV existente."""
        archivo_csv = 'consumos_totales.csv'

        if not os.path.exists(archivo_csv):
            return []

        consumos = []
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                # Saltar líneas de comentario
                lineas = f.readlines()
                contenido = ''.join([l for l in lineas if not l.startswith('#')])

            import io
            reader = csv.DictReader(io.StringIO(contenido))
            for row in reader:
                consumos.append({
                    'fecha': row.get('fecha', ''),
                    'descripcion': row.get('descripcion', ''),
                    'monto': float(row.get('monto', 0)),
                    'moneda': row.get('moneda', 'ARS'),
                    'tarjeta': row.get('tarjeta', ''),
                    'numero_tarjeta': row.get('numero_tarjeta', ''),
                    'banco': row.get('banco', ''),
                    'categoria': row.get('categoria', CATEGORIA_DEFAULT),
                    'duplicado': row.get('duplicado', 'NO')
                })
        except Exception as e:
            logger.error(f"Error leyendo CSV: {e}")

        return consumos


class CategoriaService:
    """Servicio para gestión de categorías."""

    def listar_categorias(self) -> List[Dict]:
        """Lista todas las categorías disponibles."""
        categorias = []

        for nombre in CATEGORIAS_ORDEN:
            palabras = CATEGORIAS_CONSUMOS.get(nombre, [])
            categorias.append({
                'nombre': nombre,
                'palabras_clave': palabras if nombre != CATEGORIA_DEFAULT else []
            })

        return categorias


class ConsumosService:
    """Servicio para consulta de consumos."""

    def obtener_consumos(self, moneda: str = None, categoria: str = None) -> List[Dict]:
        """
        Obtiene los consumos del último reporte generado.

        Args:
            moneda: Filtrar por moneda (ARS, USD)
            categoria: Filtrar por categoría

        Returns:
            Lista de consumos filtrados
        """
        notif_service = NotificacionService()
        consumos = notif_service._leer_consumos_csv()

        # Aplicar filtros
        if moneda:
            consumos = [c for c in consumos if c.get('moneda', '').upper() == moneda.upper()]

        if categoria:
            consumos = [c for c in consumos if c.get('categoria', '').lower() == categoria.lower()]

        return consumos

