import re

from piloto.hojas import EJERCICIOS_POR_PAGINA, generar
from piloto.muestras import cargar_catalogo


def test_genera_pagina_de_control_y_ejercicios(tmp_path):
    contenido = generar(tmp_path / "hojas.pdf").read_bytes()

    cantidad = len(cargar_catalogo())
    paginas_esperadas = 1 + -(-cantidad // EJERCICIOS_POR_PAGINA)
    paginas = len(re.findall(rb"/Type\s*/Page\b(?!s)", contenido))

    assert contenido.startswith(b"%PDF")
    assert paginas == paginas_esperadas
