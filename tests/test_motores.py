from nucleo.motores.base import agrupar_en_lineas


def test_agrupa_fragmentos_de_la_misma_linea():
    fragmentos = [
        ("x;", 120, 50, 20),
        ("int", 10, 52, 20),
        ("return", 10, 100, 20),
    ]
    assert agrupar_en_lineas(fragmentos) == "int x;\nreturn"
