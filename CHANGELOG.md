# 📝 Changelog - Historial de Cambios

## [2026-02-14] - Sesión de Desarrollo

### ✨ Nuevas Funcionalidades

#### 1. Sistema de Clasificación por Categorías
- Agregado sistema de clasificación automática de consumos
- Categorías disponibles: Utilities, Investment, Food, Household, Discretionary, Other
- Diccionario de palabras clave configurable en `constants.py`
- Log de categoría asignada a cada consumo
- Resumen por categorías al final del procesamiento

#### 2. Pesificación de Consumos en USD
- Conversión automática de consumos en USD a ARS
- Obtención de cotización del dólar oficial desde APIs públicas:
  - Fuente primaria: dolarapi.com
  - Fuente de respaldo: bluelytics.com.ar
- Se usa cotización de **venta** (más alta)
- Nueva columna `monto_ars` en el CSV
- Columna vacía para consumos que ya están en ARS

#### 3. Metadata en el CSV
- Fecha y hora de generación del archivo
- Cotización del dólar utilizada
- Total de consumos procesados

### 🐛 Correcciones

#### Detección de Moneda para Formato Galicia
- **Problema**: Consumo "RENNER 516 SH CA(BRA,ARS, 184599,57)" se detectaba como ARS cuando debía ser USD
- **Solución**: Mejorada función `detectar_moneda()` para reconocer que consumos internacionales (país != ARG) siempre se cobran en USD
- **Archivos modificados**: `main.py`

### 🔧 Refactorización

#### Organización del Código
- Extraídas constantes a archivo separado `constants.py`
- Refactorizada función `main()` aplicando SRP (Single Responsibility Principle)
- Nuevas funciones auxiliares:
  - `abrir_pdf()` - Apertura de PDFs con/sin contraseña
  - `extraer_texto_pdf()` - Extracción de texto
  - `detectar_tipo_tarjeta()` - Detección del tipo de tarjeta
  - `procesar_archivo_pdf()` - Procesamiento individual de PDF
  - `parse_fecha()` - Parsing de fechas
  - `normalizar_descripcion()` - Normalización de descripciones
  - `extraer_comercio()` - Extracción de nombre de comercio
  - `eliminar_duplicados_exactos()` - Deduplicación exacta
  - `marcar_duplicados_mismo_archivo()` - Marca duplicados en mismo archivo
  - `marcar_duplicados_entre_archivos()` - Marca duplicados entre archivos
  - `procesar_duplicados()` - Procesamiento completo de duplicados
  - `guardar_csv()` - Guardado del CSV con metadata
  - `log_resumen_categorias()` - Log de resumen por categorías
  - `log_resumen_final()` - Log del resumen final
- Imports movidos al inicio del archivo
- Secciones del código claramente delimitadas con comentarios

### 📚 Documentación

#### Archivos Creados
- `constants.py` - Constantes y configuración del proyecto
- `CATEGORIAS.md` - Documentación del sistema de categorías
- `PESIFICACION.md` - Documentación de la pesificación de consumos
- `CHANGELOG.md` - Este archivo de historial de cambios

#### Archivos Actualizados
- `README.md` - Agregada información sobre categorías y pesificación
- `INDICE.md` - Enlaces a nuevos archivos de documentación
- `GUIA_LOGGING.md` - Información sobre categorías en los logs
- `COMANDOS_LOGS.md` - Comandos para filtrar por categoría
- `EJEMPLO_OUTPUT_LOGGING.md` - Ejemplos actualizados con categorías
- `CAMBIOS_LOGGING.md` - Documentación de clasificación por categorías
- `IMPLEMENTACION_LOGGING.md` - Actualizado con información de categorías

### 📁 Estructura del Proyecto Actualizada

```
personal-finance-app/
├── main.py                    # Script principal (refactorizado)
├── constants.py               # Constantes y configuración (NUEVO)
├── requirements.txt           # Dependencias
├── data_cards/               # PDFs de tarjetas
├── consumos_totales.csv      # Salida con metadata y monto_ars
├── procesamiento_consumos.log # Logs del procesamiento
├── README.md                 # Documentación principal (actualizado)
├── INDICE.md                 # Índice de documentación (actualizado)
├── CATEGORIAS.md             # Doc. de categorías (NUEVO)
├── PESIFICACION.md           # Doc. de pesificación (NUEVO)
├── CHANGELOG.md              # Historial de cambios (NUEVO)
├── GUIA_LOGGING.md           # Guía de logging (actualizado)
├── COMANDOS_LOGS.md          # Comandos útiles (actualizado)
├── EJEMPLO_OUTPUT_LOGGING.md # Ejemplos de output (actualizado)
├── CAMBIOS_LOGGING.md        # Cambios de logging (actualizado)
├── IMPLEMENTACION_LOGGING.md # Implementación logging (actualizado)
└── SOLUCION_PARSING.md       # Solución de parsing
```

### 📊 Formato del CSV Actualizado

```csv
# Archivo generado: 2026-02-14 11:59:49
# Cotización dólar oficial (venta): $1420.00
# Total consumos: 28
#
fecha,descripcion,monto,moneda,monto_ars,tarjeta,numero_tarjeta,banco,categoria,duplicado
```

| Campo | Descripción |
|-------|-------------|
| fecha | Fecha del consumo |
| descripcion | Descripción del comercio |
| monto | Monto original |
| moneda | Moneda (ARS, USD) |
| monto_ars | Monto pesificado (solo USD) |
| tarjeta | Tipo de tarjeta |
| numero_tarjeta | Número de cuenta |
| banco | Banco emisor |
| categoria | Categoría asignada |
| duplicado | Estado de duplicado |

