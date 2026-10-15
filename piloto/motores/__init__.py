from piloto.motores.azure_vision import AzureVision
from piloto.motores.google_vision import GoogleVision
from piloto.motores.paddle import PaddleOCR
from piloto.motores.tesseract import Tesseract
from piloto.motores.trocr import TrOCR

MOTORES = {
    "tesseract": Tesseract,
    "paddleocr": PaddleOCR,
    "trocr": TrOCR,
    "google": GoogleVision,
    "azure": AzureVision,
}
