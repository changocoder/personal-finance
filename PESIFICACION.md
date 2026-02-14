# 💱 Pesificación de Consumos en USD

## Descripción

El sistema permite convertir automáticamente los consumos realizados en dólares (USD) a pesos argentinos (ARS) utilizando la cotización oficial del dólar.

## Funcionamiento

### Obtención de la Cotización

La cotización del dólar oficial se obtiene automáticamente desde APIs públicas:

1. **Fuente primaria**: `https://dolarapi.com/v1/dolares/oficial`
2. **Fuente de respaldo**: `https://api.bluelytics.com.ar/v2/latest`

Se utiliza el valor de **venta** (el más alto) porque representa el costo real al que se pesifican los consumos en dólares.

### Proceso de Pesificación

```python
def pesificar_monto(monto_usd, cotizacion):
    """
    Convierte un monto en USD a ARS usando la cotización proporcionada.
    """
    return round(monto_usd * cotizacion, 2)
```

### Columna `monto_ars`

La columna `monto_ars` en el CSV:
- **Para consumos en USD**: Muestra el monto convertido a pesos argentinos
- **Para consumos en ARS**: Se deja **vacía** (el monto ya está en pesos)

## Metadata en el CSV

El archivo `consumos_totales.csv` incluye metadata al inicio con información del procesamiento:

```csv
# Archivo generado: 2026-02-14 11:59:49
# Cotización dólar oficial (venta): $1420.00
# Total consumos: 28
#
fecha,descripcion,monto,moneda,monto_ars,...
```

Esta metadata permite:
- Saber cuándo se generó el archivo
- Conocer la cotización del dólar utilizada
- Verificar la cantidad total de consumos procesados

## Ejemplo de Salida

| fecha | descripcion | monto | moneda | monto_ars |
|-------|-------------|-------|--------|-----------|
| 30-12-25 | LOCALIZA RAC | 234.27 | USD | 332,663.40 |
| 01-01-26 | SAL DA TERRA | 25.43 | USD | 36,110.60 |
| 09-01-26 | SERVICIO CUENTA | 37851.24 | ARS | *(vacío)* |

## Configuración

### Cambiar la fuente de cotización

Para agregar nuevas fuentes de cotización, edita la función `obtener_cotizacion_dolar_oficial()` en `main.py`:

```python
urls = [
    'https://dolarapi.com/v1/dolares/oficial',
    'https://api.bluelytics.com.ar/v2/latest',
    # Agregar nuevas fuentes aquí
]
```

### Usar cotización de compra en lugar de venta

Si prefieres usar la cotización de compra (más baja), modifica:

```python
# En dolarapi.com format
if 'compra' in data:  # Cambiar 'venta' por 'compra'
    cotizacion = float(data['compra'])
```

## Logs Relacionados

El proceso de pesificación genera los siguientes logs:

```
INFO - Obteniendo cotización del dólar desde: https://dolarapi.com/v1/dolares/oficial
INFO - ✓ Cotización dólar oficial (venta): $1420.00
INFO - ✓ Cotización dólar oficial utilizada: $1420.00
```

## Manejo de Errores

Si no se puede obtener la cotización:
1. Se intenta con la fuente de respaldo
2. Si todas las fuentes fallan, se registra un error en el log
3. La columna `monto_ars` quedará vacía para los consumos en USD

