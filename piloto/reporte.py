import csv


def resumir(nombre, filas, fallidas):
    cantidad = len(filas)

    def promedio(clave):
        # Se ignoran las muestras donde la metrica no aplica
        valores = [fila[clave] for fila in filas if fila.get(clave) is not None]
        return sum(valores) / len(valores) if valores else float("nan")

    return {
        "herramienta": nombre,
        "estado": "ok" if not fallidas else f"{fallidas} muestras con error",
        "muestras": cantidad,
        "cer": promedio("cer"),
        "cer_sin_espacios": promedio("cer_sin_espacios"),
        "wer": promedio("wer"),
        "acierto_reservadas": promedio("acierto_reservadas"),
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
    print(f"\n{'Herramienta':<22}{'CER':>8}{'CER s/esp':>11}{'WER':>8}{'Reserv.':>9}{'Seg/img':>9}  Estado")
    print("-" * 84)
    for fila in resumen:
        if "cer" in fila:
            print(
                f"{fila['herramienta']:<22}{fila['cer']:>8.3f}{fila['cer_sin_espacios']:>11.3f}"
                f"{fila['wer']:>8.3f}{fila['acierto_reservadas']:>9.3f}{fila['segundos']:>9.2f}  {fila['estado']}"
            )
        else:
            print(f"{fila['herramienta']:<22}{'-':>8}{'-':>11}{'-':>8}{'-':>9}{'-':>9}  {fila['estado']}")
