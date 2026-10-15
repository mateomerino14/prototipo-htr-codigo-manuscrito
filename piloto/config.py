from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

CARPETA_IMAGENES = RAIZ / "datos" / "imagenes"
CARPETA_REFERENCIAS = RAIZ / "datos" / "referencias"
CARPETA_RESULTADOS = RAIZ / "resultados" / "piloto"

EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
