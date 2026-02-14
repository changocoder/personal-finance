# 🏷️ Sistema de Clasificación de Categorías

## Descripción

El sistema de clasificación automática asigna una categoría a cada consumo extraído de los resúmenes de tarjetas. La clasificación se realiza mediante coincidencia de palabras clave en la descripción del consumo.

## Categorías Disponibles

### 1. Utilities (Servicios)
Incluye servicios básicos, suscripciones digitales y seguros.

**Palabras clave:**
- **Streaming:** NETFLIX, SPOTIFY, YOUTUBE, PRIME, PRIMEVIDEO, DISNEY, HBO, AMAZON
- **Tecnología:** GOOGLE, APPLE.COM, APPLE COM, ICLOUD, ADOBE, MICROSOFT
- **Telecomunicaciones:** CLARO, MOVISTAR, PERSONAL, TELECOM, TELEFONICA
- **Servicios públicos:** EDENOR, EDESUR, METROGAS, AYSA, NATURGY
- **Seguros:** SERVICIO CUENTA, SEGURO, LACAJASEGURO, SEGUROS
- **Viajes/Reservas:** KIWI.COM, AIRBNB, BOOKING, DESPEGAR

### 2. Investment (Inversiones)
Consumos relacionados con inversiones y finanzas personales.

**Palabras clave:**
- **Tradicional:** INVERSION, PLAZO FIJO, FCI, FONDOS, MERCADOPAGO INVERSION
- **Criptomonedas:** CRYPTO, BITCOIN, LEMON, BUENBIT, BINANCE, RIPIO
- **Bolsa:** BROKER, BOLSA, CEDEAR, ACCIONES

### 3. Food (Alimentación)
Gastos en comida, restaurantes, supermercados y delivery.

**Palabras clave:**
- **Restaurantes:** RESTAURANT, RESTAURANTE, CAFE, CAFETERIA, PIZZA, BURGER, MCDONALD, STARBUCKS
- **Delivery:** RAPPI, PEDIDOSYA, GLOVO
- **Supermercados:** SUPERMERCADO, CARREFOUR, COTO, DIA, JUMBO, DISCO, VEA, WALMART, CHANGO, MAKRO, MAYORISTA
- **Comercios locales:** PANADERIA, VERDULERIA, CARNICERIA, ALMACEN
- **Farmacias:** FARMACITY, FARMACIA
- **Internacional:** SAL DA TERRA, GOURMET, ALIMENTOS, MAFALDA, IRMAOS GONCALVES, LOJAS AMERICANAS, BALNEARIO, PEDRINHO, REI DO MATE, TMKJB ALIMENTOS

### 4. Household (Hogar)
Gastos relacionados con el hogar, electrodomésticos y mantenimiento.

**Palabras clave:**
- **Construcción:** EASY, SODIMAC, HOMECENTER, FERRETERIA, PINTURERIA
- **Electrodomésticos:** GARBARINO, FRAVEGA, MUSIMUNDO, CETROGAR
- **Hogar:** MUEBLERIA, DECO, HOGAR, BLANQUERIA
- **Servicios:** LIMPIEZA, LAVADERO

### 5. Discretionary (Gastos Discrecionales)
Compras no esenciales, entretenimiento y transporte.

**Palabras clave:**
- **Indumentaria:** NIKE, ADIDAS, PUMA, REEBOK, ZARA, H&M, FALABELLA, RENNER, C&A, RAPSODIA, KOSIUKO, VITAMINA
- **E-commerce:** MERCADOLIBRE, MERPAGO, ML, MERCADO PAGO
- **Alquiler vehículos:** LOCALIZA, RAC, ALQUILER AUTO, RENT A CAR
- **Entretenimiento:** CINE, TEATRO, EVENTO, TICKET, ENTRADAS
- **Turismo:** VIAJE, TURISMO, HOTEL, HOSTEL
- **Transporte:** METRO, SUBTE, COLECTIVO, BUS, PASAJES, UBER, CABIFY, DIDI, BEAT

### 6. Other (Otros)
Consumos que no coinciden con ninguna de las categorías anteriores.

## Funcionamiento

```python
def clasificar_consumo(descripcion):
    """
    Clasifica un consumo en una categoría basándose en la descripción.
    
    Args:
        descripcion (str): Descripción del consumo
        
    Returns:
        str: Categoría del consumo
    """
    # La función busca coincidencias de palabras clave
    # en la descripción del consumo (case-insensitive)
```

## Orden de Prioridad

La clasificación se realiza en el siguiente orden:
1. Utilities
2. Investment
3. Food
4. Household
5. Discretionary
6. Other (por defecto)

Si una descripción coincide con palabras clave de múltiples categorías, se asignará la **primera categoría** que coincida según el orden de prioridad.

## Personalización

Para agregar nuevas palabras clave o modificar las existentes, edita el diccionario `CATEGORIAS_CONSUMOS` en `constants.py`:

```python
CATEGORIAS_CONSUMOS = {
    'Utilities': [
        'NETFLIX', 'SPOTIFY', ...
        'MI_NUEVO_SERVICIO'  # Agregar nuevas palabras aquí
    ],
    # ... otras categorías
}
```

## Ejemplo de Clasificación

| Descripción | Categoría Asignada |
|-------------|-------------------|
| `NETFLIX.COM 58139969884526236` | Utilities |
| `CARREFOUR SUC 123` | Food |
| `MERPAGO*NIKEARGENTINA` | Discretionary |
| `PLAZO FIJO 30 DIAS` | Investment |
| `GARBARINO ELECTRONICA` | Household |
| `PAGO CUOTA 123` | Other |

## Logs de Categorización

Al procesar los consumos, el sistema registra en el log:
- La categoría asignada a cada consumo
- Un resumen final con cantidad de consumos y montos por categoría

Ejemplo de salida en log:
```
Consumo [23.01.26] NETFLIX.COM 58139969884526236 | Monto: ARS   25398.00
  -> Categoría: Utilities

--- Resumen por Categorías ---
  Utilities: 15 consumos | Total: $150,234.00
  Investment: 2 consumos | Total: $50,000.00
  Food: 25 consumos | Total: $89,432.00
  Household: 3 consumos | Total: $45,000.00
  Discretionary: 18 consumos | Total: $234,567.00
  Other: 5 consumos | Total: $12,345.00
```

