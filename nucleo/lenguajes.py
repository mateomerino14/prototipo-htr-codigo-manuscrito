"""Palabras reservadas de Java y Python y su tasa de acierto en una transcripcion.

En codigo fuente no todas las palabras pesan igual: si se pierde un "while"
o un "return" el programa cambia de sentido. Por eso se mide aparte cuantas
palabras reservadas de la referencia quedaron exactamente iguales.
"""

import keyword
import re

from nucleo.errores import CORRECTO, alinear
from nucleo.metricas import normalizar

RESERVADAS_JAVA = frozenset("""
abstract assert boolean break byte case catch char class const continue default do
double else enum extends final finally float for goto if implements import instanceof
int interface long native new package private protected public return short static
strictfp super switch synchronized this throw throws transient try void volatile while
true false null var
""".split())

RESERVADAS_PYTHON = frozenset(keyword.kwlist)

PALABRAS_RESERVADAS = {
    "java": RESERVADAS_JAVA,
    "python": RESERVADAS_PYTHON,
}

PATRON_IDENTIFICADOR = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def tokenizar(texto):
    """Palabras del codigo (identificadores y reservadas), sin simbolos."""
    return PATRON_IDENTIFICADOR.findall(normalizar(texto))


def detalle_reservadas(referencia, hipotesis, lenguaje):
    """Una entrada por cada palabra reservada de la referencia.

    Cada entrada indica la palabra, lo que la herramienta obtuvo en su lugar
    y si coincide exactamente (se distinguen mayusculas, como en el codigo).
    """
    reservadas = PALABRAS_RESERVADAS.get(lenguaje)
    if not reservadas:
        return []

    detalle = []
    for tipo, esperado, obtenido in alinear(tokenizar(referencia), tokenizar(hipotesis)):
        if esperado in reservadas:
            detalle.append({
                "palabra": esperado,
                "obtenido": obtenido,
                "correcta": tipo == CORRECTO,
            })
    return detalle


def acierto_reservadas(referencia, hipotesis, lenguaje):
    """Proporcion de palabras reservadas reconocidas sin error (1 = todas).

    Devuelve None si el lenguaje no se conoce o la referencia no tiene
    palabras reservadas, para no mezclar esos casos en el promedio.
    """
    detalle = detalle_reservadas(referencia, hipotesis, lenguaje)
    if not detalle:
        return None
    return sum(entrada["correcta"] for entrada in detalle) / len(detalle)
