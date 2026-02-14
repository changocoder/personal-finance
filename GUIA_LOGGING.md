# Guía de Logging del Proyecto

## 📊 Descripción General

Se ha agregado un sistema completo de logging al proyecto que te permite ver en detalle:

1. **Cada consumo extraído** con su fecha, descripción y monto convertido
2. **Moneda detectada automáticamente** (ARS, USD, BRL)
3. **Categoría asignada automáticamente** (Utilities, Investment, Food, Household, Discretionary, Other)
4. **Montos parseados** mostrando la conversión de formato argentino a decimal
5. **Advertencias y errores** que ocurran durante el procesamiento
6. **Resumen del procesamiento** de cada PDF
7. **Detección de duplicados** con detalles
8. **Resumen por categorías** con cantidad y montos totales

## 📁 Archivos de Log

### `procesamiento_consumos.log`
Se crea automáticamente en la carpeta raíz del proyecto cuando ejecutas `main.py`. Contiene el registro completo de:
- Fecha y hora de cada operación
- Nivel de cada mensaje (INFO, WARNING, ERROR, DEBUG)
- Detalles específicos de lo que se está procesando

### Ubicación
```
personal-finance-app/
├── main.py
├── procesamiento_consumos.log  ← SE GENERA AQUÍ
├── consumos_totales.csv
└── ...
```

## 📋 Niveles de Log

El logging está configurado con los siguientes niveles:

| Nivel | Descripción | Ejemplo |
|-------|------------|---------|
| **DEBUG** | Información detallada para debugging | Conversión de montos, rutas de archivos |
| **INFO** | Información general del proceso | Consumos extraídos, PDFs procesados |
| **WARNING** | Advertencias (algo sospechoso pero continúa) | Montos inválidos, archivos que no se abrieron |
| **ERROR** | Errores serios | PDF no se pudo abrir, no hay carpeta data_cards |

## 🎯 Qué Puedes Ver en los Logs

### 1. **Procesamiento General**
```
================================================================================
# INICIANDO PROCESAMIENTO DE TARJETAS
================================================================================

Se encontraron 4 archivos PDF

────────────────────────────────────────────────────────────────────────────────
Procesando archivo: Visa-2025-11-20-0604905659.pdf
────────────────────────────────────────────────────────────────────────────────
```

### 2. **Información de la Tarjeta**
```
✓ PDF abierto sin necesidad de contraseña.
Tipo de tarjeta: VISA | Número: 0604905659 | Banco: No detectado
```

### 3. **Cada Consumo Extraído** (más importante para ti)
```
Consumo [11.11.25] 000001* LACAJASEGURO 028063215 -0                | Monto: ARS  84431.00
  -> Categoría: Utilities
Consumo [01.07.25] 515535 APPLE.COM/BILL MSSVT3N75 USD 2            | Monto: USD      2.00
  -> Categoría: Utilities
Consumo [03.07.25] K CAFÉ BRASIL                                    | Monto: BRL     35.60
  -> Categoría: Food
```

### 4. **Conversión de Montos** (para verificar)
```
Monto convertido - Original: '84431,0' -> Limpio: '84431.0' -> Final: 84431.0
Monto convertido - Original: '1.234,56' -> Limpio: '1234.56' -> Final: 1234.56
```

### 5. **Consumos Excluidos**
```
Línea excluida [24.07.25] DB IVA $ 21% 35.537 (contiene palabra excluida)
```

### 6. **Montos Inválidos**
```
Monto inválido o cero [15.05.25] DESCRIPCION RARA -> None
```

### 7. **Resumen por Tarjeta**
```
Consumos en USD encontrados: 3
Consumo [01.07.25] 515535 APPLE.COM/BILL MSSVT3N75          | Monto: USD      2.00
Consumo [02.07.25] K CAFÉ BRASIL                            | Monto: BRL     55.00
--- Resumen de extracción para VISA ---
Total consumos: 45 | ARS: 30 | USD: 10 | BRL: 5
================================================================================
```

### 8. **Duplicados Detectados**
```
================================================================================
# PROCESANDO DUPLICADOS Y GUARDANDO RESULTADOS
================================================================================

Total de consumos extraídos antes de deduplicación: 120
Consumos únicos después de deduplicación: 118
Duplicado detectado en mismo archivo: 11.07.25 - DESCRIPCION - $2000.00
```

### 9. **Resumen Final**
```
✓ Proceso finalizado exitosamente
✓ Consumos guardados en CSV: 115
✓ Archivo de salida: 'consumos_totales.csv'
✓ Archivo de log: 'procesamiento_consumos.log'
Resumen final por moneda: ARS=90 | USD=20 | BRL=5
```

## 🔍 Cómo Usar los Logs para Verificación

### Caso 1: Verificar si un consumo específico fue extraído
```bash
# Busca en el log por la fecha y descripción
grep "11.11.25.*LACAJASEGURO" procesamiento_consumos.log
```

### Caso 2: Ver todos los consumos de una tarjeta específica
```bash
grep "Consumo \[" procesamiento_consumos.log | grep "VISA"
```

### Caso 3: Ver montos que tuvieron problemas
```bash
grep -E "(inválido|WARNING|ERROR)" procesamiento_consumos.log
```

### Caso 4: Ver cómo se convirtió un monto específico
```bash
grep "84431" procesamiento_consumos.log
```

### Caso 5: Ver qué líneas fueron excluidas
```bash
grep "excluida" procesamiento_consumos.log
```

## 📱 Ejemplo Práctico: Verificar tu Consumo Problemático

El consumo que mencionaste:
```
11.11.25,000001* LACAJASEGURO 028063215 -0,84431.0
```

En el log verías algo así:
```
Monto convertido - Original: '84431,0' -> Limpio: '84431.0' -> Final: 84431.0
Consumo [11.11.25] 000001* LACAJASEGURO 028063215 -0                | Monto: $84431.00
```

Lo que confirma que:
- ✅ Se extrajo correctamente el monto `84431.00` (positivo)
- ✅ La descripción se limpió correctamente
- ✅ Se guardó en el CSV con el valor correcto

## 💾 Salida en Consola Y Archivo

Los logs se escriben en **dos lugares simultáneamente**:
1. **En consola** (para ver en tiempo real mientras se ejecuta)
2. **En archivo** `procesamiento_consumos.log` (para consultar después)

Esto significa que cuando ejecutes:
```bash
python main.py
```

Verás los logs en tiempo real en la terminal Y además tendrás un archivo de referencia permanente.

## 🎓 Recomendaciones

1. **Después de la primera ejecución**, revisa el log completo:
   ```bash
   cat procesamiento_consumos.log
   ```

2. **Busca los consumos que esperas ver** para verificar que se extrajeron correctamente

3. **Si falta algún consumo**, busca en el log con la fecha/descripción para ver:
   - ¿Fue extraído pero excluido? (palabra en PALABRAS_A_EXCLUIR)
   - ¿No fue capturado por el regex?
   - ¿Fue marcado como inválido?

4. **Verifica montos problemáticos** viendo la conversión paso a paso

## 🚀 Ejecución Rápida

```bash
# Ejecutar con logs
python main.py

# Ver el log inmediatamente después
tail -100 procesamiento_consumos.log

# O buscar algo específico
grep "APPLE" procesamiento_consumos.log
```

---

**Nota**: El archivo de log se sobrescribe cada vez que ejecutas el script. Si quieres guardar un log anterior, renómbralo antes de ejecutar nuevamente.
