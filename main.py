import os
import re
import pdfplumber
import pandas as pd

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


def limpiar_monto(monto_str):
    """Limpia y convierte un string de monto a un número flotante."""
    if not isinstance(monto_str, str) or not monto_str.strip():
        return None

    signo = -1 if monto_str.endswith('-') else 1
    monto_limpio = monto_str.replace('.', '').replace(',', '.').replace('-', '').strip()

    try:
        return float(monto_limpio) * signo
    except ValueError:
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
    patron_linea = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
    patron_linea_alt = re.compile(r"^(\d{2}[./-]\d{2}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
    matches = patron_linea.findall(texto_completo) + patron_linea_alt.findall(texto_completo)
    for match in matches:
        fecha, descripcion, monto = match
        if any(palabra in descripcion.upper() for palabra in PALABRAS_A_EXCLUIR):
            continue
        monto_float = limpiar_monto(monto)
        if monto_float is not None and abs(monto_float) > 0:
            consumos.append({
                'fecha': fecha,
                'descripcion': descripcion.strip(),
                'monto': abs(monto_float),
                'moneda': 'ARS',
                'tarjeta': nombre_tarjeta,
                'numero_tarjeta': numero_tarjeta or '',
                'banco': banco or ''
            })
    # Casos especiales: consumos en dólares
    patron_dolares = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?)\s+USD\s*([\d.]+,[\d]{2})", re.MULTILINE)
    matches_dolares = patron_dolares.findall(texto_completo)
    for match in matches_dolares:
        fecha, descripcion, monto = match
        if any(palabra in descripcion.upper() for palabra in PALABRAS_A_EXCLUIR):
            continue
        monto_float = limpiar_monto(monto)
        if monto_float is not None and abs(monto_float) > 0:
            consumos.append({
                'fecha': fecha,
                'descripcion': descripcion.strip(),
                'monto': abs(monto_float),
                'moneda': 'USD',
                'tarjeta': nombre_tarjeta,
                'numero_tarjeta': numero_tarjeta or '',
                'banco': banco or ''
            })
    return consumos


def main():
    password_pdf = '30311931'
    if not os.path.exists(CARPETA_RESUMENES):
        print(f"Error: La carpeta '{CARPETA_RESUMENES}' no existe.")
        return
    carpeta_tmp = os.path.join(CARPETA_RESUMENES, 'tmp_debug')
    os.makedirs(carpeta_tmp, exist_ok=True)
    consumos_totales = []
    print(f"Buscando archivos PDF en: {CARPETA_RESUMENES}")
    for nombre_archivo in os.listdir(CARPETA_RESUMENES):
        if nombre_archivo.lower().endswith('.pdf'):
            ruta_completa = os.path.join(CARPETA_RESUMENES, nombre_archivo)
            print(f"\nProcesando archivo: {nombre_archivo}")
            pdf = None
            abierto = False
            try:
                pdf = pdfplumber.open(ruta_completa)
                print("  -> PDF abierto sin necesidad de contraseña.")
                abierto = True
            except Exception as e:
                print(f"  -> No se pudo abrir sin contraseña: {e}")
                try:
                    pdf = pdfplumber.open(ruta_completa, password=password_pdf)
                    print("  -> PDF abierto exitosamente con contraseña.")
                    abierto = True
                except Exception as e2:
                    print(f"  -> Error al abrir con contraseña: {e2}")
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
                    nombre_tarjeta = "Desconocida"
                    if "VISA" in texto_completo[:500]:
                        nombre_tarjeta = "VISA"
                    elif "MASTERCARD" in texto_completo[:500]:
                        nombre_tarjeta = "Mastercard"
                    numero_tarjeta, banco = extraer_datos_tarjeta(texto_completo)
                    consumos = procesar_texto_resumen(texto_completo, nombre_tarjeta, numero_tarjeta, banco)
                    # Agregar nombre de archivo a cada consumo
                    for c in consumos:
                        c['archivo'] = nombre_archivo
                    consumos_totales.extend(consumos)
                    print(f"  -> {len(consumos)} consumos encontrados y agregados.")
    # Guardar en CSV
    if consumos_totales:
        import csv
        from collections import defaultdict
        from datetime import datetime, timedelta
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
        # Marcar duplicados por archivo (mismo archivo, misma fecha y monto)
        archivo_fecha_monto = defaultdict(list)
        for row in unique_consumos:
            archivo_fecha_monto[(row['archivo'], row['fecha'], row['monto'])].append(row)
        for rows in archivo_fecha_monto.values():
            if len(rows) > 1:
                for r in rows:
                    r['duplicado'] = 'ERROR_DUPLICADO_ARCHIVO'
        # Marcar duplicados por similitud de descripción y monto, fechas cercanas (±5 días) entre archivos distintos
        def parse_fecha(fecha):
            for fmt in ("%d.%m.%y", "%d-%m-%y", "%d-%b-%y", "%d.%b.%y"):
                try:
                    return datetime.strptime(fecha, fmt)
                except Exception:
                    continue
            return None
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
        # Guardar en CSV (sin los que tengan ERROR_DUPLICADO_ARCHIVO)
        fieldnames = ['fecha', 'descripcion', 'monto', 'moneda', 'tarjeta', 'numero_tarjeta', 'banco', 'duplicado']
        with open('consumos_totales.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in unique_consumos:
                if row.get('duplicado') != 'ERROR_DUPLICADO_ARCHIVO':
                    writer.writerow({k: row[k] for k in fieldnames})
        print(f"\nProceso finalizado. Los consumos únicos se han guardado en 'consumos_totales.csv'. Total: {len([r for r in unique_consumos if r.get('duplicado') != 'ERROR_DUPLICADO_ARCHIVO'])}.")
        import shutil
        if os.path.exists(carpeta_tmp):
            shutil.rmtree(carpeta_tmp)
            print(f"Archivos temporales de depuración eliminados: {carpeta_tmp}")
    else:
        print("\nNo se encontraron consumos para guardar en el CSV.")

if __name__ == "__main__":
    main()