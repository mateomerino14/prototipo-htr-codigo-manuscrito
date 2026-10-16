# Protocolo de recolección de muestras

Este protocolo asegura que todas las muestras se capturen igual, para que las
diferencias en los resultados se deban a las herramientas HTR y no a la forma
en que se tomaron las imágenes.

## 1. Conjuntos

| Conjunto | Carpeta | Objetivo | Origen |
|---|---|---|---|
| Piloto | `datos/piloto/` | 2. Selección de herramientas | Ejercicios del banco copiados a mano |
| Evaluación | `datos/evaluacion/` | 6. Evaluación del prototipo | Exámenes y prácticas reales |

## 2. Escritores

- Cada persona que escribe recibe un código: `E01`, `E02`, ... Nunca se usa su nombre.
- La relación código-persona, si hace falta guardarla, queda fuera del repositorio.
- Para el piloto se recomiendan al menos 4 escritores distintos, para cubrir
  variedad de letra.

## 3. Escritura (conjunto piloto)

- Cada escritor recibe impresas las hojas de `python -m piloto.hojas` y copia
  los ejercicios en hojas blancas o cuadriculadas, con bolígrafo azul o negro, tal como lo haría en un examen.
- Un ejercicio por hoja o por recuadro, respetando la indentación del original.
- Si el escritor se equivoca, no corrige encima: tacha y sigue, como en un
  examen real. La referencia sigue siendo el código original.

## 4. Captura

| Captura | Cómo |
|---|---|
| `foto` | Celular, con luz natural o blanca, hoja completa y sin sombras, de frente |
| `escaneo` | Escáner o app de escaneo, 300 dpi, en color |

- Sin filtros ni recortes manuales: la imagen se guarda tal como sale.
- Formato JPG o PNG.

## 5. Nombre de los archivos

```
<ejercicio>_<escritor>_<captura>.<ext>
P03_E02_foto.jpg
J11_E04_escaneo.png
```

Con ese nombre, el piloto toma solo la referencia correcta desde
`ejercicios/` y registra lenguaje, categoría, escritor y tipo de captura.

## 6. Exámenes reales (conjunto evaluación)

- Antes de fotografiar, tapar nombre, código SIS y cualquier dato personal.
- Contar con la autorización del docente del curso.
- Nombre: `X<número>_<escritor>_<captura>.jpg` (por ejemplo `X001_E07_foto.jpg`).
- Junto a cada imagen va un `.txt` con el mismo nombre, con la transcripción
  exacta del código escrito por el estudiante, incluidos sus errores.
- Lenguaje y curso se registran en `datos/evaluacion/metadatos.csv`:

```
muestra,lenguaje,curso
X001_E07_foto,java,INTRO-A
```

## 7. Diseño sugerido para el piloto

24 ejercicios × 4 escritores × 2 tipos de captura = **192 muestras** por
herramienta. Con eso se pueden comparar las herramientas entre sí y además
por lenguaje, categoría de ejercicio, escritor y tipo de captura.
