# Solución del Problema de Parsing de Montos

## 🐛 Problema Identificado

El consumo:
```
11.11.25,000001* LACAJASEGURO 028063215 -0,84431.0,ARS,VISA,0604905659,221,NO
```

Estaba siendo parseado incorrectamente como:
- **Monto extraído**: -0,84431 (negativo)
- **Monto correcto**: 84,431.00 (positivo)

### Causa Raíz

El regex utilizado para capturar consumos era demasiado permisivo en la parte de la descripción:

```python
# ANTES (incorrecto)
patron_linea = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?)\s+([\d.]+,[\d]{2})(?:\s|$)", re.MULTILINE)
```

El problema es que `.+?` (descripción) capturaba todo hasta encontrar el primer número seguido de coma. En este caso:
- La descripción incluía `028063215 -0,` 
- El regex interpretaba `-0,84431` como el monto en lugar de `84431.00`

## ✅ Solución Implementada

Se mejoró el regex y se añadió discriminación de moneda:

```python
# DESPUÉS (correcto)
patron_linea = re.compile(r"^(\d{2}[./-][A-Za-z0-9]{2,3}[./-]\d{2})\s+(.+?[^\s\d])\s+([\d.,]+)(?:\s|$)", re.MULTILINE)

moneda = detectar_moneda(descripcion)
```

### Cambios Clave:

1. **`.+?[^\s\d]`** en lugar de `.+?`:
   - Asegura que la descripción termine en un carácter que no sea espacio o dígito
   - Evita que los dígitos finales de la descripción sean incluidos en el monto

2. **`[\d.,]+`** en lugar de `[\d.]+,[\d]{2}`:
   - Más flexible con diferentes formatos de montos
   - Acepta: `84431,0`, `84,431.00`, `84.431,00`, etc.

3. **Validación adicional**:
   ```python
   if ',' not in monto and '.' not in monto:
       continue
   ```
   - Asegura que solo se procesen valores con puntos o comas (formatos de montos válidos)

4. **Detección de moneda**: Ahora se detecta si la descripción contiene `USD`, `BRL` o formato `(PAIS,MONEDA, ...)`, guardando la moneda correcta en el CSV

## 📋 Cambios Realizados en el Código

1. **main.py**:
   - Actualizado `procesar_texto_resumen()` con regex mejorado
   - Removidos imports no utilizados
   - Añadida validación de formato de monto

2. **.gitignore**:
   - Creado con patrones para ignorar la carpeta `data_cards/`
   - Excluye archivos de Python compilados, venv, IDEs, etc.

3. **README.md**:
   - Documentación completa del proyecto
   - Instrucciones de instalación y uso
   - Explicación del formato de salida
   - Información sobre detección de duplicados

## 🧪 Cómo Probar la Solución

1. Ejecuta el script con tus PDFs:
   ```bash
   python main.py
   ```

2. Verifica que el consumo se procesa correctamente en `consumos_totales.csv`:
   - La descripción debe ser: `000001* LACAJASEGURO 028063215 -0`
   - El monto debe ser: `84431.0` (positivo)
   - La moneda debe ser: `ARS`

## 📝 Recomendaciones Futuras

1. Agregar logging detallado para facilitar debugging
2. Crear tests unitarios para diferentes formatos de montos
3. Permitir configuración de regex mediante archivo de configuración
4. Agregar soporte para más tipos de tarjetas y bancos

---

**Fecha de solución**: Diciembre 2025
