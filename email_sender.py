# email_sender.py
# Módulo para envío de reportes por email

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

logger = logging.getLogger(__name__)


def cargar_configuracion_email():
    """
    Carga la configuración de email desde las variables de entorno.

    Returns:
        dict: Configuración de email o None si está deshabilitado
    """
    # Verificar si el envío de email está habilitado
    email_enabled = os.getenv('EMAIL_ENABLED', '0')
    if email_enabled != '1':
        logger.info("📧 Envío de email deshabilitado (EMAIL_ENABLED != 1)")
        return None

    # Cargar configuración
    config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'sender': os.getenv('EMAIL_SENDER'),
        'password': os.getenv('EMAIL_PASSWORD'),
        'recipient': os.getenv('EMAIL_RECIPIENT'),
        'subject': os.getenv('EMAIL_SUBJECT', 'Reporte de Consumos - Personal Finance App')
    }

    # Validar campos requeridos
    campos_requeridos = ['sender', 'password', 'recipient']
    campos_faltantes = [c for c in campos_requeridos if not config.get(c)]

    if campos_faltantes:
        logger.error(f"❌ Configuración de email incompleta. Faltan: {', '.join(campos_faltantes)}")
        return None

    return config


def generar_cuerpo_email(consumos, cotizacion_dolar):
    """
    Genera el cuerpo del email con un resumen de los consumos.

    Args:
        consumos (list): Lista de consumos procesados
        cotizacion_dolar (float): Cotización del dólar utilizada

    Returns:
        str: Cuerpo del email en formato HTML
    """
    # Calcular totales por moneda
    total_ars = sum(c['monto'] for c in consumos if c['moneda'] == 'ARS')
    total_usd = sum(c['monto'] for c in consumos if c['moneda'] == 'USD')

    # Calcular totales por categoría
    categorias = {}
    for c in consumos:
        cat = c.get('categoria', 'Other')
        if cat not in categorias:
            categorias[cat] = {'count': 0, 'monto': 0}
        categorias[cat]['count'] += 1
        categorias[cat]['monto'] += c['monto']

    # Generar HTML
    fecha_reporte = datetime.now().strftime('%d/%m/%Y %H:%M')

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .total {{ font-weight: bold; background-color: #ecf0f1; }}
            .monto {{ text-align: right; }}
            .info {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>💳 Reporte de Consumos</h1>
        
        <div class="info">
            <strong>Fecha del reporte:</strong> {fecha_reporte}<br>
            <strong>Total de consumos:</strong> {len(consumos)}<br>
            <strong>Cotización dólar oficial:</strong> ${cotizacion_dolar:.2f if cotizacion_dolar else 'N/A'}
        </div>
        
        <h2>📊 Resumen por Moneda</h2>
        <table>
            <tr>
                <th>Moneda</th>
                <th class="monto">Total</th>
            </tr>
            <tr>
                <td>ARS (Pesos Argentinos)</td>
                <td class="monto">${total_ars:,.2f}</td>
            </tr>
            <tr>
                <td>USD (Dólares)</td>
                <td class="monto">${total_usd:,.2f}</td>
            </tr>
            <tr class="total">
                <td>Total pesificado (USD → ARS)</td>
                <td class="monto">${total_ars + (total_usd * (cotizacion_dolar or 0)):,.2f}</td>
            </tr>
        </table>
        
        <h2>🏷️ Resumen por Categoría</h2>
        <table>
            <tr>
                <th>Categoría</th>
                <th>Cantidad</th>
                <th class="monto">Monto Total</th>
            </tr>
    """

    for cat in ['Utilities', 'Investment', 'Food', 'Household', 'Discretionary', 'Other']:
        if cat in categorias:
            html += f"""
            <tr>
                <td>{cat}</td>
                <td>{categorias[cat]['count']}</td>
                <td class="monto">${categorias[cat]['monto']:,.2f}</td>
            </tr>
            """

    html += """
        </table>
        
        <p><em>Este es un email automático generado por Personal Finance App. 
        El archivo CSV con el detalle completo está adjunto.</em></p>
    </body>
    </html>
    """

    return html


def enviar_reporte_email(consumos, cotizacion_dolar, archivo_csv='consumos_totales.csv'):
    """
    Envía el reporte de consumos por email.

    Args:
        consumos (list): Lista de consumos procesados
        cotizacion_dolar (float): Cotización del dólar utilizada
        archivo_csv (str): Ruta al archivo CSV para adjuntar

    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    # Cargar configuración
    config = cargar_configuracion_email()
    if not config:
        return False

    logger.info(f"📧 Preparando envío de email a {config['recipient']}...")

    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = config['sender']
        msg['To'] = config['recipient']
        msg['Subject'] = f"{config['subject']} - {datetime.now().strftime('%d/%m/%Y')}"

        # Agregar cuerpo del email
        cuerpo = generar_cuerpo_email(consumos, cotizacion_dolar)
        msg.attach(MIMEText(cuerpo, 'html'))

        # Adjuntar archivo CSV
        if os.path.exists(archivo_csv):
            with open(archivo_csv, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)

                filename = f"consumos_{datetime.now().strftime('%Y%m%d')}.csv"
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(part)
                logger.info(f"📎 Archivo adjunto: {filename}")
        else:
            logger.warning(f"⚠️ Archivo CSV no encontrado: {archivo_csv}")

        # Enviar email
        logger.info(f"📤 Conectando a {config['smtp_server']}:{config['smtp_port']}...")
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender'], config['password'])
            server.send_message(msg)

        logger.info(f"✅ Email enviado exitosamente a {config['recipient']}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("❌ Error de autenticación SMTP. Verifica EMAIL_SENDER y EMAIL_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ Error SMTP al enviar email: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado al enviar email: {e}")
        return False

