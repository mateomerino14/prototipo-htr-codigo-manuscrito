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
    return PATRON_IDENTIFICADOR.findall(normalizar(texto))


def detalle_reservadas(referencia, hipotesis, lenguaje):
    reservadas = PALABRAS_RESERVADAS.get(lenguaje)
    if not reservadas:
        return []

    detalle = []
    for tipo, esperado, obtenido in alinear(tokenizar(referencia), tokenizar(hipotesis)):
        if esperado in reservadas:
            detalle.append({
                "palabra": esperado,
                "obtenido": obtenido,
                # Distingue mayusculas: en codigo Return no es return
                "correcta": tipo == CORRECTO,
            })
    return detalle


# None si no hay reservadas, para no mezclar ese caso en el promedio
def acierto_reservadas(referencia, hipotesis, lenguaje):
    detalle = detalle_reservadas(referencia, hipotesis, lenguaje)
    if not detalle:
        return None
    return sum(entrada["correcta"] for entrada in detalle) / len(detalle)
