# 📧 Envío de Reportes por Email
## Descripción
La aplicación permite enviar automáticamente el reporte de consumos por email al finalizar el procesamiento. Soporta dos proveedores:
- **Resend** (recomendado) - API moderna y fácil de configurar
- **SMTP** - Método tradicional (Gmail, Outlook, etc.)
## Configuración Rápida con Resend (Recomendado)
### 1. Crear cuenta en Resend
1. Ve a [resend.com](https://resend.com) y crea una cuenta gratuita
2. Obtén tu API Key en [resend.com/api-keys](https://resend.com/api-keys)
### 2. Configurar variables de entorno
```bash
cp .env.example .env
```
Edita el archivo `.env`:
```env
EMAIL_ENABLED=1
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxxxx
EMAIL_RECIPIENT=tu_email@ejemplo.com
EMAIL_SENDER=onboarding@resend.dev
```
### 3. Ejecutar
```bash
python main.py
```
## Configuración con SMTP (Gmail, Outlook, etc.)
### Para Gmail
```env
EMAIL_ENABLED=1
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
EMAIL_RECIPIENT=destinatario@email.com
```
**Nota**: Para Gmail necesitas crear una "Contraseña de aplicación":
1. Activa verificación en dos pasos en tu cuenta Google
2. Ve a myaccount.google.com → Seguridad → Contraseñas de aplicación
3. Genera una nueva y úsala en EMAIL_PASSWORD
## Variables de Entorno
| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `EMAIL_ENABLED` | `1` habilitado, `0` deshabilitado | Sí |
| `EMAIL_PROVIDER` | `resend` o `smtp` | Sí |
| `EMAIL_RECIPIENT` | Email del destinatario | Sí |
| `RESEND_API_KEY` | API Key de Resend | Si provider=resend |
| `EMAIL_SENDER` | Email del remitente | Sí |
| `SMTP_SERVER` | Servidor SMTP | Si provider=smtp |
| `SMTP_PORT` | Puerto SMTP | Si provider=smtp |
| `EMAIL_PASSWORD` | Contraseña SMTP | Si provider=smtp |
## Contenido del Email
El email incluye:
- **Resumen por moneda**: Total ARS, USD y pesificado
- **Resumen por categoría**: Cantidad y montos
- **Archivo adjunto**: CSV con el detalle completo
## Planes Gratuitos de Proveedores
| Proveedor | Plan Gratuito |
|-----------|---------------|
| Resend | 3,000 emails/mes |
| SendGrid | 100 emails/día |
| Gmail SMTP | 500 emails/día |
## Seguridad
⚠️ El archivo `.env` está en `.gitignore` y **nunca** se sube al repositorio.
