"""Prueba piloto de las herramientas HTR candidatas.

Uso:
    python -m piloto
    python -m piloto --motores tesseract trocr
"""

import argparse
import time
from pathlib import Path

from piloto import config, reporte
from piloto.metricas import cer, cer_sin_espacios, wer
from piloto.motores import MOTORES


def leer_argumentos():
    parser = argparse.ArgumentParser(description="Prueba piloto de herramientas HTR")
    parser.add_argument("--imagenes", type=Path, default=config.CARPETA_IMAGENES)
    parser.add_argument("--referencias", type=Path, default=config.CARPETA_REFERENCIAS)
    parser.add_argument("--salida", type=Path, default=config.CARPETA_RESULTADOS)
    parser.add_argument("--motores", nargs="+", choices=MOTORES.keys(), default=list(MOTORES))
    return parser.parse_args()


def cargar_muestras(carpeta_imagenes, carpeta_referencias):
    """Empareja cada imagen con el .txt de su transcripcion correcta."""
    muestras = []
    for imagen in sorted(carpeta_imagenes.iterdir()):
        if imagen.suffix.lower() not in config.EXTENSIONES_IMAGEN:
            continue

        referencia = carpeta_referencias / f"{imagen.stem}.txt"
        if not referencia.exists():
            print(f"[aviso] {imagen.name} no tiene referencia, se omite")
            continue

        muestras.append((imagen, referencia.read_text(encoding="utf-8")))
    return muestras


def evaluar_motor(motor, muestras, carpeta_transcripciones):
    """Transcribe todas las muestras con un motor y calcula sus metricas."""
    carpeta_transcripciones.mkdir(parents=True, exist_ok=True)
    filas = []
    errores = 0

    for imagen, referencia in muestras:
        inicio = time.perf_counter()
        try:
            texto = motor.transcribir(imagen)
        except Exception as error:
            # Un fallo en una imagen no debe detener el resto del piloto
            print(f"    error en {imagen.name}: {error}")
            errores += 1
            continue
        segundos = time.perf_counter() - inicio

        (carpeta_transcripciones / f"{imagen.stem}.txt").write_text(texto, encoding="utf-8")
        filas.append({
            "herramienta": motor.nombre,
            "imagen": imagen.name,
            "cer": cer(referencia, texto),
            "cer_sin_espacios": cer_sin_espacios(referencia, texto),
            "wer": wer(referencia, texto),
            "segundos": segundos,
        })

    return filas, errores


def main():
    args = leer_argumentos()
    muestras = cargar_muestras(args.imagenes, args.referencias)
    if not muestras:
        print("No hay imagenes con referencia. Revisa datos/imagenes y datos/referencias.")
        return

    args.salida.mkdir(parents=True, exist_ok=True)
    detalle = []
    resumen = []

    for clave in args.motores:
        motor = MOTORES[clave]()
        es_disponible, motivo = motor.disponible()
        if not es_disponible:
            print(f"[{motor.nombre}] no disponible: {motivo}")
            resumen.append({"herramienta": motor.nombre, "estado": f"no disponible ({motivo})"})
            continue

        print(f"[{motor.nombre}] procesando {len(muestras)} imagenes...")
        filas, errores = evaluar_motor(motor, muestras, args.salida / "transcripciones" / clave)
        detalle.extend(filas)
        resumen.append(reporte.resumir(motor.nombre, filas, errores))

    reporte.guardar_csv(args.salida / "resultados_por_imagen.csv", reporte.COLUMNAS_DETALLE, detalle)
    reporte.guardar_csv(args.salida / "tabla_piloto.csv", reporte.COLUMNAS_RESUMEN, resumen)
    reporte.imprimir_tabla(resumen)
    print(f"\nResultados guardados en {args.salida}")


if __name__ == "__main__":
    main()
