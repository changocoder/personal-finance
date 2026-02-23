import os
import re
import csv
import shutil
import logging
import pdfplumber
import urllib.request
import json
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

from constants import (
    CARPETA_RESUMENES,
    ARCHIVO_SALIDA,
    NOMBRE_VARIABLE_ENTORNO,
    PALABRAS_A_EXCLUIR,
    CATEGORIAS_CONSUMOS,
    CATEGORIA_DEFAULT,
    CATEGORIAS_ORDEN
)
from email_sender import enviar_reporte_email

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesamiento_consumos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# COTIZACIÓN DEL DÓLAR
# =============================================================================

def obtener_cotizacion_dolar_oficial():
    """
    Obtiene la cotización del dólar oficial (venta) desde la API de dolarapi.com
    Se usa el valor de venta porque es el más alto y representa el costo real de compra.

    Returns:
        float: Cotización del dólar oficial para venta, o None si falla
    """
    urls = [
        'https://dolarapi.com/v1/dolares/oficial',
        'https://api.bluelytics.com.ar/v2/latest'
    ]

    for url in urls:
        try:
            logger.info(f"Obteniendo cotización del dólar desde: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

                # dolarapi.com format
                if 'venta' in data:
                    cotizacion = float(data['venta'])
                    logger.info(f"✓ Cotización dólar oficial (venta): ${cotizacion:.2f}")
                    return cotizacion

                # bluelytics format
                if 'oficial' in data:
                    cotizacion = float(data['oficial']['value_sell'])
                    logger.info(f"✓ Cotización dólar oficial (venta): ${cotizacion:.2f}")
                    return cotizacion

        except Exception as e:
            logger.warning(f"Error obteniendo cotización de {url}: {e}")
            continue

    logger.error("No se pudo obtener la cotización del dólar. Usando valor por defecto.")
    return None


def pesificar_monto(monto_usd, cotizacion):
    """
    Convierte un monto en USD a ARS usando la cotización proporcionada.

    Args:
        monto_usd (float): Monto en dólares
        cotizacion (float): Cotización del dólar

    Returns:
        float: Monto en pesos argentinos
    """
    if cotizacion is None or monto_usd is None:
        return None
    return round(monto_usd * cotizacion, 2)


# =============================================================================
# UTILIDADES DE PARSING Y LIMPIEZA
# =============================================================================



def clasificar_consumo(descripcion):
    """
    Clasifica un consumo en una categoría basándose en la descripción.

    Args:
        descripcion (str): Descripción del consumo

    Returns:
        str: Categoría del consumo (Utilities, Investment, Food, Household, Discretionary, Other)
    """
    if not descripcion:
        return CATEGORIA_DEFAULT

    desc_upper = descripcion.upper()

    for categoria, palabras_clave in CATEGORIAS_CONSUMOS.items():
        for palabra in palabras_clave:
            if palabra in desc_upper:
                logger.debug(f"Consumo '{descripcion[:40]}' clasificado como '{categoria}' por palabra clave '{palabra}'")
                return categoria

    return CATEGORIA_DEFAULT


def limpiar_monto(monto_str, fecha="", descripcion=""):
    """Limpia y convierte un string de monto a un número flotante."""
    if not isinstance(monto_str, str) or not monto_str.strip():
        logger.debug(f"Monto vacío o inválido: '{monto_str}'")
        return None

    monto_original = monto_str

    # Detectar si el monto termina con guion (formato negativo argentino)
    signo = -1 if monto_str.endswith('-') else 1

    # Limpiar: remover guiones al inicio/final y espacios
    monto_limpio = monto_str.strip().rstrip('-').lstrip('-')

    # Convertir formato argentino (1.234,56) a formato de Python (1234.56)
    # Detectar si tiene puntos como separador de miles
    if monto_limpio.count(',') == 1 and monto_limpio.count('.') > 0:
        # Formato: 1.234,56 (punto para miles, coma para decimales)
        monto_limpio = monto_limpio.replace('.', '').replace(',', '.')
    elif monto_limpio.count(',') > 1:
        # Formato: 1,234,567 (coma para miles, último es decimal)
        partes = monto_limpio.split(',')
        monto_limpio = ''.join(partes[:-1]) + '.' + partes[-1]
    elif monto_limpio.count('.') == 1 and monto_limpio.count(',') == 0:
        # Ya está en formato correcto o tiene solo punto decimal
        pass
    else:
        # Formato sin separadores de miles, solo decimales con coma
        monto_limpio = monto_limpio.replace(',', '.')

    try:
        valor = float(monto_limpio)
        resultado_final = valor * signo if valor > 0 else None

        # Preparar strings seguros para logging
        desc_display = descripcion[:50] if isinstance(descripcion, str) and descripcion else str(descripcion) if descripcion is not None else ''
        if resultado_final is not None:
            logger.debug("Monto convertido - Original: '%s' -> Limpio: '%s' -> Final: %s", monto_original, monto_limpio, resultado_final)
            if fecha and desc_display:
                formatted_monto = f"${resultado_final:>10.2f}"
                logger.info("Consumo [%s] %s | Monto: %s", fecha, desc_display, formatted_monto)
        else:
            # monto convertido pero considerado inválido (0 o negativo)
            logger.debug("Monto convertido - Original: '%s' -> Limpio: '%s' -> Final: None (valor=%s, signo=%s)", monto_original, monto_limpio, valor, signo)
            if fecha and desc_display:
                logger.warning("Consumo [%s] %s | Monto inválido o cero: %s", fecha, desc_display, valor)

        return resultado_final
    except ValueError as e:
        logger.warning(f"Error al convertir monto '{monto_original}': {str(e)}")
        return None


def extraer_datos_tarjeta(texto):
    """
    Extrae el número de tarjeta y banco del texto del resumen.
    """
    numero = None
    banco = None
    # Buscar número de cuenta o tarjeta
    match_num = re.search(r'N[°º]?\s*(?:DE\s*)?(?:CUENTA|Socio|Cuenta)[:\s-]*([0-9]{6,})', texto, re.IGNORECASE)
    if match_num:
        numero = match_num.group(1)
    else:
        # Buscar 9-10 dígitos juntos
        match_num2 = re.search(r'([0-9]{9,12})', texto)
        if match_num2:
            numero = match_num2.group(1)
    # Buscar banco o sucursal
    match_banco = re.search(r'SUCURSAL[:\s-]*([\w\s]+)', texto, re.IGNORECASE)
    if match_banco:
        banco = match_banco.group(1).strip()
        # Limpiar saltos de línea y espacios múltiples
        banco = re.sub(r'[\n\r]+', ' ', banco).strip()
        banco = re.sub(r'\s+', ' ', banco)
    else:
        match_banco2 = re.search(r'BANCO[:\s-]*([\w\s]+)', texto, re.IGNORECASE)
        if match_banco2:
            banco = match_banco2.group(1).strip()
            banco = re.sub(r'[\n\r]+', ' ', banco).strip()
            banco = re.sub(r'\s+', ' ', banco)
    return numero, banco


# =============================================================================
# DETECCIÓN DE MONEDA Y CLASIFICACIÓN
# =============================================================================

def detectar_moneda(descripcion):
    """
    Detecta la moneda del consumo basándose en la descripción.
    Retorna: 'USD', 'BRL' o 'ARS'

    Nota: En formato Galicia (PAIS,MONEDA,monto), los consumos internacionales
    siempre se cobran en USD, independientemente de la moneda original.
    """
    desc_upper = descripcion.upper()

    # Detectar USD explícito
    if ' USD ' in desc_upper or desc_upper.endswith(' USD') or ',USD,' in desc_upper:
        return 'USD'

    # Detectar BRL explícito
    if ' BRL ' in desc_upper or desc_upper.endswith(' BRL') or ',BRL,' in desc_upper:
        return 'BRL'

    # Detectar formato Galicia: (PAIS,MONEDA, monto)
    # En este formato, los consumos internacionales (cualquier país != ARG) se cobran en USD
    match_galicia = re.search(r'\(([A-Z]{3}),(USD|BRL|ARS),', desc_upper)
    if match_galicia:
        pais = match_galicia.group(1)
        moneda_original = match_galicia.group(2)
        # Si el país NO es Argentina, el consumo se cobra en USD (conversión)
        if pais != 'ARG':
            return 'USD'
        # Si es Argentina y la moneda es ARS, es un consumo local
        if moneda_original == 'ARS':
            return 'ARS'
        return moneda_original

    return 'ARS'


# =============================================================================
# PROCESAMIENTO DE TEXTO Y EXTRACCIÓN DE CONSUMOS
# =============================================================================

def procesar_texto_resumen(texto_completo, nombre_tarjeta, numero_tarjeta, banco):
    """
    Extrae consumos de texto de resumen de tarjeta y los devuelve como lista de dicts para CSV.
    """
    consumos = []
    consumos_vistos = set()  # Para evitar duplicados exactos

    def extraer_linea_completa(texto, inicio):
        fin_linea = texto.find('\n', inicio)
        if fin_linea == -1:
            fin_linea = len(texto)
        linea = texto[inicio:fin_linea]
        return linea.replace('\r', '')

    # Patrón original más flexible para capturar todos los consumos
    patron_linea = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
    patron_linea_alt = re.compile(r"^(\d{2}[./-]\d{2}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
    matches = []
    spans_vistos = set()
    for regex in (patron_linea, patron_linea_alt):
        for match in regex.finditer(texto_completo):
            span = match.span()
            if span not in spans_vistos:
                spans_vistos.add(span)
                matches.append(match)
    matches.sort(key=lambda m: m.start())

    logger.info(f"\n{'='*80}")
    logger.info(f"Procesando {nombre_tarjeta} - Total de líneas encontradas: {len(matches)}")
    logger.info(f"{'='*80}")

    consumos_extraidos = 0
    consumos_ars = 0
    consumos_usd = 0
    consumos_brl = 0

    for match in matches:
        fecha = match.group(1)
        descripcion = match.group(2)
        monto_detectado = match.group(3)
        descripcion_limpia = descripcion.strip()

        # Quitar tokens residuales típicos de extracción
        descripcion_limpia = re.sub(r"[\s,]*-0[\s,]*$", "", descripcion_limpia)
        # Normalizar espacios múltiples
        descripcion_limpia = re.sub(r"\s+", " ", descripcion_limpia).strip()

        # Verificar si es una palabra excluida
        if any(palabra in descripcion_limpia.upper() for palabra in PALABRAS_A_EXCLUIR):
            logger.debug(f"Línea excluida [{fecha}] {descripcion_limpia[:60]} (contiene palabra excluida)")
            continue

        # Detectar la moneda basándose en la descripción
        moneda_detectada = detectar_moneda(descripcion_limpia)

        # Limpiar la descripción removiendo indicadores de moneda al final
        descripcion_final = re.sub(r'\s+(USD|BRL|ARS)\s*$', '', descripcion_limpia, flags=re.IGNORECASE).strip()

        linea_completa = extraer_linea_completa(texto_completo, match.start())
        montos_en_linea = re.findall(r'\d[\d.,]*[.,]\d{2}', linea_completa)
        if not montos_en_linea:
            logger.debug(f"Línea sin montos detectados, se omite: {linea_completa[:80]}")
            continue

        monto_para_registro = monto_detectado
        moneda_final = moneda_detectada
        conversion_extranjera = False

        # Detectar si es formato Galicia con consumo internacional (PAIS,MONEDA,monto)
        es_formato_galicia = re.search(r'\([A-Z]{3},(USD|BRL|ARS),', descripcion_limpia.upper())

        # Si es consumo internacional (BRL o formato Galicia extranjero) y hay múltiples montos,
        # el último monto es la conversión a USD
        if moneda_detectada == 'USD' and es_formato_galicia and len(montos_en_linea) > 1:
            monto_convertido = montos_en_linea[-1]
            if monto_convertido != monto_detectado:
                conversion_extranjera = True
                monto_para_registro = monto_convertido
                moneda_final = 'USD'
        elif moneda_detectada == 'BRL' and len(montos_en_linea) > 1:
            monto_convertido = montos_en_linea[-1]
            # Solo aplica conversión si realmente hay un segundo monto distinto o posición posterior
            if montos_en_linea.index(monto_convertido) != 0 or monto_convertido != monto_detectado:
                conversion_extranjera = True
                monto_para_registro = monto_convertido
                moneda_final = 'USD'

        # Crear clave única para evitar duplicados exactos
        clave_consumo = (fecha, descripcion_final, monto_para_registro, moneda_final)
        if clave_consumo in consumos_vistos:
            logger.debug(f"Consumo duplicado ignorado [{fecha}] {descripcion_final[:40]} {moneda_final}")
            continue
        consumos_vistos.add(clave_consumo)

        monto_float = limpiar_monto(monto_para_registro, fecha, descripcion_final)
        if monto_float is not None and abs(monto_float) > 0:
            consumos_extraidos += 1

            # Contadores por moneda
            if moneda_final == 'USD':
                consumos_usd += 1
                if conversion_extranjera:
                    logger.info(
                        "Conversión moneda extranjera→USD [%s] %s | Original %s -> USD %s",
                        fecha,
                        descripcion_final[:60],
                        monto_detectado,
                        monto_para_registro
                    )
            elif moneda_final == 'BRL':
                consumos_brl += 1
            else:
                consumos_ars += 1

            # Log con indicador de moneda
            desc_display = descripcion_final[:50] if descripcion_final else ''
            formatted_monto = f"{moneda_final} {monto_float:>10.2f}"
            logger.info(f"Consumo [{fecha}] {desc_display} | Monto: {formatted_monto}")

            # Clasificar el consumo en una categoría
            categoria = clasificar_consumo(descripcion_final)
            logger.info(f"  -> Categoría: {categoria}")

            consumos.append({
                'fecha': fecha,
                'descripcion': descripcion_final,
                'monto': abs(monto_float),
                'moneda': moneda_final,
                'tarjeta': nombre_tarjeta,
                'numero_tarjeta': numero_tarjeta or '',
                'banco': banco or '',
                'categoria': categoria
            })
        else:
            logger.warning(f"Monto inválido o cero [{fecha}] {descripcion_limpia[:60]} -> {monto_float}")

    logger.info(f"\n--- Resumen de extracción para {nombre_tarjeta} ---")
    logger.info(f"Total consumos: {consumos_extraidos} | ARS: {consumos_ars} | USD: {consumos_usd} | BRL: {consumos_brl}")
    logger.info(f"{'='*80}\n")

    return consumos


# =============================================================================
# PROCESAMIENTO DE PDFs
# =============================================================================

def abrir_pdf(ruta_completa, password_pdf):
    """
    Intenta abrir un PDF, primero sin contraseña y luego con contraseña.

    Returns:
        tuple: (pdf_object, bool_abierto)
    """
    pdf = None
    abierto = False

    try:
        pdf = pdfplumber.open(ruta_completa)
        logger.info("✓ PDF abierto sin necesidad de contraseña.")
        abierto = True
    except Exception as e:
        logger.warning(f"✗ No se pudo abrir sin contraseña: {e}")
        try:
            pdf = pdfplumber.open(ruta_completa, password=password_pdf)
            logger.info("✓ PDF abierto exitosamente con contraseña.")
            abierto = True
        except Exception as e2:
            logger.error(f"✗ Error al abrir con contraseña: {e2}")
            abierto = False

    return pdf, abierto


def extraer_texto_pdf(pdf):
    """Extrae el texto completo de todas las páginas de un PDF."""
    texto_completo = ""
    for pagina in pdf.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto_completo += texto_pagina + "\n"
    return texto_completo


def detectar_tipo_tarjeta(texto):
    """Detecta el tipo de tarjeta basándose en el texto del resumen."""
    if "VISA" in texto[:500]:
        return "VISA"
    elif "MASTERCARD" in texto[:500]:
        return "Mastercard"
    return "Desconocida"


def procesar_archivo_pdf(ruta_completa, nombre_archivo, password_pdf, carpeta_tmp):
    """
    Procesa un archivo PDF individual y retorna la lista de consumos extraídos.
    """
    logger.info(f"\n{'─'*80}")
    logger.info(f"Procesando archivo: {nombre_archivo}")
    logger.info(f"{'─'*80}")

    pdf, abierto = abrir_pdf(ruta_completa, password_pdf)

    if not abierto or not pdf:
        return []

    consumos = []
    with pdf:
        texto_completo = extraer_texto_pdf(pdf)

        # Guardar texto extraído para depuración
        texto_debug_path = os.path.join(carpeta_tmp, f"texto_extraido_{nombre_archivo}.txt")
        with open(texto_debug_path, 'w', encoding='utf-8') as debug_file:
            debug_file.write(texto_completo)
        logger.debug(f"Texto extraído guardado en: {texto_debug_path}")

        nombre_tarjeta = detectar_tipo_tarjeta(texto_completo)
        numero_tarjeta, banco = extraer_datos_tarjeta(texto_completo)
        logger.info(f"Tipo de tarjeta: {nombre_tarjeta} | Número: {numero_tarjeta or 'No detectado'} | Banco: {banco or 'No detectado'}")

        consumos = procesar_texto_resumen(texto_completo, nombre_tarjeta, numero_tarjeta, banco)

        # Agregar nombre de archivo a cada consumo
        for c in consumos:
            c['archivo'] = nombre_archivo

        logger.info(f"✓ {len(consumos)} consumos encontrados y agregados.\n")

    return consumos


# =============================================================================
# DEDUPLICACIÓN Y VALIDACIÓN
# =============================================================================

def parse_fecha(fecha):
    """Parsea una fecha en varios formatos posibles."""
    for fmt in ("%d.%m.%y", "%d-%m-%y", "%d-%b-%y", "%d.%b.%y"):
        try:
            return datetime.strptime(fecha, fmt)
        except Exception:
            continue
    return None


def normalizar_descripcion(desc):
    """Normaliza una descripción para comparación."""
    return re.sub(r'[^a-z0-9]', '', desc.lower())


def extraer_comercio(desc):
    """Extrae la parte 'comercio' de la descripción sin el número de operación."""
    return re.sub(r'\s+\d{5,}$', '', desc).strip()


def eliminar_duplicados_exactos(consumos_totales):
    """Elimina duplicados exactos basándose en todos los campos."""
    unique_consumos = []
    seen = set()

    for row in consumos_totales:
        key = (
            row['fecha'],
            row['descripcion'],
            row['monto'],
            row['moneda'],
            row['tarjeta'],
            row['numero_tarjeta'],
            row['banco'],
            row['archivo'],
            row['categoria']
        )
        if key not in seen:
            seen.add(key)
            unique_consumos.append(row)

    return unique_consumos


def marcar_duplicados_mismo_archivo(unique_consumos):
    """
    Marca duplicados dentro del mismo archivo.
    No marca como duplicados si tienen diferente número de operación.
    """
    archivo_fecha_monto = defaultdict(list)

    for row in unique_consumos:
        archivo_fecha_monto[(row['archivo'], row['fecha'], row['monto'], row['moneda'])].append(row)

    for rows in archivo_fecha_monto.values():
        if len(rows) > 1:
            comercios = [extraer_comercio(r['descripcion']) for r in rows]

            # Solo marcar como duplicados si TODAS las descripciones son idénticas
            if len(set(comercios)) == 1 and len(set(r['descripcion'] for r in rows)) == 1:
                for r in rows:
                    r['duplicado'] = 'ERROR_DUPLICADO_ARCHIVO'
                    logger.warning(f"Duplicado exacto en mismo archivo: {r['fecha']} - {r['descripcion'][:50]} - {r['moneda']} {r['monto']}")
            else:
                # Son consumos diferentes con el mismo monto (ej: varios viajes en metro)
                for r in rows:
                    r['duplicado'] = 'NO'
                    logger.info(f"Consumo válido (mismo monto, diferente operación): {r['fecha']} - {r['descripcion'][:50]} - {r['moneda']} {r['monto']}")


def marcar_duplicados_entre_archivos(unique_consumos):
    """
    Marca duplicados por similitud de descripción y monto entre archivos distintos.
    Fechas cercanas (±5 días).
    """
    for i, r1 in enumerate(unique_consumos):
        if r1.get('duplicado') == 'ERROR_DUPLICADO_ARCHIVO':
            continue
        r1['duplicado'] = 'NO'
        fecha1 = parse_fecha(r1['fecha'])
        desc1 = normalizar_descripcion(r1['descripcion'])

        for j, r2 in enumerate(unique_consumos):
            if i == j or r1['archivo'] == r2['archivo']:
                continue
            if r1['monto'] == r2['monto'] and r1['tarjeta'] == r2['tarjeta'] and r1['numero_tarjeta'] == r2['numero_tarjeta']:
                desc2 = normalizar_descripcion(r2['descripcion'])
                if 'primevideo' in desc1 and 'primevideo' in desc2:
                    fecha2 = parse_fecha(r2['fecha'])
                    if fecha1 and fecha2 and abs((fecha1 - fecha2).days) <= 5:
                        r1['duplicado'] = 'SI'
                        r2['duplicado'] = 'SI'
                        logger.info(f"Duplicado por similitud detectado: {r1['fecha']} - {r1['descripcion'][:50]} - ${r1['monto']}")


def procesar_duplicados(consumos_totales):
    """
    Procesa y marca duplicados en la lista de consumos.

    Returns:
        list: Lista de consumos únicos con campo 'duplicado' marcado
    """
    logger.info(f"Total de consumos extraidos antes de deduplicacion: {len(consumos_totales)}")

    unique_consumos = eliminar_duplicados_exactos(consumos_totales)
    logger.info(f"Consumos unicos despues de deduplicacion: {len(unique_consumos)}")

    marcar_duplicados_mismo_archivo(unique_consumos)
    marcar_duplicados_entre_archivos(unique_consumos)

    return unique_consumos


# =============================================================================
# EXPORTACIÓN Y REPORTES
# =============================================================================

def guardar_csv(consumos, cotizacion_dolar, archivo_salida='consumos_totales.csv'):
    """
    Guarda los consumos en un archivo CSV.
    Para consumos en USD, agrega el monto pesificado.
    Para consumos en ARS, deja vacía la columna monto_ars.
    Incluye metadata con la cotización del dólar utilizada.
    """
    fieldnames = ['fecha', 'descripcion', 'monto', 'moneda', 'monto_ars', 'tarjeta', 'numero_tarjeta', 'banco', 'categoria', 'duplicado']

    with open(archivo_salida, 'w', newline='', encoding='utf-8') as csvfile:
        # Escribir metadata como comentario al inicio
        fecha_proceso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        csvfile.write(f"# Archivo generado: {fecha_proceso}\n")
        csvfile.write(f"# Cotización dólar oficial (venta): ${cotizacion_dolar:.2f}\n" if cotizacion_dolar else "# Cotización dólar: No disponible\n")
        csvfile.write(f"# Total consumos: {len(consumos)}\n")
        csvfile.write("#\n")

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in consumos:
            # Calcular monto_ars solo para consumos en USD
            if row['moneda'] == 'USD' and cotizacion_dolar:
                monto_ars = pesificar_monto(row['monto'], cotizacion_dolar)
            else:
                # Para ARS u otras monedas, dejar vacío
                monto_ars = ''

            row_to_write = {k: row[k] for k in fieldnames if k != 'monto_ars'}
            row_to_write['monto_ars'] = monto_ars
            writer.writerow(row_to_write)

    return len(consumos)


def log_resumen_categorias(consumos):
    """Genera y loguea el resumen de consumos por categoría."""
    logger.info(f"\n--- Resumen por Categorías ---")

    categorias_count = {}
    categorias_monto = {}

    for row in consumos:
        cat = row.get('categoria', CATEGORIA_DEFAULT)
        categorias_count[cat] = categorias_count.get(cat, 0) + 1
        categorias_monto[cat] = categorias_monto.get(cat, 0) + row['monto']

    for cat in CATEGORIAS_ORDEN:
        count = categorias_count.get(cat, 0)
        monto = categorias_monto.get(cat, 0)
        logger.info(f"  {cat}: {count} consumos | Total: ${monto:,.2f}")


def log_resumen_final(cantidad_guardados, cotizacion_dolar=None):
    """Loguea el resumen final del procesamiento."""
    logger.info(f"\n✓ Proceso finalizado exitosamente")
    logger.info(f"✓ Consumos guardados en CSV: {cantidad_guardados}")
    if cotizacion_dolar:
        logger.info(f"✓ Cotización dólar oficial utilizada: ${cotizacion_dolar:.2f}")
    logger.info(f"✓ Archivo de salida: 'consumos_totales.csv'")
    logger.info(f"✓ Archivo de log: 'procesamiento_consumos.log'\n")


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal que orquesta el procesamiento de PDFs de tarjetas."""
    password_pdf = '30311931'

    # Validar que existe la carpeta de resúmenes
    if not os.path.exists(CARPETA_RESUMENES):
        logger.error(f"Error: La carpeta '{CARPETA_RESUMENES}' no existe.")
        return

    logger.info(f"\n{'#'*80}")
    logger.info(f"# INICIANDO PROCESAMIENTO DE TARJETAS")
    logger.info(f"{'#'*80}\n")

    # Preparar carpeta temporal para debug
    carpeta_tmp = os.path.join(CARPETA_RESUMENES, 'tmp_debug')
    os.makedirs(carpeta_tmp, exist_ok=True)

    # Buscar archivos PDF
    logger.info(f"Buscando archivos PDF en: {CARPETA_RESUMENES}")
    archivos_pdf = [f for f in os.listdir(CARPETA_RESUMENES) if f.lower().endswith('.pdf')]
    logger.info(f"Se encontraron {len(archivos_pdf)} archivos PDF\n")

    # Procesar cada PDF y acumular consumos
    consumos_totales = []
    for nombre_archivo in archivos_pdf:
        ruta_completa = os.path.join(CARPETA_RESUMENES, nombre_archivo)
        consumos = procesar_archivo_pdf(ruta_completa, nombre_archivo, password_pdf, carpeta_tmp)
        consumos_totales.extend(consumos)

    # Procesar y guardar resultados
    if consumos_totales:
        logger.info(f"\n{'#'*80}")
        logger.info(f"# PROCESANDO DUPLICADOS Y GUARDANDO RESULTADOS")
        logger.info(f"{'#'*80}\n")

        # Obtener cotización del dólar para pesificar
        cotizacion_dolar = obtener_cotizacion_dolar_oficial()

        # Deduplicar y marcar duplicados
        unique_consumos = procesar_duplicados(consumos_totales)

        # Filtrar duplicados erróneos y guardar
        consumos_a_guardar = [r for r in unique_consumos if r.get('duplicado') != 'ERROR_DUPLICADO_ARCHIVO']
        cantidad_guardados = guardar_csv(consumos_a_guardar, cotizacion_dolar)

        # Generar reportes
        log_resumen_categorias(consumos_a_guardar)
        log_resumen_final(cantidad_guardados, cotizacion_dolar)

        # Enviar reporte por email (si está habilitado)
        enviar_reporte_email(consumos_a_guardar, cotizacion_dolar)

        # Limpiar archivos temporales
        if os.path.exists(carpeta_tmp):
            shutil.rmtree(carpeta_tmp)
            logger.debug(f"Archivos temporales de depuración eliminados: {carpeta_tmp}")
    else:
        logger.error("\nNo se encontraron consumos para guardar en el CSV.")

if __name__ == "__main__":
    main()