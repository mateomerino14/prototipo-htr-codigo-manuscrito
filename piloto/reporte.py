"""Exporta los resultados del piloto a CSV y los muestra en consola."""

import csv

COLUMNAS_DETALLE = ["herramienta", "imagen", "cer", "cer_sin_espacios", "wer", "segundos"]
COLUMNAS_RESUMEN = ["herramienta", "estado", "imagenes", "cer", "cer_sin_espacios", "wer", "segundos"]


def resumir(nombre, filas, errores):
    """Promedia las metricas de una herramienta sobre todas sus imagenes."""
    cantidad = len(filas)

    def promedio(clave):
        return sum(fila[clave] for fila in filas) / cantidad if cantidad else float("nan")

    return {
        "herramienta": nombre,
        "estado": "ok" if not errores else f"{errores} imagenes con error",
        "imagenes": cantidad,
        "cer": promedio("cer"),
        "cer_sin_espacios": promedio("cer_sin_espacios"),
        "wer": promedio("wer"),
        "segundos": promedio("segundos"),
    }


def guardar_csv(ruta, columnas, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
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
