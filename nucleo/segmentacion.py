import cv2
import numpy as np
from PIL import Image

MARGEN = 6
ALTO_MINIMO = 12
UMBRAL_TINTA = 0.01


def _binarizar(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (3, 3), 0)
    _, binaria = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binaria


def _detectar_bandas(binaria):
    ancho = binaria.shape[1]
    perfil = binaria.sum(axis=1) / 255 / ancho
    filas_con_tinta = perfil > UMBRAL_TINTA

    bandas = []
    inicio = None
    for y, hay_tinta in enumerate(filas_con_tinta):
        if hay_tinta and inicio is None:
            inicio = y
        elif not hay_tinta and inicio is not None:
            bandas.append([inicio, y])
            inicio = None
    if inicio is not None:
        bandas.append([inicio, len(filas_con_tinta)])

    return bandas


def _unir_bandas_cercanas(bandas):
    # Evita que el punto de una "i" o de un ";" quede como linea aparte
    unidas = []
    for banda in bandas:
        if unidas and banda[0] - unidas[-1][1] < ALTO_MINIMO // 2:
            unidas[-1][1] = banda[1]
        else:
            unidas.append(banda)
    return [b for b in unidas if b[1] - b[0] >= ALTO_MINIMO]


# Corta la imagen en lineas con el perfil de proyeccion horizontal
def segmentar_lineas(ruta_imagen):
    imagen = cv2.imread(str(ruta_imagen))
    if imagen is None:
        raise ValueError(f"No se pudo abrir la imagen: {ruta_imagen}")

    binaria = _binarizar(imagen)
    alto, ancho = binaria.shape
    rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

    lineas = []
    for y0, y1 in _unir_bandas_cercanas(_detectar_bandas(binaria)):
        columnas = np.where(binaria[y0:y1].sum(axis=0) > 0)[0]
        x0 = max(int(columnas.min()) - MARGEN, 0)
        x1 = min(int(columnas.max()) + MARGEN, ancho)
        recorte = rgb[max(y0 - MARGEN, 0):min(y1 + MARGEN, alto), x0:x1]
        lineas.append(Image.fromarray(recorte))

    return lineas
