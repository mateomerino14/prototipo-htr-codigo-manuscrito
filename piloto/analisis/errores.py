"""Analisis de errores caracter por caracter.

Alinea la referencia con la transcripcion (misma tabla de Levenshtein que el
CER) y clasifica cada diferencia segun el tipo de caracter afectado. Con esto
se puede responder que se equivoca cada herramienta, no solo cuanto.
"""

from piloto.metricas import normalizar

CORRECTO = "correcto"
SUSTITUCION = "sustitucion"
ELIMINACION = "eliminacion"
INSERCION = "insercion"

OPERADORES = set("+-*/%=<>!&|^~")
DELIMITADORES = set("()[]{}")
PUNTUACION = set(";:,.")
COMILLAS = set("'\"")


def clasificar_caracter(caracter):
    if caracter == "\n":
        return "salto_linea"
    if caracter == " ":
        return "espacio"
    if caracter.isdigit():
        return "digito"
    if caracter.isalpha():
        return "letra"
    if caracter in OPERADORES:
        return "operador"
    if caracter in DELIMITADORES:
        return "delimitador"
    if caracter in PUNTUACION:
        return "puntuacion"
    if caracter in COMILLAS:
        return "comillas"
    return "otro"


def alinear(referencia, hipotesis):
    """Devuelve la lista de operaciones (tipo, esperado, obtenido) de menor costo."""
    n, m = len(referencia), len(hipotesis)
    tabla = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        tabla[i][0] = i
    for j in range(m + 1):
        tabla[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            costo = referencia[i - 1] != hipotesis[j - 1]
            tabla[i][j] = min(tabla[i - 1][j] + 1, tabla[i][j - 1] + 1, tabla[i - 1][j - 1] + costo)

    # Se recorre la tabla desde el final para reconstruir el camino
    operaciones = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and tabla[i][j] == tabla[i - 1][j - 1] + (referencia[i - 1] != hipotesis[j - 1]):
            tipo = CORRECTO if referencia[i - 1] == hipotesis[j - 1] else SUSTITUCION
            operaciones.append((tipo, referencia[i - 1], hipotesis[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and tabla[i][j] == tabla[i - 1][j] + 1:
            operaciones.append((ELIMINACION, referencia[i - 1], ""))
            i -= 1
        else:
            operaciones.append((INSERCION, "", hipotesis[j - 1]))
            j -= 1

    operaciones.reverse()
    return operaciones


def analizar(referencia, hipotesis):
    """Lista de errores, cada uno con su tipo y la clase de caracter afectada.

    Los espacios al inicio de una linea de la referencia se cuentan como
    errores de indentacion, separados de los espacios normales.
    """
    errores = []
    en_sangria = True

    for tipo, esperado, obtenido in alinear(normalizar(referencia), normalizar(hipotesis)):
        if tipo != CORRECTO:
            caracter = esperado or obtenido
            clase = clasificar_caracter(caracter)
            if clase == "espacio" and en_sangria:
                clase = "indentacion"
            errores.append({"tipo": tipo, "clase": clase, "esperado": esperado, "obtenido": obtenido})

        if esperado == "\n":
            en_sangria = True
        elif esperado and esperado != " ":
            en_sangria = False

    return errores
