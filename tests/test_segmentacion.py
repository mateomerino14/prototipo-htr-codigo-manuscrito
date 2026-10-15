from PIL import Image, ImageDraw, ImageFont

from piloto.segmentacion import segmentar_lineas


def _imagen_con_lineas(ruta, lineas):
    try:
        fuente = ImageFont.truetype("DejaVuSansMono.ttf", 28)
    except OSError:
        fuente = ImageFont.load_default()

    imagen = Image.new("RGB", (600, 60 + 60 * len(lineas)), "white")
    dibujo = ImageDraw.Draw(imagen)
    for i, linea in enumerate(lineas):
        dibujo.text((20, 30 + i * 60), linea, fill="black", font=fuente)
    imagen.save(ruta)


def test_detecta_una_imagen_por_linea(tmp_path):
    ruta = tmp_path / "codigo.png"
    _imagen_con_lineas(ruta, ["int x = 0;", "x = x + 1;", "System.out.println(x);"])
    assert len(segmentar_lineas(ruta)) == 3
