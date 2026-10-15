import os

from piloto.motores.base import MotorHTR


class AzureVision(MotorHTR):
    """Requiere AZURE_VISION_ENDPOINT y AZURE_VISION_KEY del recurso en Azure."""

    nombre = "Azure AI Vision"

    def disponible(self):
        try:
            from azure.ai.vision.imageanalysis import ImageAnalysisClient  # noqa: F401
        except ImportError:
            return False, "falta instalar azure-ai-vision-imageanalysis"

        if not (os.environ.get("AZURE_VISION_ENDPOINT") and os.environ.get("AZURE_VISION_KEY")):
            return False, "faltan AZURE_VISION_ENDPOINT y AZURE_VISION_KEY"
        return True, ""

    def transcribir(self, ruta_imagen):
        from azure.ai.vision.imageanalysis import ImageAnalysisClient
        from azure.ai.vision.imageanalysis.models import VisualFeatures
        from azure.core.credentials import AzureKeyCredential

        cliente = ImageAnalysisClient(
            endpoint=os.environ["AZURE_VISION_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_VISION_KEY"]),
        )
        with open(ruta_imagen, "rb") as archivo:
            resultado = cliente.analyze(
                image_data=archivo.read(), visual_features=[VisualFeatures.READ]
            )

        if not resultado.read:
            return ""
        return "\n".join(
            linea.text for bloque in resultado.read.blocks for linea in bloque.lines
        )
