# Personal Finance PDF Extractor

Pequeña herramienta para extraer consumos (transacciones) desde resúmenes/estados de tarjetas en PDF y consolidarlos en un CSV.

Estado: trabajo en progreso

---

Contenido
- Descripción
- Requisitos
- Instalación
- Uso
- Estructura del proyecto
- Formato esperado de los PDFs
- Solución de problemas (incluye PdfminerException)
- .gitignore recomendado

---

Descripción
-----------
Este proyecto abre archivos PDF (resúmenes de tarjetas) ubicados en la carpeta `data_cards/`, extrae el texto de cada página y busca patrones para identificar consumos (fecha, descripción, monto). Los consumos detectados se normalizan, se eliminan duplicados y se guardan en `consumos_totales.csv`.

Requisitos
----------
- Python 3.8+
- Dependencias listadas en `requirements.txt` (pdfplumber, pandas, etc.)

Instalación
-----------
Recomendado crear un entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Uso
---
1. Coloca tus PDFs en la carpeta `data_cards/` del proyecto.
2. (Opcional) Si tus PDFs están protegidos con contraseña y conoces la contraseña, puedes configurar la variable `password_pdf` en `main.py` o exportar una variable de entorno con el nombre configurado (por ejemplo `PDF_PASSWORD`) y modificar el código para leerla.
3. Ejecuta el script principal:

```bash
python main.py
```

Resultados
- `consumos_totales.csv`: CSV con los consumos únicos detectados.
- `consumos_totales.txt`: (si se usa) salida de texto con consumos.
- `data_cards/tmp_debug/`: durante la ejecución se crean archivos `texto_extraido_<nombre_pdf>.txt` para cada PDF procesado (su contenido ayuda a depurar patrones de extracción). El directorio temporal se elimina al final si hay resultados.

Estructura del proyecto
----------------------
- `main.py` - script principal que busca PDFs, abre cada uno (intenta sin contraseña y con contraseña configurada), extrae texto, procesa patrones y genera el CSV.
- `data_cards/` - carpeta donde colocar los PDF (ignorada en `.gitignore` recomendada).
- `consumos_totales.csv` - salida generada.
- `requirements.txt` - dependencias del proyecto.

Formato esperado de PDFs / patrones
----------------------------------
El procesador busca líneas que contengan una fecha y un monto con formato local (ej.: `01.07.25 DESCRIPCION 1.234,56`) y también variantes en USD.
Si tus PDFs tienen formato distinto (columnas separadas, tablas embebidas, o texto con saltos de línea intermedios), puede que los patrones no coincidan y no se detecten consumos.

Solución de problemas
---------------------
- PdfminerException (o `Pdfplumber` levantando excepciones):
  - Sucede cuando `pdfplumber` no puede leer el PDF (archivo corrupto, cifrado con contraseña desconocida, o formato no soportado).
  - Recomendaciones:
    1. Revisa los archivos de depuración `data_cards/tmp_debug/texto_extraido_<pdf>.txt` (si existen) para ver qué texto fue extraído antes de fallar.
    2. Si el PDF está cifrado, asegúrate de conocer la contraseña. Puedes:
       - Configurar `password_pdf` en `main.py` (por ahora está establecido en el script) o modificar el código para leer la variable de entorno `PDF_PASSWORD`.
       - Usar herramientas externas (ej. `qpdf --decrypt`) para generar una versión sin contraseña.
    3. Si la extracción produce texto vacío o malformado, prueba con otro extractor (ej. `pdftotext`) para comparar.
    4. En logs puedes añadir prints o usar `logging` para capturar excepciones completas (stacktrace) y el nombre del archivo que causa el error.

- No se encuentran consumos:
  - Los patrones regex del script esperan fechas y montos en formatos concretos. Abre el `texto_extraido_<pdf>.txt` y verifica cómo están las líneas para ajustar `procesar_texto_resumen()` en `main.py`.

.gitignore recomendado
----------------------
El repositorio incluye ahora un archivo `.gitignore` en la raíz con las reglas recomendadas para este proyecto. El archivo ya fue creado y excluye, entre otras cosas, los PDFs personales en `data_cards/`.

Contenido del `.gitignore` creado:

```text
# Ignore all files in data_cards (keep the folder if you want)
data_cards/*
!data_cards/.gitkeep

# Output files
consumos_totales.csv
consumos_totales.txt

# Python cache and compiled files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
.venv/
venv/
ENV/
env/

# Build/dist
build/
dist/
*.egg-info/

# IDE/editor
.vscode/
.idea/
*.swp

# Logs and temp
*.log
*.tmp

# pytest
.pytest_cache/

# Jupyter
.ipynb_checkpoints

# macOS
.DS_Store
```

Nota: si prefieres no versionar la carpeta `data_cards/` pero mantenerla en el repositorio, añade manualmente un archivo vacío `data_cards/.gitkeep`.

Buenas prácticas y próximos pasos
--------------------------------
- Extraer la lógica de procesamiento de texto a un módulo separado para facilitar pruebas unitarias.
- Añadir tests (pytest) con ejemplos de texto extraído y casos borde (montos negativos, IVA, devoluciones).
- Hacer la contraseña configurable por variable de entorno y documentarla en este README.
- Añadir logging nivel DEBUG para diagnosticar `PdfminerException` cuando ocurran.

Contacto
--------
Si necesitas que adapte los regex para tus PDFs concretos, comparte un ejemplo (el contenido del `texto_extraido_*.txt`) y te ayudo a ajustar `procesar_texto_resumen()`.
