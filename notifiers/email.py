# notifiers/email.py
"""
Notificador de Email - Soporta Resend (recomendado) y SMTP tradicional.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

logger = logging.getLogger(__name__)

# Intentar importar resend (opcional)
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailNotifier:
    """
    Notificador por email.
    Soporta Resend API (recomendado) y SMTP tradicional.
    """

    def __init__(self):
        logger.debug("Inicializando EmailNotifier...")
        self.provider = os.getenv('EMAIL_PROVIDER', 'smtp').lower()
        self.recipient = os.getenv('EMAIL_RECIPIENT')
        self.subject = os.getenv('EMAIL_SUBJECT', 'Reporte de Consumos - Personal Finance App')
        self.sender = os.getenv('EMAIL_SENDER')

        # Configuración específica por proveedor
        if self.provider == 'resend':
            self.api_key = os.getenv('RESEND_API_KEY')
            if not self.sender:
                self.sender = 'onboarding@resend.dev'
            logger.debug(f"Configurado para Resend - Sender: {self.sender}")
        else:
            self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
            self.password = os.getenv('EMAIL_PASSWORD')
            logger.debug(f"Configurado para SMTP - Server: {self.smtp_server}:{self.smtp_port}")

    def is_configured(self) -> bool:
        """Verifica si el notificador está correctamente configurado."""
        logger.debug("Validando configuración de email...")

        if not self.recipient:
            logger.error("❌ Falta EMAIL_RECIPIENT")
            return False

        if self.provider == 'resend':
            if not self.api_key:
                logger.error("❌ Falta RESEND_API_KEY para usar Resend")
                return False
            if not RESEND_AVAILABLE:
                logger.error("❌ Librería 'resend' no instalada. Ejecuta: pip install resend")
                return False
            logger.debug("✓ Configuración Resend válida")
        else:
            if not self.sender or not self.password:
                logger.error("❌ Configuración SMTP incompleta. Faltan: EMAIL_SENDER o EMAIL_PASSWORD")
                return False
            logger.debug("✓ Configuración SMTP válida")

        logger.debug(f"✓ Configuración completa - Provider: {self.provider}, Recipient: {self.recipient}")
        return True

    def send(self, consumos: list, cotizacion: float) -> bool:
        """
        Envía el reporte de consumos por email.

        Args:
            consumos: Lista de consumos procesados
            cotizacion: Cotización del dólar utilizada

        Returns:
            bool: True si se envió correctamente
        """
        logger.info(f"📧 Iniciando envío de email...")
        logger.debug(f"   Consumos a reportar: {len(consumos)}")
        logger.debug(f"   Cotización dólar: ${cotizacion:.2f}" if cotizacion else "   Cotización dólar: N/A")

        if not self.is_configured():
            return False

        logger.info(f"📧 Preparando email para {self.recipient} via {self.provider.upper()}...")

        try:
            logger.debug("Generando cuerpo HTML del email...")
            html_body = self._generate_html_body(consumos, cotizacion)
            logger.debug(f"✓ HTML generado ({len(html_body)} caracteres)")

            if self.provider == 'resend':
                return self._send_with_resend(html_body)
            else:
                return self._send_with_smtp(html_body)

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Error de autenticación SMTP. Verifica EMAIL_SENDER y EMAIL_PASSWORD")
            return False
        except Exception as e:
            logger.error(f"❌ Error al enviar email: {e}")
            logger.debug(f"   Detalle del error: {type(e).__name__}: {e}")
            return False

    def _send_with_resend(self, html_body: str) -> bool:
        """Envía email usando Resend API."""
        logger.debug("Configurando API de Resend...")
        resend.api_key = self.api_key

        # Preparar adjunto
        attachments = []
        csv_path = 'consumos_totales.csv'
        if os.path.exists(csv_path):
            logger.debug(f"Preparando adjunto: {csv_path}")
            with open(csv_path, 'rb') as f:
                filename = f"consumos_{datetime.now().strftime('%Y%m%d')}.csv"
                file_content = f.read()
                attachments.append({
                    "filename": filename,
                    "content": list(file_content)
                })
                logger.info(f"📎 Archivo adjunto: {filename} ({len(file_content)} bytes)")
        else:
            logger.warning(f"⚠️ Archivo CSV no encontrado: {csv_path}")

        logger.info("📤 Enviando via Resend API...")
        logger.debug(f"   From: {self.sender}")
        logger.debug(f"   To: {self.recipient}")
        logger.debug(f"   Subject: {self.subject}")

        params = {
            "from": self.sender,
            "to": [self.recipient],
            "subject": f"{self.subject} - {datetime.now().strftime('%d/%m/%Y')}",
            "html": html_body
        }

        if attachments:
            params["attachments"] = attachments

        response = resend.Emails.send(params)
        logger.info(f"✅ Email enviado exitosamente via Resend")
        logger.info(f"   ID: {response['id']}")
        return True

    def _send_with_smtp(self, html_body: str) -> bool:
        """Envía email usando SMTP tradicional."""
        logger.debug("Preparando mensaje MIME...")
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.recipient
        msg['Subject'] = f"{self.subject} - {datetime.now().strftime('%d/%m/%Y')}"

        msg.attach(MIMEText(html_body, 'html'))
        logger.debug("✓ Cuerpo HTML adjuntado")

        # Adjuntar CSV
        csv_path = 'consumos_totales.csv'
        if os.path.exists(csv_path):
            logger.debug(f"Preparando adjunto: {csv_path}")
            with open(csv_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                file_content = attachment.read()
                part.set_payload(file_content)
                encoders.encode_base64(part)
                filename = f"consumos_{datetime.now().strftime('%Y%m%d')}.csv"
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(part)
                logger.info(f"📎 Archivo adjunto: {filename} ({len(file_content)} bytes)")
        else:
            logger.warning(f"⚠️ Archivo CSV no encontrado: {csv_path}")

        logger.info(f"📤 Conectando a {self.smtp_server}:{self.smtp_port}...")
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            logger.debug("Iniciando TLS...")
            server.starttls()
            logger.debug(f"Autenticando como {self.sender}...")
            server.login(self.sender, self.password)
            logger.debug("Enviando mensaje...")
            server.send_message(msg)

        logger.info("✅ Email enviado exitosamente via SMTP")
        logger.debug(f"   From: {self.sender}")
        logger.debug(f"   To: {self.recipient}")
        return True

    def _generate_html_body(self, consumos: list, cotizacion: float) -> str:
        """Genera el cuerpo HTML del email."""
        logger.debug("Calculando totales para el reporte...")

        # Calcular totales
        total_ars = sum(c['monto'] for c in consumos if c['moneda'] == 'ARS')
        total_usd = sum(c['monto'] for c in consumos if c['moneda'] == 'USD')

        logger.debug(f"   Total ARS: ${total_ars:,.2f}")
        logger.debug(f"   Total USD: ${total_usd:,.2f}")

        # Totales por categoría
        categorias = {}
        for c in consumos:
            cat = c.get('categoria', 'Other')
            if cat not in categorias:
                categorias[cat] = {'count': 0, 'monto': 0}
            categorias[cat]['count'] += 1
            categorias[cat]['monto'] += c['monto']

        logger.debug(f"   Categorías encontradas: {', '.join(categorias.keys())}")

        fecha_reporte = datetime.now().strftime('%d/%m/%Y %H:%M')
        cotizacion_str = f"${cotizacion:.2f}" if cotizacion else 'N/A'
        total_pesificado = total_ars + (total_usd * (cotizacion or 0))

        logger.debug(f"   Total pesificado: ${total_pesificado:,.2f}")

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
                <strong>Cotización dólar oficial:</strong> {cotizacion_str}
            </div>
            
            <h2>📊 Resumen por Moneda</h2>
            <table>
                <tr><th>Moneda</th><th class="monto">Total</th></tr>
                <tr><td>ARS (Pesos Argentinos)</td><td class="monto">${total_ars:,.2f}</td></tr>
                <tr><td>USD (Dólares)</td><td class="monto">${total_usd:,.2f}</td></tr>
                <tr class="total"><td>Total pesificado (USD → ARS)</td><td class="monto">${total_pesificado:,.2f}</td></tr>
            </table>
            
            <h2>🏷️ Resumen por Categoría</h2>
            <table>
                <tr><th>Categoría</th><th>Cantidad</th><th class="monto">Monto Total</th></tr>
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
            <p><em>Este es un email automático generado por Personal Finance App.</em></p>
        </body>
        </html>
        """

        return html

