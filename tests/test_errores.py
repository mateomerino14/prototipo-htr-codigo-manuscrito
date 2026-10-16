from nucleo.errores import (
    ELIMINACION, INSERCION, SUSTITUCION, alinear, analizar, clasificar_caracter,
)
from nucleo.metricas import levenshtein


def test_clasifica_caracteres():
    assert clasificar_caracter("a") == "letra"
    assert clasificar_caracter("0") == "digito"
    assert clasificar_caracter(";") == "puntuacion"
    assert clasificar_caracter("{") == "delimitador"
    assert clasificar_caracter("=") == "operador"
    assert clasificar_caracter('"') == "comillas"


def test_alineacion_coincide_con_levenshtein():
    ref, hip = "for (int i = 0;", "fer (int l = O:"
    errores = [op for op in alinear(ref, hip) if op[0] != "correcto"]
    assert len(errores) == levenshtein(ref, hip)


def test_detecta_confusion_cero_por_o():
    errores = analizar("x = 0;", "x = O;")
    assert errores == [{"tipo": SUSTITUCION, "clase": "digito", "esperado": "0", "obtenido": "O"}]


def test_separa_indentacion_de_espacios():
    errores = analizar("if x:\n    y = 1", "if x:\ny = 1")
    assert {e["clase"] for e in errores} == {"indentacion"}
    assert all(e["tipo"] == ELIMINACION for e in errores)


def test_espacio_interno_no_es_indentacion():
    errores = analizar("a = b", "a =b")
    assert errores[0]["clase"] == "espacio"


def test_insercion():
    errores = analizar("x;", "x;;")
    assert errores[0]["tipo"] == INSERCION
    assert errores[0]["clase"] == "puntuacion"
