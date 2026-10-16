from nucleo.metricas import cer, cer_sin_espacios, levenshtein, normalizar, wer


def test_levenshtein_cadenas():
    assert levenshtein("kitten", "sitting") == 3
    assert levenshtein("", "abc") == 3
    assert levenshtein("igual", "igual") == 0


def test_levenshtein_listas():
    assert levenshtein(["int", "x", "=", "0"], ["int", "x", "=", "O"]) == 1


def test_normalizar_conserva_indentacion():
    texto = "\r\ndef f():\r\n    return 1   \r\n\r\n"
    assert normalizar(texto) == "def f():\n    return 1"


def test_cer_perfecto_y_total():
    assert cer("print(x)", "print(x)") == 0.0
    assert cer("ab", "") == 1.0


def test_cer_detecta_confusion_de_caracteres():
    assert cer("x = 0;", "x = O;") == 1 / 6


def test_indentacion_perdida():
    referencia = "if x:\n    y = 1"
    hipotesis = "if x:\ny = 1"
    assert cer(referencia, hipotesis) > 0
    assert cer_sin_espacios(referencia, hipotesis) == 0


def test_wer():
    assert wer("return a + b", "return a + 6") == 1 / 4


def test_referencia_vacia():
    assert cer("", "") == 0.0
    assert wer("", "algo") == 1.0
