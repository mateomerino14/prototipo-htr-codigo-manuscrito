import os
import shutil

from nucleo.motores.base import MotorHTR


# Linea base: pensado para texto impreso, no manuscrito
class Tesseract(MotorHTR):
    nombre = "Tesseract"
    CONFIGURACION = "--psm 6 -c preserve_interword_spaces=1"

    def disponible(self):
        try:
            import pytesseract  # noqa: F401
        except ImportError:
            return False, "falta instalar pytesseract"

        if not shutil.which("tesseract") and not os.environ.get("TESSERACT_CMD"):
            return False, "no se encontro el programa tesseract"
        return True, ""

    def transcribir(self, ruta_imagen):
        import pytesseract
        from PIL import Image

        if os.environ.get("TESSERACT_CMD"):
            pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]

        return pytesseract.image_to_string(
            Image.open(ruta_imagen), lang="eng", config=self.CONFIGURACION
        )
