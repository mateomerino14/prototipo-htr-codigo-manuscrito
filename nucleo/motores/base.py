from abc import ABC, abstractmethod


# Cada herramienta importa su libreria al usarse, asi no se exigen todas instaladas
class MotorHTR(ABC):
    nombre = "base"

    def disponible(self):
        return True, ""

    @abstractmethod
    def transcribir(self, ruta_imagen):
        pass


# Dos fragmentos van en la misma linea si sus centros estan a menos de medio alto
def agrupar_en_lineas(fragmentos):
    lineas = []
    for texto, x, y_centro, alto in sorted(fragmentos, key=lambda f: f[2]):
        if lineas and abs(y_centro - lineas[-1]["y_centro"]) < alto / 2:
            lineas[-1]["fragmentos"].append((x, texto))
        else:
            lineas.append({"y_centro": y_centro, "fragmentos": [(x, texto)]})

    return "\n".join(
        " ".join(texto for _, texto in sorted(linea["fragmentos"]))
        for linea in lineas
    )
