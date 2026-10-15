# Prototipo HTR para código manuscrito

Prototipo que integra herramientas HTR de acceso público para transcribir a
texto plano el código fuente manuscrito (Java y Python) de exámenes y
prácticas de los cursos introductorios de programación de la FCyT-UMSS.

Proyecto de Grado — Mateo Alejandro Merino Vidal.

## Estructura

```
prototipo-htr-codigo-manuscrito/
├── piloto/                 Prueba piloto de selección de herramientas (objetivo 2)
│   ├── __main__.py         Ejecución del piloto
│   ├── config.py           Rutas y constantes
│   ├── metricas.py         CER, CER sin espacios y WER
│   ├── segmentacion.py     Separación de la imagen en líneas
│   ├── reporte.py          Exportación a CSV y tabla en consola
│   └── motores/            Un conector por herramienta HTR
├── datos/                  Imágenes y referencias (no se suben al repo)
├── tests/
└── requirements.txt
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

## Datos

Cada imagen en `datos/imagenes/` necesita un `.txt` con el mismo nombre en
`datos/referencias/`, con el código tal como está escrito en la hoja:
mismos saltos de línea e indentación con espacios, guardado en UTF-8.

```
datos/imagenes/ejercicio01.jpg
datos/referencias/ejercicio01.txt
```

Esta carpeta está en `.gitignore`: las imágenes de exámenes pueden contener
datos de estudiantes y no deben subirse al repositorio.

## Prueba piloto

```bash
python -m piloto                             # todas las herramientas disponibles
python -m piloto --motores tesseract trocr   # solo algunas
```

Las herramientas sin instalar o sin credenciales se marcan como no disponibles
y el piloto continúa con las demás. En `resultados/piloto/` se generan:

| Archivo | Contenido |
|---|---|
| `tabla_piloto.csv` | Promedio de cada herramienta |
| `resultados_por_imagen.csv` | Métricas de cada imagen con cada herramienta |
| `transcripciones/<herramienta>/` | Texto obtenido por cada herramienta |

### Métricas

Todas van de 0 (perfecto) hacia arriba.

| Métrica | Qué mide |
|---|---|
| CER | Caracteres mal reconocidos, incluyendo espacios e indentación |
| CER sin espacios | Solo caracteres visibles. Si es bajo y el CER alto, el error está en la indentación |
| WER | Palabras mal reconocidas |

### Google Cloud Vision y Azure AI Vision

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
