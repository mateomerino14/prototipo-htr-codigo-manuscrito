from nucleo.motores.base import MotorHTR
from nucleo.segmentacion import segmentar_lineas


class TrOCR(MotorHTR):
    """TrOCR reconoce una sola linea a la vez, por eso se segmenta antes."""

    nombre = "TrOCR"
    MODELO = "microsoft/trocr-base-handwritten"
    MAX_TOKENS = 128

    def __init__(self):
        self._procesador = None
        self._modelo = None
        self._dispositivo = "cpu"

    def disponible(self):
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
        except ImportError:
            return False, "falta instalar torch y transformers"
        return True, ""

    def _cargar_modelo(self):
        if self._modelo is not None:
            return

        import torch
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel

        self._dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        self._procesador = TrOCRProcessor.from_pretrained(self.MODELO)
        self._modelo = VisionEncoderDecoderModel.from_pretrained(self.MODELO)
        self._modelo.to(self._dispositivo)

    def _reconocer_linea(self, imagen_linea):
        import torch

        pixeles = self._procesador(images=imagen_linea, return_tensors="pt").pixel_values
        with torch.no_grad():
            ids = self._modelo.generate(
                pixeles.to(self._dispositivo), max_new_tokens=self.MAX_TOKENS
            )
        return self._procesador.batch_decode(ids, skip_special_tokens=True)[0]

    def transcribir(self, ruta_imagen):
        self._cargar_modelo()
        lineas = [self._reconocer_linea(linea) for linea in segmentar_lineas(ruta_imagen)]
        return "\n".join(lineas)
