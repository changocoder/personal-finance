# 🔍 Comandos Útiles para Trabajar con Logs

Una colección de comandos `grep` y `bash` que puedes usar para analizar rápidamente tus logs.

## 📊 Comandos Básicos

### Ver todo el log (primero espera que termine main.py)
```bash
cat procesamiento_consumos.log
```

### Ver últimas 50 líneas del log
```bash
tail -50 procesamiento_consumos.log
```

### Ver las primeras 50 líneas
```bash
head -50 procesamiento_consumos.log
```

---

## 🔎 Buscar Consumos

### Ver todos los consumos extraídos
```bash
grep "Consumo \[" procesamiento_consumos.log
```

### Ver consumos de una fecha específica
```bash
grep "Consumo \[11.11.25\]" procesamiento_consumos.log
```

### Ver consumos de un mes específico
```bash
grep "Consumo \[01.07" procesamiento_consumos.log
```

### Buscar un comercio específico (ej: APPLE)
```bash
grep -i "apple" procesamiento_consumos.log
```

### Buscar consumos que contengan cierta palabra
```bash
grep -i "netflix" procesamiento_consumos.log
```

### Ver consumos en un rango de montos (ejemplo: 1000 a 5000)
```bash
grep "Consumo \[" procesamiento_consumos.log | awk '$NF ~ /[0-9]{4}\./ {print}'
```

---

## 💱 Montos y Conversiones

### Ver cómo se convirtieron los montos (DEBUG)
```bash
grep "Monto convertido" procesamiento_consumos.log
```

### Ver conversión de un monto específico (ej: 84431)
```bash
grep "84431" procesamiento_consumos.log
```

### Ver todos los montos inválidos
```bash
grep "Monto inválido" procesamiento_consumos.log
```

### Ver montos que fallaron al convertir
```bash
grep -i "error.*monto" procesamiento_consumos.log
```

---

## ⚠️ Advertencias y Errores

### Ver todas las advertencias
```bash
grep "WARNING" procesamiento_consumos.log
```

### Ver todos los errores
```bash
grep "ERROR" procesamiento_consumos.log
```

### Ver advertencias y errores juntos
```bash
grep -E "(WARNING|ERROR)" procesamiento_consumos.log
```

### Ver montos problemáticos
```bash
grep -E "(inválido|ERROR|WARNING)" procesamiento_consumos.log
```

---

## 📁 Líneas Excluidas

### Ver todas las líneas excluidas
```bash
grep "excluida" procesamiento_consumos.log
```

### Ver líneas excluidas por IVA
```bash
grep -i "excluida.*iva" procesamiento_consumos.log
```

### Contar cuántas líneas fueron excluidas
```bash
grep "excluida" procesamiento_consumos.log | wc -l
```

### Ver qué palabras causaron más exclusiones
```bash
grep "excluida" procesamiento_consumos.log | grep -o "(.*)" | sort | uniq -c | sort -rn
```

---

## 🔄 Duplicados

### Ver todos los duplicados detectados
```bash
grep "Duplicado" procesamiento_consumos.log
```

### Ver solo duplicados en mismo archivo
```bash
grep "Duplicado detectado en mismo archivo" procesamiento_consumos.log
```

### Ver solo duplicados por similitud
```bash
grep "Duplicado por similitud" procesamiento_consumos.log
```

### Contar duplicados
```bash
grep "Duplicado" procesamiento_consumos.log | wc -l
```

---

## 💳 Por Tarjeta

### Ver consumos de VISA
```bash
grep "Consumo \[" procesamiento_consumos.log | grep -i "visa"
```

### Ver consumos de Mastercard
```bash
grep "Consumo \[" procesamiento_consumos.log | grep -i "master"
```

### Ver consumos en USD
```bash
grep "Consumo USD" procesamiento_consumos.log
```

### Ver consumos en ARS
```bash
grep "Consumo \[" procesamiento_consumos.log | grep -v "USD"
```

---

## 📈 Estadísticas

### Contar total de consumos extraídos
```bash
grep "Consumo \[" procesamiento_consumos.log | wc -l
```

### Contar consumos por archivo
```bash
grep "Procesando archivo:" procesamiento_consumos.log
```

### Ver resumen de consumos por tarjeta
```bash
grep "Total de consumos extraídos para" procesamiento_consumos.log
```

### Ver líneas encontradas por archivo
```bash
grep "Total de líneas encontradas:" procesamiento_consumos.log
```

### Contar total de líneas antes de deduplicación
```bash
grep "Total de consumos extraídos antes de deduplicación:" procesamiento_consumos.log
```

### Ver consumos finales guardados
```bash
grep "Consumos guardados en CSV:" procesamiento_consumos.log
```

---

## 🕐 Por Fecha

### Ver consumos de una fecha exacta
```bash
grep "Consumo \[11.11.25\]" procesamiento_consumos.log
```

### Ver consumos desde una fecha en adelante (ej: desde 15.11)
```bash
grep "Consumo \[" procesamiento_consumos.log | awk '{print $0}' | sort
```

### Ver consumos más recientes
```bash
grep "Consumo \[" procesamiento_consumos.log | tail -10
```

### Ver consumos más antiguos
```bash
grep "Consumo \[" procesamiento_consumos.log | head -10
```

---

## 🎯 Búsquedas Avanzadas

### Ver todo lo relacionado con APPLE (consumos + conversiones + errores)
```bash
grep -i "apple" procesamiento_consumos.log
```

### Ver línea completa de un consumo por fecha y descripción
```bash
grep "11.11.25.*LACAJASEGURO" procesamiento_consumos.log
```

### Ver consumos entre dos fechas (ej: 01.07 a 30.07)
```bash
grep "Consumo \[\(0[1-2]\|[12]\d\|30\)\.07" procesamiento_consumos.log
```

### Ver consumos mayores a $5000
```bash
grep "Consumo \[" procesamiento_consumos.log | awk '$NF > 5000 {print}'
```

### Buscar consumos que coincidan en dos archivos
```bash
grep "11.11.25" procesamiento_consumos.log | sort | uniq -d
```

---

## 💾 Guardar Resultados

### Guardar todos los consumos en un archivo
```bash
grep "Consumo \[" procesamiento_consumos.log > mis_consumos.txt
```

### Guardar consumos de una tarjeta
```bash
grep "Consumo \[" procesamiento_consumos.log | grep -i "visa" > visa_consumos.txt
```

### Guardar conversiones de montos
```bash
grep "Monto convertido" procesamiento_consumos.log > conversiones.txt
```

### Guardar advertencias y errores
```bash
grep -E "(WARNING|ERROR)" procesamiento_consumos.log > problemas.txt
```

---

## 📋 Casos de Uso Específicos

### Auditar un consumo sospechoso
```bash
# 1. Buscar el consumo
grep -i "descripcion_sospechosa" procesamiento_consumos.log

# 2. Ver su conversión de monto
grep "84431" procesamiento_consumos.log

# 3. Verificar si aparece en CSV
grep "84431" consumos_totales.csv
```

### Investigar por qué falta un consumo
```bash
# 1. Buscar en el log
grep -i "descripcion_esperada" procesamiento_consumos.log

# 2. Si dice "excluida", revisar PALABRAS_A_EXCLUIR
# 3. Si dice "inválido", revisar el monto en el PDF
# 4. Si no aparece, el regex no lo capturó
```

### Comparar consumos antes y después de deduplicación
```bash
echo "Antes:"
grep "Total de consumos extraídos antes" procesamiento_consumos.log

echo "Después:"
grep "Consumos guardados en CSV:" procesamiento_consumos.log
```

### Validar que todo procesó correctamente
```bash
# Ver si hay errores
grep "ERROR" procesamiento_consumos.log

# Ver si hay advertencias
grep "WARNING" procesamiento_consumos.log

# Ver total de consumos
grep "Consumos guardados en CSV:" procesamiento_consumos.log
```

---

## 🚀 Atajos Útiles

### Ver resumen rápido
```bash
echo "=== CONSUMOS TOTALES ===" && \
grep "Consumo \[" procesamiento_consumos.log | wc -l && \
echo "=== PROBLEMAS ===" && \
grep -c "WARNING\|ERROR" procesamiento_consumos.log && \
echo "=== RESULTADO FINAL ===" && \
grep "Consumos guardados" procesamiento_consumos.log
```

### Crear reporte completo
```bash
{
  echo "REPORTE DE PROCESAMIENTO"
  echo "======================="
  echo ""
  echo "Archivos procesados:"
  grep "Procesando archivo:" procesamiento_consumos.log
  echo ""
  echo "Consumos por tarjeta:"
  grep "Total de consumos extraídos para" procesamiento_consumos.log
  echo ""
  echo "Resultado final:"
  grep "Consumos guardados" procesamiento_consumos.log
} > reporte.txt
```

### Buscar todos los problemas
```bash
{
  echo "=== ADVERTENCIAS ==="
  grep "WARNING" procesamiento_consumos.log
  echo ""
  echo "=== ERRORES ==="
  grep "ERROR" procesamiento_consumos.log
  echo ""
  echo "=== LÍNEAS EXCLUIDAS ==="
  grep "excluida" procesamiento_consumos.log | head -5
} > problemas.txt
```

---

## 💡 Tips Importantes

1. **Usa `grep -i` para búsquedas sin sensibilidad de mayúsculas**
   ```bash
   grep -i "apple" procesamiento_consumos.log  # Encuentra APPLE, Apple, apple
   ```

2. **Usa `|` para combinar comandos**
   ```bash
   grep "Consumo" procesamiento_consumos.log | wc -l  # Cuenta consumos
   ```

3. **Usa `>` para guardar en archivo**
   ```bash
   grep "ERROR" procesamiento_consumos.log > errores.txt
   ```

4. **Usa `-E` para búsquedas con múltiples opciones**
   ```bash
   grep -E "(WARNING|ERROR|inválido)" procesamiento_consumos.log
   ```

5. **Guarda el log antes de ejecutar de nuevo**
   ```bash
   mv procesamiento_consumos.log procesamiento_consumos_old.log
   python main.py
   ```

---

**Nota**: Después de ejecutar `python main.py`, el archivo `procesamiento_consumos.log` se sobrescribe. Si quieres guardar un log anterior, renómbralo primero.

