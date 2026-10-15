import os

from piloto.motores.base import MotorHTR


class GoogleVision(MotorHTR):
    """Requiere GOOGLE_APPLICATION_CREDENTIALS apuntando a la clave JSON."""

    nombre = "Google Cloud Vision"

    def disponible(self):
        try:
            from google.cloud import vision  # noqa: F401
        except ImportError:
            return False, "falta instalar google-cloud-vision"

        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            return False, "falta la variable GOOGLE_APPLICATION_CREDENTIALS"
        return True, ""

    def transcribir(self, ruta_imagen):
        from google.cloud import vision

        cliente = vision.ImageAnnotatorClient()
        with open(ruta_imagen, "rb") as archivo:
            imagen = vision.Image(content=archivo.read())

        # document_text_detection es el modo pensado para texto denso y manuscrito
        respuesta = cliente.document_text_detection(
            image=imagen, image_context={"language_hints": ["en"]}
        )
        if respuesta.error.message:
            raise RuntimeError(respuesta.error.message)

        return respuesta.full_text_annotation.text
