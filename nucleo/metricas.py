def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a

    fila_anterior = list(range(len(b) + 1))
    for i, elem_a in enumerate(a, start=1):
        fila_actual = [i]
        for j, elem_b in enumerate(b, start=1):
            eliminacion = fila_anterior[j] + 1
            insercion = fila_actual[j - 1] + 1
            sustitucion = fila_anterior[j - 1] + (elem_a != elem_b)
            fila_actual.append(min(eliminacion, insercion, sustitucion))
        fila_anterior = fila_actual

    return fila_anterior[-1]


def normalizar(texto):
    # La indentacion se conserva porque en Python es parte del codigo
    lineas = texto.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lineas = [linea.rstrip() for linea in lineas]

    while lineas and not lineas[0]:
        lineas.pop(0)
    while lineas and not lineas[-1]:
        lineas.pop()

    return "\n".join(lineas)


def _tasa_error(referencia, hipotesis):
    if not referencia:
        return 0.0 if not hipotesis else 1.0
    return levenshtein(referencia, hipotesis) / len(referencia)


def cer(referencia, hipotesis):
    return _tasa_error(normalizar(referencia), normalizar(hipotesis))


# Si este es bajo y el CER alto, el error esta en la indentacion
def cer_sin_espacios(referencia, hipotesis):
    ref = "".join(normalizar(referencia).split())
    hip = "".join(normalizar(hipotesis).split())
    return _tasa_error(ref, hip)


def wer(referencia, hipotesis):
    ref = normalizar(referencia).split()
    hip = normalizar(hipotesis).split()
    return _tasa_error(ref, hip)
