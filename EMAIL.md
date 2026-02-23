# 📧 Envío de Reportes por Email
## Descripción
La aplicación permite enviar automáticamente el reporte de consumos por email al finalizar el procesamiento. Esta funcionalidad puede habilitarse o deshabilitarse mediante un flag de configuración.
## Configuración
### 1. Crear archivo .env
```bash
cp .env.example .env
```
### 2. Configurar variables de entorno
```env
# Habilitar/Deshabilitar envío de email (1 = habilitado, 0 = deshabilitado)
EMAIL_ENABLED=1
# Configuración del servidor SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
# Credenciales de email
EMAIL_SENDER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
# Destinatario del reporte
EMAIL_RECIPIENT=destinatario@email.com
```
## Variables de Entorno
| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| EMAIL_ENABLED | Flag para habilitar/deshabilitar | Sí | 0 |
| SMTP_SERVER | Servidor SMTP | No | smtp.gmail.com |
| SMTP_PORT | Puerto SMTP | No | 587 |
| EMAIL_SENDER | Email del remitente | Sí* | - |
| EMAIL_PASSWORD | Contraseña o App Password | Sí* | - |
| EMAIL_RECIPIENT | Email del destinatario | Sí* | - |
*Requerido solo si EMAIL_ENABLED=1
## Gmail: Crear App Password
1. Ve a myaccount.google.com → Seguridad
2. Activa "Verificación en dos pasos"
3. Contraseñas de aplicación → Generar nueva
4. Usa esa contraseña en EMAIL_PASSWORD
## Contenido del Email
- **Cuerpo HTML**: Resumen por moneda y categoría
- **Adjunto**: consumos_YYYYMMDD.csv
## Logs
```
INFO - 📧 Envío de email deshabilitado (EMAIL_ENABLED != 1)
INFO - ✅ Email enviado exitosamente a destinatario@email.com
ERROR - ❌ Error de autenticación SMTP
```
## Seguridad
El archivo .env está en .gitignore y nunca se sube al repositorio.
