"""Prueba piloto de las herramientas HTR candidatas.

Uso:
    python -m piloto                              # conjunto datos/piloto
    python -m piloto --motores tesseract trocr
    python -m piloto --conjunto evaluacion

Cada ejecucion se guarda en su propia carpeta resultados/<conjunto>/<fecha_hora>/
para no sobrescribir corridas anteriores.
"""

import argparse
import json
import platform
import time
from datetime import datetime

from piloto import config, reporte
from piloto.analisis.errores import analizar
from piloto.analisis.informe import generar_informe
from piloto.metricas import cer, cer_sin_espacios, wer
from piloto.motores import MOTORES
from piloto.muestras import cargar_muestras


def leer_argumentos():
    parser = argparse.ArgumentParser(description="Prueba piloto de herramientas HTR")
    parser.add_argument("--conjunto", default=config.CONJUNTO_POR_DEFECTO,
                        help="subcarpeta de datos/ con las imagenes")
    parser.add_argument("--motores", nargs="+", choices=MOTORES.keys(), default=list(MOTORES))
    return parser.parse_args()


def preparar_corrida(conjunto):
    carpeta = config.CARPETA_RESULTADOS / conjunto / datetime.now().strftime(config.FORMATO_CORRIDA)
    for subcarpeta in ("transcripciones", "tablas", "graficas"):
        (carpeta / subcarpeta).mkdir(parents=True, exist_ok=True)
    return carpeta


def evaluar_motor(motor, muestras, carpeta_transcripciones):
    """Transcribe todas las muestras con un motor y calcula sus metricas.

    Devuelve las metricas por muestra, el detalle de cada error de caracter y
    la cantidad de muestras que fallaron.
    """
    carpeta_transcripciones.mkdir(parents=True, exist_ok=True)
    filas = []
    detalle_errores = []
    fallidas = 0

    for muestra in muestras:
        inicio = time.perf_counter()
        try:
            texto = motor.transcribir(muestra.imagen)
        except Exception as error:
            # Un fallo en una imagen no debe detener el resto del piloto
            print(f"    error en {muestra.imagen.name}: {error}")
            fallidas += 1
            continue
        segundos = time.perf_counter() - inicio

        (carpeta_transcripciones / f"{muestra.id}.txt").write_text(texto, encoding="utf-8")
        filas.append({
            "herramienta": motor.nombre,
            **muestra.metadatos(),
            "cer": cer(muestra.referencia, texto),
            "cer_sin_espacios": cer_sin_espacios(muestra.referencia, texto),
            "wer": wer(muestra.referencia, texto),
            "segundos": segundos,
        })
        for error_caracter in analizar(muestra.referencia, texto):
            detalle_errores.append({
                "herramienta": motor.nombre,
                "muestra": muestra.id,
                "lenguaje": muestra.lenguaje,
                **error_caracter,
            })

    return filas, detalle_errores, fallidas


def guardar_registro(carpeta, args, muestras, resumen):
    """Deja constancia de como se hizo la corrida, para poder repetirla."""
    registro = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "conjunto": args.conjunto,
        "motores_solicitados": args.motores,
        "cantidad_muestras": len(muestras),
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "resumen": resumen,
    }
    (carpeta / "ejecucion.json").write_text(
        json.dumps(registro, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )


def main():
    args = leer_argumentos()
    carpeta_datos = config.CARPETA_DATOS / args.conjunto
    if not carpeta_datos.exists():
        print(f"No existe la carpeta {carpeta_datos}")
        return

    muestras, omitidas = cargar_muestras(carpeta_datos)
    for nombre in omitidas:
        print(f"[aviso] {nombre} no tiene referencia, se omite")
    if not muestras:
        print(f"No hay muestras validas en {carpeta_datos}")
        return

    corrida = preparar_corrida(args.conjunto)
    detalle = []
    errores = []
    resumen = []

    for clave in args.motores:
        motor = MOTORES[clave]()
        es_disponible, motivo = motor.disponible()
        if not es_disponible:
            print(f"[{motor.nombre}] no disponible: {motivo}")
            resumen.append({"herramienta": motor.nombre, "estado": f"no disponible ({motivo})"})
            continue

        print(f"[{motor.nombre}] procesando {len(muestras)} muestras...")
        filas, errores_motor, fallidas = evaluar_motor(motor, muestras, corrida / "transcripciones" / clave)
        detalle.extend(filas)
        errores.extend(errores_motor)
        resumen.append(reporte.resumir(motor.nombre, filas, fallidas))

    reporte.guardar_csv(corrida / "tablas" / "resultados_por_muestra.csv", detalle)
    reporte.guardar_csv(corrida / "tablas" / "resumen_herramientas.csv", resumen)
    reporte.guardar_csv(corrida / "tablas" / "errores.csv", errores)
    guardar_registro(corrida, args, muestras, resumen)
    reporte.imprimir_tabla(resumen)
    generar_informe(corrida)
    print(f"\nResultados guardados en {corrida}")


if __name__ == "__main__":
    main()
