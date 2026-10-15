import pandas as pd

from piloto.analisis.tablas_latex import escapar, tabla_a_latex


def test_escapa_caracteres_especiales():
    assert escapar("a_b") == r"a\_b"
    assert escapar("50%") == r"50\%"
    assert escapar("{") == r"\{"
    assert escapar(" ") == r"\textvisiblespace"


def test_genera_tabular_completo():
    tabla = pd.DataFrame([{"herramienta": "TrOCR", "media": 0.12345}])
    tex = tabla_a_latex(tabla, "Prueba")
    assert r"\begin{tabular}{|l|c|}" in tex
    assert r"TrOCR & 0.123 \\" in tex
    assert r"\textit{Prueba}" in tex
