import csv
import shutil
import subprocess
from pathlib import Path

import pytest

# Una referencia con errores castigaria a las herramientas por algo que no es suyo
CARPETA = Path(__file__).resolve().parents[1] / "ejercicios"


def _catalogo():
    with open(CARPETA / "catalogo.csv", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def test_catalogo_apunta_a_archivos_existentes():
    for fila in _catalogo():
        assert (CARPETA / fila["archivo"]).exists(), fila["id"]


def test_ids_unicos():
    ids = [fila["id"] for fila in _catalogo()]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("fila", [f for f in _catalogo() if f["lenguaje"] == "python"], ids=lambda f: f["id"])
def test_python_compila(fila):
    codigo = (CARPETA / fila["archivo"]).read_text(encoding="utf-8")
    compile(codigo, fila["archivo"], "exec")


@pytest.mark.skipif(shutil.which("javac") is None, reason="javac no esta instalado")
def test_java_compila(tmp_path):
    archivos = [str(CARPETA / f["archivo"]) for f in _catalogo() if f["lenguaje"] == "java"]
    resultado = subprocess.run(["javac", "-d", str(tmp_path), *archivos], capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stderr
