"""Prueba el informe completo con resultados simulados de varias herramientas."""

import csv
import random

import pytest

from nucleo.errores import analizar
from nucleo.lenguajes import acierto_reservadas, detalle_reservadas
from piloto.analisis.informe import generar_informe
from piloto.muestras import cargar_catalogo

HERRAMIENTAS = {"Tesseract": 0.30, "PaddleOCR": 0.15, "TrOCR": 0.10}
CONFUSIONES = {"0": "O", "1": "l", ";": ":", "i": "l", "=": "-", "(": "C", "r": "n", "e": "c"}


def _ensuciar(texto, probabilidad, azar):
    """Simula una transcripcion con confusiones tipicas y sin indentacion."""
    salida = []
    for linea in texto.split("\n"):
        if azar.random() < probabilidad:
            linea = linea.lstrip()
        salida.append("".join(
            CONFUSIONES.get(c, c) if azar.random() < probabilidad else c for c in linea
        ))
    return "\n".join(salida)


def _escribir(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def crear_corrida(carpeta):
    """Escribe una corrida simulada completa en la carpeta indicada."""
    from nucleo.metricas import cer, cer_sin_espacios, wer

    azar = random.Random(7)
    catalogo = cargar_catalogo()
    detalle, errores, reservadas = [], [], []

    for herramienta, probabilidad in HERRAMIENTAS.items():
        for id_ejercicio, ejercicio in catalogo.items():
            for escritor, captura in (("E01", "foto"), ("E02", "escaneo")):
                referencia = ejercicio["codigo"]
                texto = _ensuciar(referencia, probabilidad, azar)
                muestra = f"{id_ejercicio}_{escritor}_{captura}"
                detalle.append({
                    "herramienta": herramienta, "muestra": muestra, "ejercicio": id_ejercicio,
                    "lenguaje": ejercicio["lenguaje"], "categoria": ejercicio["categoria"],
                    "escritor": escritor, "captura": captura,
                    "cer": cer(referencia, texto), "cer_sin_espacios": cer_sin_espacios(referencia, texto),
                    "wer": wer(referencia, texto),
                    "acierto_reservadas": acierto_reservadas(referencia, texto, ejercicio["lenguaje"]),
                    "segundos": azar.uniform(0.2, 3),
                })
                identificacion = {"herramienta": herramienta, "muestra": muestra,
                                  "lenguaje": ejercicio["lenguaje"]}
                for error in analizar(referencia, texto):
                    errores.append({**identificacion, **error})
                for palabra in detalle_reservadas(referencia, texto, ejercicio["lenguaje"]):
                    reservadas.append({**identificacion, **palabra})

    (carpeta / "tablas").mkdir(parents=True)
    _escribir(carpeta / "tablas" / "resultados_por_muestra.csv", detalle)
    _escribir(carpeta / "tablas" / "errores.csv", errores)
    _escribir(carpeta / "tablas" / "reservadas.csv", reservadas)
    return carpeta


@pytest.fixture
def corrida(tmp_path):
    return crear_corrida(tmp_path)


def test_genera_tablas_latex_y_graficas(corrida):
    generar_informe(corrida)

    estadisticas = {p.stem for p in (corrida / "tablas" / "estadisticas").glob("*.csv")}
    assert {"descriptivas_cer", "cer_por_lenguaje", "cer_por_categoria", "confusiones_frecuentes",
            "descriptivas_acierto_reservadas", "reservadas_por_lenguaje", "reservadas_mas_falladas"} <= estadisticas

    for tabla in ("descriptivas_cer", "reservadas_mas_falladas"):
        assert (corrida / "tablas" / "latex" / f"{tabla}.tex").exists()

    graficas = {p.name for p in (corrida / "graficas").iterdir()}
    for nombre in ("distribucion_cer", "impacto_indentacion", "cer_por_lenguaje",
                   "cer_por_categoria", "distribucion_errores", "confusiones_trocr",
                   "reservadas_por_lenguaje", "reservadas_falladas_tesseract"):
        assert f"{nombre}.png" in graficas
        assert f"{nombre}.pdf" in graficas
