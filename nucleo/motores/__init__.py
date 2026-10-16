from nucleo.motores.azure_vision import AzureVision
from nucleo.motores.google_vision import GoogleVision
from nucleo.motores.paddle import PaddleOCR
from nucleo.motores.tesseract import Tesseract
from nucleo.motores.trocr import TrOCR

MOTORES = {
    "tesseract": Tesseract,
    "paddleocr": PaddleOCR,
    "trocr": TrOCR,
    "google": GoogleVision,
    "azure": AzureVision,
}
