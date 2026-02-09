import os
import re
import logging
import pdfplumber

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

# --- CONFIGURACIÓN ---
# 1. Carpeta donde se encuentran tus resúmenes en PDF.
CARPETA_RESUMENES = 'data_cards/'

# 2. Nombre del archivo de texto donde se guardarán los resultados.
ARCHIVO_SALIDA = 'consumos_totales.txt'

# 3. Nombre de la variable de entorno que contiene la contraseña de los PDFs.
NOMBRE_VARIABLE_ENTORNO = 'PDF_PASSWORD'

# 4. Palabras clave para identificar y excluir filas que NO son consumos.
PALABRAS_A_EXCLUIR = [
    'SALDO ANTERIOR', 'SU PAGO', 'IMPUESTO', 'IVA', 'DB.RG',
    'SALDO ACTUAL', 'PAGO MINIMO', 'Total Consumos',
    'DEV.IMP.'
]


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
    else:
        match_banco2 = re.search(r'BANCO[:\s-]*([\w\s]+)', texto, re.IGNORECASE)
        if match_banco2:
            banco = match_banco2.group(1).strip()
    return numero, banco


def procesar_texto_resumen(texto_completo, nombre_tarjeta, numero_tarjeta, banco):
    """
    Extrae consumos de texto de resumen de tarjeta y los devuelve como lista de dicts para CSV.
    """
    consumos = []
    # Patrón original más flexible para capturar todos los consumos
    patron_linea = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
    patron_linea_alt = re.compile(r"^(\d{2}[./-]\d{2}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
    matches = patron_linea.findall(texto_completo) + patron_linea_alt.findall(texto_completo)

    logger.info(f"\n{'='*80}")
    logger.info(f"Procesando {nombre_tarjeta} - Total de líneas encontradas: {len(matches)}")
    logger.info(f"{'='*80}")

    consumos_extraidos = 0
    for match in matches:
        fecha, descripcion, monto = match
        descripcion_limpia = descripcion.strip()
        # Quitar tokens residuales típicos de extracción que aparecen antes del monto,
        # p.ej. líneas como "... 028063215 -0 84.431,00" dejan un "-0" al final de la descripción.
        # Solo eliminamos cuando es un token aislado al final (o seguido solo de comas/espacios).
        descripcion_limpia = re.sub(r"[\s,]*-0[\s,]*$", "", descripcion_limpia)
        # Normalizar espacios múltiples
        descripcion_limpia = re.sub(r"\s+", " ", descripcion_limpia).strip()

        # Verificar si es una palabra excluida
        if any(palabra in descripcion_limpia.upper() for palabra in PALABRAS_A_EXCLUIR):
            logger.debug(f"Línea excluida [{fecha}] {descripcion_limpia[:60]} (contiene palabra excluida)")
            continue

        monto_float = limpiar_monto(monto, fecha, descripcion_limpia)
        if monto_float is not None and abs(monto_float) > 0:
            consumos_extraidos += 1
            consumos.append({
                'fecha': fecha,
                'descripcion': descripcion_limpia,
                'monto': abs(monto_float),
                'moneda': 'ARS',
                'tarjeta': nombre_tarjeta,
                'numero_tarjeta': numero_tarjeta or '',
                'banco': banco or ''
            })
        else:
            logger.warning(f"Monto inválido o cero [{fecha}] {descripcion_limpia[:60]} -> {monto_float}")

    # Casos especiales: consumos en dólares
    patron_dolares = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?)\s+USD\s*([\d.]+,[\d]{2})", re.MULTILINE)
    matches_dolares = patron_dolares.findall(texto_completo)

    logger.info(f"Consumos en USD encontrados: {len(matches_dolares)}")

    for match in matches_dolares:
        fecha, descripcion, monto = match
        descripcion_limpia = descripcion.strip()

        if any(palabra in descripcion_limpia.upper() for palabra in PALABRAS_A_EXCLUIR):
            logger.debug(f"Línea USD excluida [{fecha}] {descripcion_limpia[:60]} (contiene palabra excluida)")
            continue

        monto_float = limpiar_monto(monto, fecha, descripcion_limpia)
        if monto_float is not None and abs(monto_float) > 0:
            consumos_extraidos += 1
            desc_display = descripcion_limpia[:50] if isinstance(descripcion_limpia, str) and descripcion_limpia else str(descripcion_limpia)
            formatted_monto = f"${monto_float:>10.2f}"
            logger.info("Consumo USD [%s] %s | Monto: %s", fecha, desc_display, formatted_monto)
            consumos.append({
                'fecha': fecha,
                'descripcion': descripcion_limpia,
                'monto': abs(monto_float),
                'moneda': 'USD',
                'tarjeta': nombre_tarjeta,
                'numero_tarjeta': numero_tarjeta or '',
                'banco': banco or ''
            })
        else:
            logger.warning(f"Monto USD inválido o cero [{fecha}] {descripcion_limpia[:60]} -> {monto_float}")

    logger.info(f"Total de consumos extraídos para {nombre_tarjeta}: {consumos_extraidos}")
    logger.info(f"{'='*80}\n")

    return consumos


def main():
    password_pdf = '30311931'
    if not os.path.exists(CARPETA_RESUMENES):
        logger.error(f"Error: La carpeta '{CARPETA_RESUMENES}' no existe.")
        return

    logger.info(f"\n{'#'*80}")
    logger.info(f"# INICIANDO PROCESAMIENTO DE TARJETAS")
    logger.info(f"{'#'*80}\n")

    carpeta_tmp = os.path.join(CARPETA_RESUMENES, 'tmp_debug')
    os.makedirs(carpeta_tmp, exist_ok=True)
    consumos_totales = []

    logger.info(f"Buscando archivos PDF en: {CARPETA_RESUMENES}")
    archivos_pdf = [f for f in os.listdir(CARPETA_RESUMENES) if f.lower().endswith('.pdf')]
    logger.info(f"Se encontraron {len(archivos_pdf)} archivos PDF\n")

    for nombre_archivo in archivos_pdf:
        ruta_completa = os.path.join(CARPETA_RESUMENES, nombre_archivo)
        logger.info(f"\n{'─'*80}")
        logger.info(f"Procesando archivo: {nombre_archivo}")
        logger.info(f"{'─'*80}")

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

        if abierto and pdf:
            with pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"

                # Guardar texto extraído para depuración en carpeta temporal
                texto_debug_path = os.path.join(carpeta_tmp, f"texto_extraido_{nombre_archivo}.txt")
                with open(texto_debug_path, 'w', encoding='utf-8') as debug_file:
                    debug_file.write(texto_completo)
                logger.debug(f"Texto extraído guardado en: {texto_debug_path}")

                nombre_tarjeta = "Desconocida"
                if "VISA" in texto_completo[:500]:
                    nombre_tarjeta = "VISA"
                elif "MASTERCARD" in texto_completo[:500]:
                    nombre_tarjeta = "Mastercard"

                numero_tarjeta, banco = extraer_datos_tarjeta(texto_completo)
                logger.info(f"Tipo de tarjeta: {nombre_tarjeta} | Número: {numero_tarjeta or 'No detectado'} | Banco: {banco or 'No detectado'}")

                consumos = procesar_texto_resumen(texto_completo, nombre_tarjeta, numero_tarjeta, banco)

                # Agregar nombre de archivo a cada consumo
                for c in consumos:
                    c['archivo'] = nombre_archivo

                consumos_totales.extend(consumos)
                logger.info(f"✓ {len(consumos)} consumos encontrados y agregados.\n")
    # Guardar en CSV
    if consumos_totales:
        import csv
        from collections import defaultdict
        from datetime import datetime

        logger.info(f"\n{'#'*80}")
        logger.info(f"# PROCESANDO DUPLICADOS Y GUARDANDO RESULTADOS")
        logger.info(f"{'#'*80}\n")

        logger.info(f"Total de consumos extraídos antes de deduplicación: {len(consumos_totales)}")

        def parse_fecha(fecha):
            for fmt in ("%d.%m.%y", "%d-%m-%y", "%d-%b-%y", "%d.%b.%y"):
                try:
                    return datetime.strptime(fecha, fmt)
                except Exception:
                    continue
            return None
        def normalizar_descripcion(desc):
            return re.sub(r'[^a-z0-9]', '', desc.lower())
        # Eliminar duplicados exactos
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
                row['archivo']
            )
            if key not in seen:
                seen.add(key)
                unique_consumos.append(row)

        logger.info(f"Consumos únicos después de deduplicación: {len(unique_consumos)}")

        # Marcar duplicados por archivo (mismo archivo, misma fecha y monto)
        archivo_fecha_monto = defaultdict(list)
        for row in unique_consumos:
            archivo_fecha_monto[(row['archivo'], row['fecha'], row['monto'])].append(row)
        for rows in archivo_fecha_monto.values():
            if len(rows) > 1:
                for r in rows:
                    r['duplicado'] = 'ERROR_DUPLICADO_ARCHIVO'
                    logger.warning(f"Duplicado detectado en mismo archivo: {r['fecha']} - {r['descripcion'][:50]} - ${r['monto']}")

        # Marcar duplicados por similitud de descripción y monto, fechas cercanas (±5 días) entre archivos distintos
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

        # Guardar en CSV (sin los que tengan ERROR_DUPLICADO_ARCHIVO)
        consumos_a_guardar = [r for r in unique_consumos if r.get('duplicado') != 'ERROR_DUPLICADO_ARCHIVO']
        fieldnames = ['fecha', 'descripcion', 'monto', 'moneda', 'tarjeta', 'numero_tarjeta', 'banco', 'duplicado']
        with open('consumos_totales.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in consumos_a_guardar:
                writer.writerow({k: row[k] for k in fieldnames})

        logger.info(f"\n✓ Proceso finalizado exitosamente")
        logger.info(f"✓ Consumos guardados en CSV: {len(consumos_a_guardar)}")
        logger.info(f"✓ Archivo de salida: 'consumos_totales.csv'")
        logger.info(f"✓ Archivo de log: 'procesamiento_consumos.log'\n")

        import shutil
        if os.path.exists(carpeta_tmp):
            shutil.rmtree(carpeta_tmp)
            logger.debug(f"Archivos temporales de depuración eliminados: {carpeta_tmp}")
    else:
        logger.error("\nNo se encontraron consumos para guardar en el CSV.")

if __name__ == "__main__":
    main()