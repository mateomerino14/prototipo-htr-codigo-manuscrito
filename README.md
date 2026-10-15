# Prototipo HTR para código manuscrito

Prototipo que integra herramientas HTR de acceso público para transcribir a
texto plano el código fuente manuscrito (Java y Python) de exámenes y
prácticas de los cursos introductorios de programación de la FCyT-UMSS.

Proyecto de Grado — Mateo Alejandro Merino Vidal.

## Estructura

```
prototipo-htr-codigo-manuscrito/
├── ejercicios/              Banco de ejercicios de referencia (24: Java y Python)
│   ├── catalogo.csv         Id, lenguaje y categoría de cada ejercicio
│   ├── java/
│   └── python/
├── datos/                   Muestras manuscritas (no se suben al repositorio)
│   ├── piloto/              Objetivo 2: selección de herramientas
│   └── evaluacion/          Objetivo 6: evaluación del prototipo
├── piloto/                  Prueba piloto
│   ├── __main__.py          Ejecución
│   ├── muestras.py          Carga de muestras y metadatos
│   ├── metricas.py          CER, CER sin espacios y WER
│   ├── segmentacion.py      Separación de la imagen en líneas
│   ├── motores/             Un conector por herramienta HTR
│   └── analisis/            Errores, estadísticas, gráficas y tablas LaTeX
├── resultados/              Una carpeta por corrida (no se sube)
├── docs/
│   └── protocolo_muestras.md
└── tests/
```

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
```

La primera ejecución descarga los modelos de TrOCR (unos 1,3 GB) y de PaddleOCR.

Tesseract necesita además el programa instalado:

- **Windows:** instalador de UB Mannheim (github.com/UB-Mannheim/tesseract/wiki).
  Si no queda en el PATH, definir `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`.
- **Linux:** `sudo apt install tesseract-ocr`.

## Muestras

La forma de recolectar, anonimizar y nombrar las muestras está en
[`docs/protocolo_muestras.md`](docs/protocolo_muestras.md). En resumen:

```
datos/piloto/P03_E02_foto.jpg     ejercicio P03, escritor E02, capturado con foto
```

Con ese nombre la referencia se toma sola del banco de ejercicios. Para
exámenes reales, junto a la imagen va un `.txt` con su transcripción exacta.

## Ejecución

```bash
python -m piloto                               # conjunto datos/piloto, todas las herramientas
python -m piloto --motores tesseract trocr     # solo algunas herramientas
python -m piloto --conjunto evaluacion         # otro conjunto de datos
python -m piloto.analisis                      # regenera el informe de la última corrida
```

Las herramientas sin instalar o sin credenciales se marcan como no
disponibles y el piloto continúa con las demás.

## Resultados

Cada corrida queda en `resultados/<conjunto>/<fecha_hora>/`:

```
ejecucion.json                   Fecha, herramientas, versión de Python y resumen
transcripciones/<herramienta>/   Texto obtenido por cada herramienta
tablas/
├── resultados_por_muestra.csv   Métricas de cada muestra con cada herramienta
├── resumen_herramientas.csv     Promedios por herramienta
├── errores.csv                  Cada error de carácter: tipo, clase, esperado y obtenido
├── estadisticas/                Media, mediana, desviación, comparaciones por factor
└── latex/                       Tablas listas para \input{} en el documento
graficas/                        PNG (300 dpi) y PDF de cada gráfica
```

### Métricas

| Métrica | Qué mide |
|---|---|
| CER | Proporción de caracteres mal reconocidos, incluyendo espacios e indentación |
| CER sin espacios | Solo caracteres visibles. Si es bajo y el CER alto, el error está en la indentación |
| WER | Proporción de palabras mal reconocidas |

Todas van de 0 (transcripción perfecta) hacia arriba.

### Análisis de errores

Cada transcripción se alinea carácter por carácter con su referencia. Cada
diferencia se clasifica por tipo (sustitución, eliminación, inserción) y por
clase de carácter: letra, dígito, operador, delimitador, puntuación,
comillas, espacio, indentación o salto de línea.

### Gráficas

| Gráfica | Qué muestra |
|---|---|
| `distribucion_cer` | Diagrama de caja del CER por herramienta |
| `impacto_indentacion` | CER con y sin espacios |
| `cer_por_lenguaje`, `cer_por_captura` | CER promedio por factor |
| `cer_por_categoria` | Mapa de calor herramienta × categoría de ejercicio |
| `distribucion_errores` | Porcentaje de errores por clase de carácter |
| `confusiones_<herramienta>` | Sustituciones más frecuentes |
| `tiempo_por_herramienta` | Tiempo promedio por muestra |

Cada herramienta mantiene el mismo color y trama en todas las gráficas, de
modo que también se distinguen al imprimir en blanco y negro.

## Google Cloud Vision y Azure AI Vision

```bash
pip install -r requirements-nube.txt
```

- **Google:** cuenta de servicio con la API Cloud Vision habilitada y
  `GOOGLE_APPLICATION_CREDENTIALS=ruta\a\clave.json`.
- **Azure:** recurso Computer Vision y las variables `AZURE_VISION_ENDPOINT`
  y `AZURE_VISION_KEY`.

Las claves van siempre en variables de entorno, nunca dentro del repositorio.

## Pruebas

```bash
python -m pytest
```

Incluyen la validación de que todos los ejercicios del banco compilan (Java
solo si `javac` está instalado).
