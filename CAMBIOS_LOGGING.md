# Resumen de Cambios - Sistema de Logging Agregado

## ✅ Cambios Realizados

Se ha implementado un sistema completo de **logging detallado** que te permite:

### 1. **Ver cada consumo extraído con detalles**
   - Fecha del consumo
   - Descripción completa
   - Monto parseado final
   - Moneda detectada automáticamente (ARS, USD o BRL)

**Ejemplo:**
```
INFO:Consumo [11.11.25] 000001* LACAJASEGURO 028063215 -0                | Monto: $84431.00
INFO:Consumo [01.07.25] 515535 APPLE.COM/BILL MSSVT3N75 USD 2            | Monto: $2.00
```

### 2. **Ver la conversión de montos paso a paso**
   - Monto original del PDF
   - Monto limpio después de procesar
   - Monto final convertido

**Ejemplo:**
```
DEBUG:Monto convertido - Original: '84431,0' -> Limpio: '84431.0' -> Final: 84431.0
DEBUG:Monto convertido - Original: '1.234,56' -> Limpio: '1234.56' -> Final: 1234.56
```

### 3. **Identificar consumos que fueron excluidos**
   - Muestra el motivo (palabra clave excluida)
   - Facilita ajustar PALABRAS_A_EXCLUIR si es necesario

**Ejemplo:**
```
DEBUG:Línea excluida [24.07.25] DB IVA $ 21% 35.537 (contiene palabra excluida)
```

### 4. **Ver advertencias y errores**
   - Montos inválidos que no pudieron procesarse
   - PDFs que no se pudieron abrir
   - Problemas con conversión de formatos

**Ejemplo:**
```
WARNING:Monto inválido o cero [15.05.25] DESCRIPCION RARA -> None
ERROR:Error al abrir con contraseña: ...
```

### 5. **Resumen por archivo PDF**
   - Cantidad de consumos extraídos por PDF
   - Tipo y número de tarjeta detectado
   - Total de consumos discriminados por moneda
   - Resumen agregado: `Total consumos: X | ARS: Y | USD: Z | BRL: W`

**Ejemplo:**
```
INFO:Procesando archivo: Visa-2025-11-20-0604905659.pdf
INFO:✓ PDF abierto sin necesidad de contraseña.
INFO:Tipo de tarjeta: VISA | Número: 0604905659 | Banco: No detectado
INFO:Consumos en USD encontrados: 3
INFO:Total de consumos extraídos para VISA: 45
INFO:Resumen por moneda: Total consumos: 45 | ARS: 10 | USD: 30 | BRL: 5
```

### 6. **Detección de duplicados**
   - Duplicados dentro del mismo archivo
   - Duplicados entre diferentes archivos por similitud
   - Detalles de cada duplicado encontrado

**Ejemplo:**
```
WARNING:Duplicado detectado en mismo archivo: 11.07.25 - DESCRIPCION - $2000.00
INFO:Duplicado por similitud detectado: 15.07.25 - PRIMEVIDEO - $99.99
```

### 7. **Clasificación automática por categorías**
   - Cada consumo se clasifica en: Utilities, Investment, Food, Household, Discretionary, Other
   - Se muestra la categoría asignada en el log
   - Resumen final con cantidad y montos por categoría

**Ejemplo:**
```
INFO:Consumo [11.11.25] LACAJASEGURO 028063215  | Monto: ARS  84431.00
INFO:  -> Categoría: Utilities
INFO:Consumo [23.07.25] MERPAGO*NIKEARGENTINA   | Monto: ARS   8500.00
INFO:  -> Categoría: Discretionary

INFO:--- Resumen por Categorías ---
INFO:  Utilities: 12 consumos | Total: $182,452.08
INFO:  Food: 7 consumos | Total: $158.12
INFO:  Discretionary: 8 consumos | Total: $237,092.35
```

### 8. **Resumen final del procesamiento**
   - Total de consumos extraídos
   - Consumos únicos después de deduplicación
   - Consumos guardados en CSV final
   - Cantidad final por moneda reflejada en el CSV (`moneda`)

**Ejemplo:**
```
INFO:Total de consumos extraídos antes de deduplicación: 120
INFO:Consumos únicos después de deduplicación: 118
INFO:✓ Consumos guardados en CSV: 115
INFO:✓ Archivo de salida: 'consumos_totales.csv'
INFO:✓ Archivo de log: 'procesamiento_consumos.log'
INFO:Resumen final: Total consumos: 115 | ARS: 50 | USD: 60 | BRL: 5
```

## 📁 Archivos Generados

### `procesamiento_consumos.log`
- Se crea automáticamente en la carpeta raíz
- Se sobrescribe cada vez que ejecutas `main.py`
- Contiene el registro completo con timestamp
- Se puede consultar incluso después de que termina la ejecución

### Salida simultánea
- **Consola**: Ves los logs en tiempo real
- **Archivo**: Se guardan permanentemente para consulta posterior

## 🔍 Cómo Usar los Logs

### Búsqueda rápida en terminal

```bash
# Ver todos los consumos extraídos
grep "Consumo \[" procesamiento_consumos.log

# Buscar un consumo específico por descripción
grep "APPLE" procesamiento_consumos.log

# Ver solo consumos en USD
grep "Consumo USD" procesamiento_consumos.log

# Ver montos que tuvieron problemas
grep -E "(inválido|ERROR)" procesamiento_consumos.log

# Ver cómo se convirtió un monto específico
grep "84431" procesamiento_consumos.log

# Ver qué líneas fueron excluidas
grep "excluida" procesamiento_consumos.log

# Ver duplicados
grep "Duplicado" procesamiento_consumos.log
```

## 📊 Niveles de Log Configurados

| Nivel | Descripción |
|-------|------------|
| **INFO** | Información de proceso general, consumos extraídos |
| **WARNING** | Montos inválidos, archivo no abierto, duplicados |
| **ERROR** | Errores serios, carpeta no existe |
| **DEBUG** | Información detallada (conversión de montos, etc.) |

## 💡 Caso de Uso: Tu Consumo Problemático

**Problema original:**
```
11.11.25,000001* LACAJASEGURO 028063215 -0,84431.0
```
Extracto incorrectamente como: `-0,84431` (negativo)

**Con los nuevos logs verías:**
```
DEBUG:Monto convertido - Original: '84431,0' -> Limpio: '84431.0' -> Final: 84431.0
INFO:Consumo [11.11.25] 000001* LACAJASEGURO 028063215 -0                | Monto: $84431.00
```

Esto **confirma** que se extrajo correctamente como `$84431.00` (positivo).

## 🚀 Para Empezar

1. Ejecuta tu script normalmente:
   ```bash
   python main.py
   ```

2. Verás los logs en la consola inmediatamente

3. Luego puedes abrir y revisar el log:
   ```bash
   cat procesamiento_consumos.log
   ```

4. O buscar algo específico:
   ```bash
   grep "APPLE" procesamiento_consumos.log
   ```

5. Para consulta posterior, antes de ejecutar de nuevo, puedes renombrar el log anterior:
   ```bash
   mv procesamiento_consumos.log procesamiento_consumos_backup_$(date +%Y%m%d_%H%M%S).log
   ```

## 📚 Documentación Completa

Para guía completa y ejemplos detallados, consulta: **`GUIA_LOGGING.md`**

---

**Ventajas principales:**

✅ **Transparencia total**: Ves exactamente qué se extrajo y cómo  
✅ **Fácil debugging**: Si falta un consumo, los logs te dicen por qué  
✅ **Verificación**: Puedes comparar el log con tus PDFs  
✅ **Historial**: Tienes registro permanente de cada ejecución  
✅ **Mejora continua**: Puedes ajustar PALABRAS_A_EXCLUIR basándote en los logs  
