# Personal Finance App

Una aplicación para extraer y procesar consumos de tarjetas de crédito desde archivos PDF de resúmenes bancarios.

## 📋 Descripción

Esta aplicación automatiza la extracción de consumos de tarjetas de crédito a partir de archivos PDF de resúmenes. Soporta múltiples tipos de tarjetas (VISA, Mastercard) y detecta automáticamente información como:

- Fecha del consumo
- Descripción del comercio
- Monto en ARS o USD
- Tipo de tarjeta
- Número de tarjeta
- Banco emisor

Además, identifica y marca duplicados automáticamente.

## 🚀 Características

- ✅ Extracción de texto desde PDFs (con o sin contraseña)
- ✅ Detección automática del tipo de tarjeta y banco
- ✅ Procesamiento de montos en ARS y USD
- ✅ Eliminación de duplicados
- ✅ Exportación a CSV
- ✅ Manejo robusto de errores

## 📁 Estructura del Proyecto

```
personal-finance-app/
├── main.py                    # Script principal de procesamiento
├── extract_text.py            # Módulo de extracción de texto desde PDFs
├── requirements.txt           # Dependencias del proyecto
├── consumos_totales.csv       # Archivo de salida con consumos procesados
├── data_cards/                # Carpeta con archivos PDF de resúmenes (ignorada en git)
│   └── .gitkeep
├── .gitignore                 # Configuración de git
└── README.md                  # Este archivo
```

## 📦 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Coloca tus archivos PDF en la carpeta `data_cards/`

## 🎯 Uso

Ejecuta el script principal:

```bash
python main.py
```

El script:
1. Buscará todos los archivos PDF en la carpeta `data_cards/`
2. Extraerá el texto de cada PDF
3. Parseará los consumos detectados
4. Guardará los resultados en `consumos_totales.csv`
5. Generará un archivo de log `procesamiento_consumos.log` con todos los detalles

### Verificar Resultados

Después de ejecutar, puedes ver:

- **Consumos extraídos**: en `consumos_totales.csv`
- **Detalles del procesamiento**: en `procesamiento_consumos.log`
- **Montos convertidos**: en `procesamiento_consumos.log` (ver GUIA_LOGGING.md)

### Contraseña de PDFs

Si tus PDFs están protegidos con contraseña, edita la variable `password_pdf` en `main.py`:

```python
password_pdf = 'tu_contraseña_aqui'
```

### 📊 Logging y Depuración

El script genera un archivo de log automáticamente (`procesamiento_consumos.log`) que contiene:

- ✅ Cada consumo extraído con fecha, descripción y monto
- ✅ Conversión de montos paso a paso (para verificar)
- ✅ Avisos sobre consumos excluidos o inválidos
- ✅ Detalles sobre duplicados detectados
- ✅ Resumen del procesamiento

Para aprender cómo usar los logs, consulta `GUIA_LOGGING.md`

Ejemplo rápido:
```bash
# Ver consumos extraídos
grep "Consumo \[" procesamiento_consumos.log

# Buscar un consumo específico
grep "APPLE" procesamiento_consumos.log

# Ver montos inválidos
grep "inválido" procesamiento_consumos.log
```

## 📊 Formato de Salida

El archivo `consumos_totales.csv` contiene las siguientes columnas:

| Campo | Descripción |
|-------|-------------|
| fecha | Fecha del consumo (dd.mm.yy) |
| descripcion | Descripción del comercio |
| monto | Monto del consumo |
| moneda | Moneda (ARS o USD) |
| tarjeta | Tipo de tarjeta (VISA, Mastercard, etc.) |
| numero_tarjeta | Número de tarjeta (últimos dígitos) |
| banco | Código del banco emisor |
| duplicado | Indica si es un duplicado (SI/NO/ERROR_DUPLICADO_ARCHIVO) |

## ⚙️ Configuración

En `main.py` puedes personalizar:

- **CARPETA_RESUMENES**: Carpeta donde buscar PDFs (default: `data_cards/`)
- **ARCHIVO_SALIDA**: Nombre del archivo de salida (default: `consumos_totales.txt`)
- **PALABRAS_A_EXCLUIR**: Palabras clave para filtrar líneas que no son consumos

```python
PALABRAS_A_EXCLUIR = [
    'SALDO ANTERIOR', 'SU PAGO', 'IMPUESTO', 'IVA', 'DB.RG',
    'SALDO ACTUAL', 'PAGO MINIMO', 'Total Consumos',
    'DEV.IMP.'
]
```

## 🐛 Detección de Duplicados

El script detecta duplicados de dos formas:

1. **Duplicados exactos**: Mismo consumo en el mismo archivo
2. **Duplicados por similitud**: Mismo monto, tarjeta y descripción similar en archivos diferentes (dentro de ±5 días)

## 📝 Notas Importantes

- Los archivos PDF en `data_cards/` son ignorados por git (.gitignore)
- Se recomienda mantener una copia de seguridad de tus archivos PDF
- El script genera archivos temporales en `data_cards/tmp_debug/` que se eliminan automáticamente al finalizar
- Los montos se procesan como valores positivos (se ignora el signo en el PDF)

## 🔐 Privacidad y Seguridad

- Los datos de tus tarjetas se procesan localmente
- No se envía información a servidores externos
- Se recomienda no compartir el archivo `consumos_totales.csv` ni los PDFs

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Realiza un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Contacto y Soporte

Si encuentras problemas o tienes sugerencias, por favor abre un issue en el repositorio.

---

**Última actualización**: Diciembre 2025
