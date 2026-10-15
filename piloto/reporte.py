"""Exporta los resultados del piloto a CSV y los muestra en consola."""

import csv


def resumir(nombre, filas, fallidas):
    """Promedia las metricas de una herramienta sobre todas sus muestras."""
    cantidad = len(filas)

    def promedio(clave):
        return sum(fila[clave] for fila in filas) / cantidad if cantidad else float("nan")

    return {
        "herramienta": nombre,
        "estado": "ok" if not fallidas else f"{fallidas} muestras con error",
        "muestras": cantidad,
        "cer": promedio("cer"),
        "cer_sin_espacios": promedio("cer_sin_espacios"),
        "wer": promedio("wer"),
        "segundos": promedio("segundos"),
    }


def _columnas(filas):
    # Union de claves respetando el orden de aparicion
    columnas = {}
    for fila in filas:
        columnas.update(dict.fromkeys(fila))
    return list(columnas)


def guardar_csv(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=_columnas(filas))
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({
                clave: f"{valor:.4f}" if isinstance(valor, float) else valor
                for clave, valor in fila.items()
            })


def imprimir_tabla(resumen):
    print(f"\n{'Herramienta':<22}{'CER':>8}{'CER s/esp':>11}{'WER':>8}{'Seg/img':>9}  Estado")
    print("-" * 75)
    for fila in resumen:
        if "cer" in fila:
            print(
                f"{fila['herramienta']:<22}{fila['cer']:>8.3f}{fila['cer_sin_espacios']:>11.3f}"
                f"{fila['wer']:>8.3f}{fila['segundos']:>9.2f}  {fila['estado']}"
            )
        else:
            print(f"{fila['herramienta']:<22}{'-':>8}{'-':>11}{'-':>8}{'-':>9}  {fila['estado']}")
