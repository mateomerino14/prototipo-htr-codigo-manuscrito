from nucleo.lenguajes import acierto_reservadas, detalle_reservadas, tokenizar


def test_tokeniza_solo_palabras():
    assert tokenizar("for (int i = 0; i < n; i++) {") == ["for", "int", "i", "i", "n", "i"]


def test_todas_las_reservadas_correctas():
    codigo = "while i <= n:\n    i += 1\nreturn i"
    assert acierto_reservadas(codigo, codigo, "python") == 1.0


def test_detecta_reservada_mal_reconocida():
    detalle = detalle_reservadas("public static void main", "pubic static void main", "java")
    fallidas = [d for d in detalle if not d["correcta"]]
    assert fallidas == [{"palabra": "public", "obtenido": "pubic", "correcta": False}]
    assert acierto_reservadas("public static void main", "pubic static void main", "java") == 2 / 3


def test_distingue_mayusculas():
    assert acierto_reservadas("return x", "Return x", "python") == 0.0


def test_reservada_perdida_cuenta_como_error():
    assert acierto_reservadas("if x:\n    return y", "x:\n    return y", "python") == 0.5


def test_sin_reservadas_o_lenguaje_desconocido():
    assert acierto_reservadas("x = y", "x = y", "python") is None
    assert acierto_reservadas("return x", "return x", "desconocido") is None


def test_banco_de_ejercicios_contra_si_mismo():
    from piloto.muestras import cargar_catalogo

    # P01 solo usa funciones predefinidas (int, input, print), no reservadas
    for id_ejercicio, ejercicio in cargar_catalogo().items():
        codigo = ejercicio["codigo"]
        assert acierto_reservadas(codigo, codigo, ejercicio["lenguaje"]) in (1.0, None), id_ejercicio
