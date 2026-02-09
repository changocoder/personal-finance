# Ejemplo de Output de Logging

Este archivo contiene un ejemplo de cómo se ve el output completo del logging cuando ejecutas `python main.py`.

## Ejemplo de Ejecución Completa

```
================================================================================
# INICIANDO PROCESAMIENTO DE TARJETAS
================================================================================

2025-12-09 10:45:23,123 - INFO - Buscando archivos PDF en: data_cards/
2025-12-09 10:45:23,124 - INFO - Se encontraron 4 archivos PDF

────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,150 - INFO - Procesando archivo: Visa-2025-11-20-0604905659.pdf
────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,200 - INFO - ✓ PDF abierto sin necesidad de contraseña.
2025-12-09 10:45:23,250 - INFO - Tipo de tarjeta: VISA | Número: 0604905659 | Banco: No detectado

================================================================================
Procesando VISA - Total de líneas encontradas: 45
================================================================================

2025-12-09 10:45:23,260 - INFO - Consumo [11.11.25] 000001* LACAJASEGURO 028063215 -0  | Monto: $84431.00
2025-12-09 10:45:23,261 - DEBUG - Monto convertido - Original: '84431,0' -> Limpio: '84431.0' -> Final: 84431.0
2025-12-09 10:45:23,262 - INFO - Consumo [01.07.25] 515535 APPLE.COM/BILL MSSVT3N75 USD 2 | Monto: $2.00
2025-12-09 10:45:23,263 - DEBUG - Monto convertido - Original: '2,00' -> Limpio: '2.00' -> Final: 2.0
2025-12-09 10:45:23,264 - INFO - Consumo [21.07.25] 082803 APPLE.COM/BILL USD 8         | Monto: $8.00
2025-12-09 10:45:23,265 - DEBUG - Monto convertido - Original: '8,00' -> Limpio: '8.00' -> Final: 8.0
2025-12-09 10:45:23,266 - INFO - Consumo [23.07.25] 582401* MERPAGO*NIKEARGENTINA Cuota | Monto: $8500.00
2025-12-09 10:45:23,267 - DEBUG - Monto convertido - Original: '8.500,00' -> Limpio: '8500.00' -> Final: 8500.0
2025-12-09 10:45:23,268 - DEBUG - Línea excluida [24.07.25] DB IVA $ 21% 35.537 (contiene palabra excluida)
2025-12-09 10:45:23,269 - DEBUG - Línea excluida [24.07.25] IVA RG 4240 21%( 3762 (contiene palabra excluida)
2025-12-09 10:45:23,270 - DEBUG - Línea excluida [24.07.25] IVA RG 4240 21%( 11112 (contiene palabra excluida)
2025-12-09 10:45:23,271 - INFO - Consumo [25.07.25] COMPRA ONLINE TIENDA ROPA        | Monto: $1500.00
2025-12-09 10:45:23,272 - DEBUG - Monto convertido - Original: '1.500,00' -> Limpio: '1500.00' -> Final: 1500.0

... (más consumos) ...

2025-12-09 10:45:23,300 - INFO - Consumos en USD encontrados: 5
2025-12-09 10:45:23,301 - INFO - Consumo USD [01.07.25] SUBSCRIPTION NETFLIX USD 15    | Monto: $15.00
2025-12-09 10:45:23,302 - INFO - Consumo USD [15.07.25] COMPRA AMAZON USD 45           | Monto: $45.00
2025-12-09 10:45:23,310 - INFO - Total de consumos extraídos para VISA: 42
================================================================================

────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,350 - INFO - Procesando archivo: Mastercard-2025-11-20-1347917536.pdf
────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,400 - INFO - ✓ PDF abierto sin necesidad de contraseña.
2025-12-09 10:45:23,450 - INFO - Tipo de tarjeta: Mastercard | Número: 1347917536 | Banco: No detectado

================================================================================
Procesando Mastercard - Total de líneas encontradas: 38
================================================================================

2025-12-09 10:45:23,460 - INFO - Consumo [10.11.25] CAFÉ RESTAURANT LA BOCA         | Monto: $850.00
2025-12-09 10:45:23,461 - INFO - Consumo [11.11.25] COMBUSTIBLE ESTACION YPF        | Monto: $2500.00
2025-12-09 10:45:23,462 - INFO - Consumo [12.11.25] SUPERMERCADO CARREFOUR          | Monto: $5200.50
2025-12-09 10:45:23,463 - DEBUG - Monto convertido - Original: '5.200,50' -> Limpio: '5200.50' -> Final: 5200.5

... (más consumos) ...

2025-12-09 10:45:23,500 - INFO - Total de consumos extraídos para Mastercard: 38
================================================================================

────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,550 - INFO - Procesando archivo: PTCFD65420251129063503519H1764500377659.PDF
────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,580 - WARNING - ✗ No se pudo abrir sin contraseña: Cannot open document
2025-12-09 10:45:23,620 - INFO - ✓ PDF abierto exitosamente con contraseña.
2025-12-09 10:45:23,670 - INFO - Tipo de tarjeta: Desconocida | Número: No detectado | Banco: No detectado
2025-12-09 10:45:23,671 - WARNING - Monto inválido o cero [05.11.25] LINEA CORRUPTA SIN MONTO -> None
2025-12-09 10:45:23,680 - INFO - Total de consumos extraídos para Desconocida: 25
================================================================================

────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,730 - INFO - Procesando archivo: 0956202589.24-07-25.pdf
────────────────────────────────────────────────────────────────────────────────
2025-12-09 10:45:23,800 - INFO - ✓ PDF abierto sin necesidad de contraseña.
2025-12-09 10:45:23,850 - INFO - Tipo de tarjeta: VISA | Número: 202589 | Banco: No detectado

================================================================================
Procesando VISA - Total de líneas encontradas: 52
================================================================================

... (consumos) ...

2025-12-09 10:45:23,950 - INFO - Total de consumos extraídos para VISA: 52
================================================================================

================================================================================
# PROCESANDO DUPLICADOS Y GUARDANDO RESULTADOS
================================================================================

2025-12-09 10:45:24,000 - INFO - Total de consumos extraídos antes de deduplicación: 157
2025-12-09 10:45:24,050 - INFO - Consumos únicos después de deduplicación: 155
2025-12-09 10:45:24,080 - WARNING - Duplicado detectado en mismo archivo: 11.07.25 - COMPRA ELECTRODOMESTICOS - $3500.00
2025-12-09 10:45:24,090 - INFO - Duplicado por similitud detectado: 15.07.25 - PRIMEVIDEO - $99.99
2025-12-09 10:45:24,100 - INFO - Duplicado por similitud detectado: 20.07.25 - PRIMEVIDEO - $99.99
2025-12-09 10:45:24,150 - INFO - 
2025-12-09 10:45:24,151 - INFO - ✓ Proceso finalizado exitosamente
2025-12-09 10:45:24,152 - INFO - ✓ Consumos guardados en CSV: 152
2025-12-09 10:45:24,153 - INFO - ✓ Archivo de salida: 'consumos_totales.csv'
2025-12-09 10:45:24,154 - INFO - ✓ Archivo de log: 'procesamiento_consumos.log'
```

## Explicación del Output

### Secciones Principales

1. **Encabezado**: Indica que inicia el procesamiento
2. **Para cada PDF**: 
   - Nombre del archivo
   - Método de apertura (con/sin contraseña)
   - Tipo y número de tarjeta detectado
   - Número total de líneas encontradas
   - Cada consumo extraído con su monto
   - Total de consumos de ese archivo
3. **Deduplicación**: Resumen de duplicados encontrados
4. **Resumen final**: Resultado final del proceso

## Información que Extraes de Aquí

### Para Verificar un Consumo Específico
Busca la fecha y descripción en el log para ver:
- ✅ Que fue extraído correctamente
- ✅ El monto final en formato correcto
- ✅ Si fue excluido o procesado

### Para Revisar Conversión de Montos
Los logs `DEBUG` muestran:
```
Original: '84431,0' -> Limpio: '84431.0' -> Final: 84431.0
```

Esto te permite verificar que los formatos se convirtieron correctamente.

### Para Identificar Problemas
- Si un consumo no aparece en el CSV pero sí en el log
- Si un monto está incorrectamente calculado
- Si hay duplicados que no debería haber

## Niveles de Severidad

- **INFO** (azul/blanco): Operaciones normales
- **WARNING** (amarillo): Algo sospechoso pero continúa
- **ERROR** (rojo): Errores que impiden continuar
- **DEBUG** (gris): Información técnica detallada

Este ejemplo debería ayudarte a entender qué esperar cuando ejecutes tu script.

