# constants.py
# Archivo de constantes y configuración del proyecto Personal Finance App

# --- CONFIGURACIÓN DE CARPETAS Y ARCHIVOS ---
CARPETA_RESUMENES = 'data_cards/'
ARCHIVO_SALIDA = 'consumos_totales.txt'
NOMBRE_VARIABLE_ENTORNO = 'PDF_PASSWORD'

# --- PALABRAS CLAVE PARA EXCLUIR (NO SON CONSUMOS) ---
PALABRAS_A_EXCLUIR = [
    'SALDO ANTERIOR', 'SU PAGO', 'IMPUESTO', 'IVA', 'DB.RG',
    'SALDO ACTUAL', 'PAGO MINIMO', 'Total Consumos',
    'DEV.IMP.'
]

# --- CATEGORÍAS DE CONSUMOS ---
# Taxonomía para clasificación automática de gastos
CATEGORIAS_CONSUMOS = {
    'Utilities': [
        # Streaming y entretenimiento digital
        'NETFLIX', 'SPOTIFY', 'YOUTUBE', 'PRIME', 'PRIMEVIDEO', 'DISNEY', 'HBO', 'AMAZON',
        # Servicios tecnológicos
        'GOOGLE', 'APPLE.COM', 'APPLE COM', 'ICLOUD', 'ADOBE', 'MICROSOFT',
        # Telecomunicaciones
        'CLARO', 'MOVISTAR', 'PERSONAL', 'TELECOM', 'TELEFONICA',
        # Servicios públicos
        'EDENOR', 'EDESUR', 'METROGAS', 'AYSA', 'NATURGY',
        # Servicios financieros y seguros
        'SERVICIO CUENTA', 'SEGURO', 'LACAJASEGURO', 'SEGUROS',
        # Viajes y reservas
        'KIWI.COM', 'AIRBNB', 'BOOKING', 'DESPEGAR'
    ],

    'Investment': [
        # Inversiones tradicionales
        'INVERSION', 'PLAZO FIJO', 'FCI', 'FONDOS', 'MERCADOPAGO INVERSION',
        # Criptomonedas
        'CRYPTO', 'BITCOIN', 'LEMON', 'BUENBIT', 'BINANCE', 'RIPIO',
        # Mercado de valores
        'BROKER', 'BOLSA', 'CEDEAR', 'ACCIONES'
    ],

    'Food': [
        # Restaurantes y cafeterías
        'RESTAURANT', 'RESTAURANTE', 'CAFE', 'CAFETERIA', 'PIZZA', 'BURGER',
        'MCDONALD', 'STARBUCKS',
        # Delivery
        'RAPPI', 'PEDIDOSYA', 'GLOVO',
        # Supermercados
        'SUPERMERCADO', 'CARREFOUR', 'COTO', 'DIA', 'JUMBO', 'DISCO', 'VEA',
        'WALMART', 'CHANGO', 'MAKRO', 'MAYORISTA',
        # Comercios de alimentos
        'PANADERIA', 'VERDULERIA', 'CARNICERIA', 'ALMACEN',
        # Farmacias (productos de consumo)
        'FARMACITY', 'FARMACIA',
        # Comercios internacionales (Brasil)
        'SAL DA TERRA', 'GOURMET', 'ALIMENTOS', 'MAFALDA',
        'IRMAOS GONCALVES', 'LOJAS AMERICANAS', 'BALNEARIO', 'PEDRINHO',
        'REI DO MATE', 'TMKJB ALIMENTOS'
    ],

    'Household': [
        # Construcción y mejoras del hogar
        'EASY', 'SODIMAC', 'HOMECENTER', 'FERRETERIA', 'PINTURERIA',
        # Electrodomésticos
        'GARBARINO', 'FRAVEGA', 'MUSIMUNDO', 'CETROGAR',
        # Mobiliario y decoración
        'MUEBLERIA', 'DECO', 'HOGAR', 'BLANQUERIA',
        # Servicios del hogar
        'LIMPIEZA', 'LAVADERO'
    ],

    'Discretionary': [
        # Indumentaria y calzado
        'NIKE', 'ADIDAS', 'PUMA', 'REEBOK', 'ZARA', 'H&M', 'FALABELLA',
        'RENNER', 'C&A', 'RAPSODIA', 'KOSIUKO', 'VITAMINA',
        # E-commerce
        'MERCADOLIBRE', 'MERPAGO', 'ML', 'MERCADO PAGO',
        # Alquiler de vehículos
        'LOCALIZA', 'RAC', 'ALQUILER AUTO', 'RENT A CAR',
        # Entretenimiento
        'CINE', 'TEATRO', 'EVENTO', 'TICKET', 'ENTRADAS',
        # Turismo
        'VIAJE', 'TURISMO', 'HOTEL', 'HOSTEL',
        # Transporte
        'METRO', 'SUBTE', 'COLECTIVO', 'BUS', 'PASAJES',
        'UBER', 'CABIFY', 'DIDI', 'BEAT'
    ]
}

# Categoría por defecto para consumos no clasificados
CATEGORIA_DEFAULT = 'Other'

# Lista ordenada de categorías para reportes
CATEGORIAS_ORDEN = ['Utilities', 'Investment', 'Food', 'Household', 'Discretionary', 'Other']

