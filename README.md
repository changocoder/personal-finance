# 💳 Personal Finance App

Aplicación para extraer y procesar consumos de tarjetas de crédito desde resúmenes en PDF.

## 📋 Descripción

Esta herramienta permite:
- Extraer automáticamente consumos de resúmenes de tarjetas VISA y Mastercard en formato PDF
- Discriminar consumos en diferentes monedas (ARS, USD, BRL)
- **Pesificar automáticamente los consumos en USD** usando la cotización del dólar oficial
- **Clasificar automáticamente los consumos en categorías** (Utilities, Investment, Food, Household, Discretionary, Other)
- Detectar y marcar posibles duplicados
- Exportar los resultados a un archivo CSV para análisis
- **Enviar reportes automáticos por email** (configurable)
- Registrar logs detallados con totales por moneda, categoría y trazabilidad de conversiones

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd personal-finance-app
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura del proyecto

```
personal-finance-app/
├── main.py                    # Script principal
├── constants.py               # Constantes y configuración (categorías, palabras clave)
├── email_sender.py            # Módulo de envío de emails
├── requirements.txt           # Dependencias del proyecto
├── .env.example               # Plantilla de variables de entorno
├── data_cards/               # Carpeta para los PDFs (ignorada por git)
│   └── .gitkeep
├── consumos_totales.csv      # Archivo de salida con los consumos
├── procesamiento_consumos.log # Log detallado del procesamiento
└── README.md
```

## 📖 Uso

### 1. Colocar los PDFs

Coloca tus resúmenes de tarjetas en formato PDF en la carpeta `data_cards/`.

### 2. Ejecutar el procesamiento

```bash
python main.py
```

### 3. Revisar los resultados

- **consumos_totales.csv**: Archivo con todos los consumos extraídos (incluye columna de moneda)
- **procesamiento_consumos.log**: Log detallado del proceso (incluye resumen ARS/USD/BRL)

## 📊 Formato del archivo CSV de salida

El archivo CSV incluye metadata al inicio con la fecha de generación y cotización del dólar utilizada.

| Campo | Descripción |
|-------|-------------|
| `fecha` | Fecha del consumo |
| `descripcion` | Descripción del comercio/servicio |
| `monto` | Monto del consumo (en la moneda original) |
| `moneda` | Moneda (ARS, USD, BRL) |
| `monto_ars` | Monto pesificado (solo para USD, vacío para ARS) |
| `tarjeta` | Tipo de tarjeta (VISA, Mastercard) |
| `numero_tarjeta` | Número de cuenta/tarjeta |
| `banco` | Banco emisor |
| `categoria` | Categoría del consumo (ver sección Categorías) |
| `duplicado` | Indica si el consumo es un posible duplicado |

## 🏷️ Categorías de Consumos

Los consumos se clasifican automáticamente en las siguientes categorías:

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **Utilities** | Servicios y suscripciones | Netflix, Spotify, YouTube, servicios de luz/gas, seguros, viajes |
| **Investment** | Inversiones y finanzas | Plazo fijo, FCI, criptomonedas, brokers |
| **Food** | Alimentación y supermercados | Restaurantes, cafeterías, supermercados, farmacias, delivery |
| **Household** | Hogar y electrodomésticos | Ferreterías, electrodomésticos, muebles, limpieza |
| **Discretionary** | Gastos discrecionales | Ropa, entretenimiento, transporte, compras online |
| **Other** | Sin categorizar | Consumos que no coinciden con ninguna categoría |

### Palabras clave por categoría

<details>
<summary>Ver detalle de palabras clave</summary>

**Utilities:**
- Streaming: NETFLIX, SPOTIFY, YOUTUBE, PRIME, DISNEY, HBO
- Tech: GOOGLE, APPLE, ADOBE, MICROSOFT, ICLOUD
- Servicios: CLARO, MOVISTAR, EDENOR, METROGAS, AYSA
- Seguros: SEGURO, LACAJASEGURO
- Viajes: KIWI.COM, AIRBNB, BOOKING, DESPEGAR

**Investment:**
- INVERSION, PLAZO FIJO, FCI, FONDOS
- Crypto: LEMON, BUENBIT, BINANCE, RIPIO
- Bolsa: BROKER, CEDEAR, ACCIONES

**Food:**
- Restaurantes: RESTAURANT, CAFE, PIZZA, BURGER, STARBUCKS
- Delivery: RAPPI, PEDIDOSYA, GLOVO
- Supermercados: CARREFOUR, COTO, JUMBO, DISCO, WALMART
- Otros: FARMACIA, PANADERIA, VERDULERIA

**Household:**
- EASY, SODIMAC, FERRETERIA
- Electro: GARBARINO, FRAVEGA, MUSIMUNDO
- MUEBLERIA, BLANQUERIA, LIMPIEZA

**Discretionary:**
- Ropa: NIKE, ADIDAS, ZARA, FALABELLA, RENNER
- Compras: MERCADOLIBRE, MERPAGO
- Transporte: UBER, CABIFY, METRO, SUBTE
- Entretenimiento: CINE, TEATRO, EVENTO

</details>

## 🔐 PDFs protegidos con contraseña

Si tus PDFs están protegidos con contraseña, puedes configurarla de dos formas:

1. **Variable de entorno** (recomendado):
```bash
export PDF_PASSWORD="tu_contraseña"
```

2. **Directamente en el código** (no recomendado para producción):
Modifica la variable `password_pdf` en la función `main()`.

## 🪙 Monedas soportadas

La aplicación detecta automáticamente las siguientes monedas:
- **ARS**: Pesos argentinos (por defecto)
- **USD**: Dólares estadounidenses
- **BRL**: Reales brasileños

## 📧 Envío de Reportes por Email

La aplicación puede enviar automáticamente el reporte por email. Para configurarlo:

### 1. Crear archivo de configuración
```bash
cp .env.example .env
```

### 2. Configurar variables de entorno
```env
# Habilitar envío (1 = habilitado, 0 = deshabilitado)
EMAIL_ENABLED=1

# Configuración SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
EMAIL_RECIPIENT=destinatario@email.com
```

Para más detalles, consulta [EMAIL.md](EMAIL.md).

## 📝 Logs

El archivo `procesamiento_consumos.log` contiene información detallada:
- Archivos procesados
- Consumos extraídos con sus montos y monedas
- **Categoría asignada a cada consumo**
- Resumen de cantidades por moneda (ARS, USD, BRL)
- **Resumen de consumos por categoría con totales**
- Duplicados detectados
- Errores de procesamiento

## ⚙️ Configuración

En el archivo `constants.py` puedes modificar:

```python
# Carpeta donde se encuentran los PDFs
CARPETA_RESUMENES = 'data_cards/'

# Archivo de salida
ARCHIVO_SALIDA = 'consumos_totales.txt'

# Palabras para excluir (no son consumos reales)
PALABRAS_A_EXCLUIR = [
    'SALDO ANTERIOR', 'SU PAGO', 'IMPUESTO', 'IVA', 'DB.RG',
    'SALDO ACTUAL', 'PAGO MINIMO', 'Total Consumos', 'DEV.IMP.'
]

# Categorías de consumos (puedes agregar/modificar palabras clave)
CATEGORIAS_CONSUMOS = {
    'Utilities': ['NETFLIX', 'SPOTIFY', ...],
    'Investment': ['INVERSION', 'PLAZO FIJO', ...],
    'Food': ['RESTAURANT', 'SUPERMERCADO', ...],
    'Household': ['FERRETERIA', 'GARBARINO', ...],
    'Discretionary': ['NIKE', 'MERCADOLIBRE', ...]
}

# Categoría por defecto
CATEGORIA_DEFAULT = 'Other'

# Orden de categorías para reportes
CATEGORIAS_ORDEN = ['Utilities', 'Investment', 'Food', 'Household', 'Discretionary', 'Other']
```

## 🛡️ Privacidad

El archivo `.gitignore` está configurado para:
- **NO** subir los PDFs de tus resúmenes
- **NO** subir el archivo CSV con tus consumos
- **NO** subir los logs de procesamiento

Esto protege tu información financiera personal.

## 🐛 Solución de problemas

### Error al abrir PDF
- Verifica que el archivo no esté corrupto
- Si está protegido, asegúrate de configurar la contraseña correcta

### No se detectan consumos
- Revisa el log para ver el texto extraído
- Algunos formatos de PDF pueden no ser compatibles

### Montos incorrectos
- Los montos se procesan considerando el formato argentino (punto como separador de miles, coma como decimal)

## 📄 Licencia

MIT License

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores.
