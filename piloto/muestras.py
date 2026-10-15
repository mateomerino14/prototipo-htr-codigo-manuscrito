"""Carga de las muestras manuscritas y sus metadatos.

Convencion de nombres de las imagenes:

    <ejercicio>_<escritor>_<captura>.<ext>      ej. P03_E02_foto.jpg

- ejercicio: id del banco de ejercicios (J01..J12, P01..P12). La referencia
  se toma automaticamente de ejercicios/.
- escritor: quien escribio la hoja (E01, E02, ...), sin nombres reales.
- captura: foto o escaneo.

Si junto a la imagen hay un .txt con el mismo nombre, se usa ese texto como
referencia. Asi se cargan los examenes reales, que no estan en el banco.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path

from piloto import config

DESCONOCIDO = "desconocido"


@dataclass
class Muestra:
    id: str
    imagen: Path
    referencia: str
    ejercicio: str = DESCONOCIDO
    lenguaje: str = DESCONOCIDO
    categoria: str = DESCONOCIDO
    escritor: str = DESCONOCIDO
    captura: str = DESCONOCIDO
    extra: dict = field(default_factory=dict)

    def metadatos(self):
        return {
            "muestra": self.id,
            "ejercicio": self.ejercicio,
            "lenguaje": self.lenguaje,
            "categoria": self.categoria,
            "escritor": self.escritor,
            "captura": self.captura,
            "lineas": self.referencia.count("\n") + 1,
            **self.extra,
        }


def cargar_catalogo(carpeta_ejercicios=config.CARPETA_EJERCICIOS):
    """Devuelve {id: fila del catalogo} con el codigo de referencia incluido."""
    catalogo = {}
    with open(carpeta_ejercicios / "catalogo.csv", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            fila["codigo"] = (carpeta_ejercicios / fila["archivo"]).read_text(encoding="utf-8")
            catalogo[fila["id"]] = fila
    return catalogo


def _leer_metadatos_extra(carpeta):
    """Lee metadatos.csv (opcional) para muestras que no siguen la convencion."""
    ruta = carpeta / "metadatos.csv"
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as archivo:
        return {fila.pop("muestra"): fila for fila in csv.DictReader(archivo)}


def _desde_nombre(stem):
    partes = stem.split("_")
    if len(partes) < 3:
        return {}
    return {"ejercicio": partes[0].upper(), "escritor": partes[1].upper(), "captura": partes[2].lower()}


def cargar_muestras(carpeta, catalogo=None):
    """Recorre la carpeta y arma la lista de muestras con su referencia."""
    catalogo = catalogo if catalogo is not None else cargar_catalogo()
    extra = _leer_metadatos_extra(carpeta)
    muestras = []
    omitidas = []

    for imagen in sorted(carpeta.iterdir()):
        if imagen.suffix.lower() not in config.EXTENSIONES_IMAGEN:
            continue

        datos = {**_desde_nombre(imagen.stem), **extra.get(imagen.stem, {})}
        ejercicio = catalogo.get(datos.get("ejercicio", ""))
        ruta_txt = imagen.with_suffix(".txt")

        if ruta_txt.exists():
            referencia = ruta_txt.read_text(encoding="utf-8")
        elif ejercicio:
            referencia = ejercicio["codigo"]
        else:
            omitidas.append(imagen.name)
            continue

        if ejercicio:
            datos.setdefault("lenguaje", ejercicio["lenguaje"])
            datos.setdefault("categoria", ejercicio["categoria"])

        campos = {"ejercicio", "lenguaje", "categoria", "escritor", "captura"}
        muestras.append(Muestra(
            id=imagen.stem,
            imagen=imagen,
            referencia=referencia,
            **{k: v for k, v in datos.items() if k in campos},
            extra={k: v for k, v in datos.items() if k not in campos},
        ))

    return muestras, omitidas
