"""Interfaz comun para todas las herramientas HTR."""

from abc import ABC, abstractmethod


class MotorHTR(ABC):
    """Cada herramienta HTR se integra heredando de esta clase.

    Las librerias de cada herramienta se importan dentro de sus metodos, asi
    el piloto funciona aunque alguna no este instalada.
    """

    nombre = "base"

    def disponible(self):
        """Devuelve (True, "") si se puede usar, o (False, motivo) si no."""
        return True, ""

    @abstractmethod
    def transcribir(self, ruta_imagen):
        """Devuelve el texto reconocido en la imagen."""


def agrupar_en_lineas(fragmentos):
    """Arma el texto final a partir de fragmentos sueltos.

    Cada fragmento es (texto, x, y_centro, alto). Dos fragmentos van en la
    misma linea si sus centros estan a menos de medio alto de distancia.
    """
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
