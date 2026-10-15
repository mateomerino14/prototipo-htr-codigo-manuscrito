from piloto.motores.paddle import PaddleOCR
from piloto.motores.tesseract import Tesseract
from piloto.motores.trocr import TrOCR

MOTORES = {
    "tesseract": Tesseract,
    "paddleocr": PaddleOCR,
    "trocr": TrOCR,
}
