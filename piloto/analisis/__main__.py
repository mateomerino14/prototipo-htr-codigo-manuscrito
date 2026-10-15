"""Regenera el informe de una corrida ya hecha.

Uso:
    python -m piloto.analisis                       # la corrida mas reciente
    python -m piloto.analisis resultados/piloto/20261020_101500
"""

import sys
from pathlib import Path

from piloto import config
from piloto.analisis.informe import generar_informe


def corrida_mas_reciente():
    corridas = sorted((config.CARPETA_RESULTADOS / config.CONJUNTO_POR_DEFECTO).glob("*/tablas"))
    return corridas[-1].parent if corridas else None


def main():
    corrida = Path(sys.argv[1]) if len(sys.argv) > 1 else corrida_mas_reciente()
    if corrida is None or not corrida.exists():
        print("No se encontro la corrida a analizar.")
        return
    generar_informe(corrida)


if __name__ == "__main__":
    main()
