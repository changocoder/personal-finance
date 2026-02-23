# 📚 Índice de Documentación del Proyecto

**Personal Finance App** - Herramienta para extraer y procesar consumos de tarjetas de crédito desde PDFs.

---

## 🗂️ Documentación por Temas

### 🚀 Para Empezar (Lee Primero)

1. **[README.md](README.md)**
   - Overview del proyecto
   - Cómo instalar y usar
   - Estructura de carpetas
   - Formato de salida CSV

2. **[IMPLEMENTACION_LOGGING.md](IMPLEMENTACION_LOGGING.md)** ⭐
   - **Resumen completo** de lo que se agregó
   - Qué obtienes con los logs
   - Cómo empezar a usar
   - Casos de uso prácticos

### 📊 Logging Detallado

3. **[GUIA_LOGGING.md](GUIA_LOGGING.md)**
   - Guía **más completa y detallada** del logging
   - Todas las características
   - Niveles de log
   - Ejemplos prácticos
   - Cómo usar para verificación

4. **[CAMBIOS_LOGGING.md](CAMBIOS_LOGGING.md)**
   - Qué cambios específicos se hicieron
   - Cómo funciona cada parte
   - Ejemplos de output
   - Ventajas del sistema

5. **[EJEMPLO_OUTPUT_LOGGING.md](EJEMPLO_OUTPUT_LOGGING.md)**
   - Ejemplo real de output completo
   - Explicación sección por sección
   - Qué información extraer
   - Cómo interpretar

### 🔍 Comandos Prácticos

6. **[COMANDOS_LOGS.md](COMANDOS_LOGS.md)**
   - Colección de comandos `grep` útiles
   - Buscar consumos específicos
   - Encontrar problemas
   - Calcular estadísticas
   - Casos de uso avanzados

### 🐛 Solución de Problemas

7. **[SOLUCION_PARSING.md](SOLUCION_PARSING.md)**
   - Problema del parsing de montos
   - Solución implementada
   - Cómo funciona ahora
   - Mejoras realizadas

### 🏷️ Clasificación de Consumos

8. **[CATEGORIAS.md](CATEGORIAS.md)**
   - Sistema de clasificación automática
   - Categorías disponibles (Utilities, Investment, Food, Household, Discretionary, Other)
   - Palabras clave por categoría
   - Cómo personalizar las categorías
   - Ejemplos de clasificación

### 💱 Pesificación de Consumos

9. **[PESIFICACION.md](PESIFICACION.md)**
   - Conversión automática de USD a ARS
   - Obtención de cotización del dólar oficial
   - Metadata incluida en el CSV
   - Configuración de fuentes de cotización

### 📝 Historial de Cambios

10. **[CHANGELOG.md](CHANGELOG.md)**
    - Registro de todas las iteraciones y cambios
    - Nuevas funcionalidades agregadas
    - Correcciones realizadas
    - Refactorizaciones del código

### 📧 Envío de Reportes por Email

11. **[EMAIL.md](EMAIL.md)**
    - Configuración de envío de email
    - Variables de entorno requeridas
    - Configuración de Gmail y otros proveedores
    - Flag para habilitar/deshabilitar la funcionalidad

### 🔔 Sistema de Notificaciones

12. **[NOTIFICACIONES.md](NOTIFICACIONES.md)**
    - Arquitectura del sistema de notificaciones
    - Patrón Protocol (Duck Typing)
    - Cómo agregar nuevos notificadores
    - Factory pattern para crear notificadores

---

## 📖 Guía de Lectura Recomendada

### Si eres nuevo en el proyecto:
1. Lee **README.md** (2 min)
2. Lee **IMPLEMENTACION_LOGGING.md** (5 min)
3. Ejecuta `python main.py`
4. Revisa el archivo `procesamiento_consumos.log` generado

### Si quieres entender los logs en profundidad:
1. Lee **GUIA_LOGGING.md** (10 min)
2. Consulta **EJEMPLO_OUTPUT_LOGGING.md** para ver ejemplos (5 min)
3. Usa **COMANDOS_LOGS.md** para buscar información (consultable)

### Si quieres aprender comandos:
1. Consulta **COMANDOS_LOGS.md**
2. Copia y adapta los comandos a tus necesidades
3. Experimenta con `grep` en el log

### Si tienes un problema específico:
1. **¿Falta un consumo?** → Lee "Caso 3" en GUIA_LOGGING.md
2. **¿Monto incorrecto?** → Lee SOLUCION_PARSING.md
3. **¿No sabes qué comando usar?** → Consulta COMANDOS_LOGS.md
4. **¿No entienden los logs?** → Lee EJEMPLO_OUTPUT_LOGGING.md

---

## 🎯 Quick Links (Búsquedas Rápidas)

### Verificar un consumo específico
Abre: **GUIA_LOGGING.md** → Sección "Caso 1: Verificar si un consumo específico fue extraído"

### Ver montos que se convirtieron
Abre: **COMANDOS_LOGS.md** → Sección "Montos y Conversiones"

### Encontrar líneas excluidas
Abre: **COMANDOS_LOGS.md** → Sección "Líneas Excluidas"

### Entender el problema de los montos
Abre: **SOLUCION_PARSING.md** → Sección "Problema Identificado"

### Buscar duplicados
Abre: **COMANDOS_LOGS.md** → Sección "Duplicados"

---

## 📂 Archivos del Proyecto

```
personal-finance-app/
│
├── 📄 ARCHIVOS DE CÓDIGO
│   ├── main.py                      # Script principal (con logging agregado)
│   ├── requirements.txt             # Dependencias Python
│   └── .gitignore                   # Archivo git (ignora data_cards/)
│
├── 📚 DOCUMENTACIÓN
│   ├── README.md                    # Overview del proyecto
│   ├── IMPLEMENTACION_LOGGING.md    # Resumen de logging (LEE PRIMERO)
│   ├── GUIA_LOGGING.md              # Guía detallada de logging
│   ├── CAMBIOS_LOGGING.md           # Qué se cambió
│   ├── EJEMPLO_OUTPUT_LOGGING.md    # Ejemplo de output
│   ├── COMANDOS_LOGS.md             # Comandos útiles para logs
│   ├── SOLUCION_PARSING.md          # Solución del problema de montos
│   └── INDICE.md                    # Este archivo
│
├── 📊 ARCHIVOS GENERADOS
│   ├── consumos_totales.csv         # Output: consumos extraídos
│   └── procesamiento_consumos.log   # Output: logs detallados
│
├── 📁 CARPETAS
│   └── data_cards/                  # Tus PDFs (ignorada en git)
│       └── .gitkeep
│
└── 🔧 SISTEMA
    └── __pycache__/                 # Cache de Python (ignorado)
```

---

## 🔑 Términos Clave

| Término | Definición |
|---------|-----------|
| **Log** | Registro detallado de lo que hace el script |
| **Logging** | Sistema de registrar información |
| **Consumo** | Una línea en tu tarjeta (compra o gasto) |
| **Duplicado** | Mismo consumo en dos PDFs o archivos |
| **Monto** | Cantidad de dinero (precio del consumo) |
| **ARS** | Pesos argentinos (moneda local) |
| **USD** | Dólares estadounidenses |
| **DEBUG** | Información técnica detallada |
| **INFO** | Información general normal |
| **WARNING** | Advertencia (algo sospechoso) |
| **ERROR** | Error (problema grave) |

---

## ✅ Checklist de Lectura

- [ ] Leí README.md
- [ ] Leí IMPLEMENTACION_LOGGING.md
- [ ] Ejecuté `python main.py`
- [ ] Abrí procesamiento_consumos.log
- [ ] Leí GUIA_LOGGING.md
- [ ] Probé algunos comandos de COMANDOS_LOGS.md
- [ ] Entiendo ahora cómo funciona el logging
- [ ] Puedo verificar mis consumos fácilmente

---

## 🚀 Próximos Pasos

1. **Ejecuta el script**: `python main.py`
2. **Revisa los logs**: `cat procesamiento_consumos.log`
3. **Busca tus consumos**: `grep "descripcion" procesamiento_consumos.log`
4. **Verifica en CSV**: Abre `consumos_totales.csv`

---

## 💬 Preguntas Frecuentes

**P: ¿Por dónde empiezo?**
R: Empieza con README.md luego IMPLEMENTACION_LOGGING.md

**P: ¿Dónde están los logs?**
R: En el archivo `procesamiento_consumos.log` (se crea cuando ejecutas main.py)

**P: ¿Cómo busco un consumo específico?**
R: Usa: `grep "descripcion" procesamiento_consumos.log`
Ver ejemplos en COMANDOS_LOGS.md

**P: ¿Por qué falta un consumo en el CSV?**
R: Busca en logs (puede estar excluido o ser inválido)
Ver "Caso 3" en GUIA_LOGGING.md

**P: ¿Dónde está la documentación de X?**
R: Usa este índice para encontrar rápidamente

---

## 🎓 Niveles de Profundidad

### Nivel 1: Usuario Básico
Lee: README.md + IMPLEMENTACION_LOGGING.md
Acciones: Ejecuta y revisa archivos de salida

### Nivel 2: Usuario Intermedio
Lee: GUIA_LOGGING.md + EJEMPLO_OUTPUT_LOGGING.md
Acciones: Busca consumos, verifica montos

### Nivel 3: Power User
Lee: COMANDOS_LOGS.md + CAMBIOS_LOGGING.md
Acciones: Análisis avanzado, scripts propios, customización

### Nivel 4: Developer
Lee: Código de main.py + SOLUCION_PARSING.md
Acciones: Modificar código, agregar features

---

## 📞 Soporte

Si no encuentras lo que buscas:

1. **Busca en los archivos**: Usa `grep -i "termino" *.md`
2. **Consulta el índice**: Este archivo
3. **Revisa EJEMPLO_OUTPUT_LOGGING.md**: Muestra qué esperar
4. **Lee COMANDOS_LOGS.md**: Tiene muchos ejemplos

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2025  
**Estado**: ✅ Completo y listo para usar


