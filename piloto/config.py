from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

CARPETA_EJERCICIOS = RAIZ / "ejercicios"
CARPETA_DATOS = RAIZ / "datos"
CARPETA_RESULTADOS = RAIZ / "resultados"

CONJUNTO_POR_DEFECTO = "piloto"
FORMATO_CORRIDA = "%Y%m%d_%H%M%S"

EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
