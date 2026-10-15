from piloto.muestras import cargar_catalogo, cargar_muestras


def _crear_imagen(ruta):
    ruta.write_bytes(b"")  # para cargar muestras no se abre la imagen


def test_toma_la_referencia_del_banco(tmp_path):
    _crear_imagen(tmp_path / "P03_E02_foto.jpg")
    muestras, omitidas = cargar_muestras(tmp_path, cargar_catalogo())

    assert omitidas == []
    muestra = muestras[0]
    assert muestra.ejercicio == "P03"
    assert muestra.escritor == "E02"
    assert muestra.captura == "foto"
    assert muestra.lenguaje == "python"
    assert muestra.categoria == "condicional"
    assert muestra.referencia.startswith("def mayor")


def test_txt_propio_tiene_prioridad(tmp_path):
    _crear_imagen(tmp_path / "X001_E05_escaneo.png")
    (tmp_path / "X001_E05_escaneo.txt").write_text("x = 1\n", encoding="utf-8")
    muestras, _ = cargar_muestras(tmp_path, cargar_catalogo())

    assert muestras[0].referencia == "x = 1\n"
    assert muestras[0].lenguaje == "desconocido"


def test_metadatos_csv_completa_datos(tmp_path):
    _crear_imagen(tmp_path / "X002_E01_foto.jpg")
    (tmp_path / "X002_E01_foto.txt").write_text("int x;", encoding="utf-8")
    (tmp_path / "metadatos.csv").write_text(
        "muestra,lenguaje,curso\nX002_E01_foto,java,INTRO-A\n", encoding="utf-8"
    )
    muestras, _ = cargar_muestras(tmp_path, cargar_catalogo())

    assert muestras[0].lenguaje == "java"
    assert muestras[0].metadatos()["curso"] == "INTRO-A"


def test_omite_imagenes_sin_referencia(tmp_path):
    _crear_imagen(tmp_path / "suelta.jpg")
    muestras, omitidas = cargar_muestras(tmp_path, cargar_catalogo())

    assert muestras == []
    assert omitidas == ["suelta.jpg"]
