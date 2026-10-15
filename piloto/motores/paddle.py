from piloto.motores.base import MotorHTR, agrupar_en_lineas


class PaddleOCR(MotorHTR):
    nombre = "PaddleOCR"

    def __init__(self):
        self._ocr = None
        self._es_version_3 = True

    def disponible(self):
        try:
            import paddleocr  # noqa: F401
        except ImportError:
            return False, "falta instalar paddleocr y paddlepaddle"
        return True, ""

    def _cargar_modelo(self):
        if self._ocr is not None:
            return

        from paddleocr import PaddleOCR as ClientePaddle

        # La version 3 cambio los parametros del constructor y la forma de predecir
        try:
            self._ocr = ClientePaddle(
                lang="en",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            self._es_version_3 = hasattr(self._ocr, "predict")
        except (TypeError, ValueError):
            self._ocr = ClientePaddle(lang="en", use_angle_cls=True, show_log=False)
            self._es_version_3 = False

    def _fragmentos_version_3(self, ruta_imagen):
        fragmentos = []
        for resultado in self._ocr.predict(str(ruta_imagen)):
            datos = resultado if "rec_texts" in resultado else resultado.json["res"]
            for texto, (x0, y0, x1, y1) in zip(datos["rec_texts"], datos["rec_boxes"]):
                fragmentos.append((texto, x0, (y0 + y1) / 2, y1 - y0))
        return fragmentos

    def _fragmentos_version_2(self, ruta_imagen):
        fragmentos = []
        for pagina in self._ocr.ocr(str(ruta_imagen), cls=True) or []:
            for caja, (texto, _) in pagina or []:
                ys = [punto[1] for punto in caja]
                fragmentos.append((texto, caja[0][0], sum(ys) / 4, max(ys) - min(ys)))
        return fragmentos

    def transcribir(self, ruta_imagen):
        self._cargar_modelo()
        if self._es_version_3:
            fragmentos = self._fragmentos_version_3(ruta_imagen)
        else:
            fragmentos = self._fragmentos_version_2(ruta_imagen)
        return agrupar_en_lineas(fragmentos)
