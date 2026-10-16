# Uso: python -m piloto [--conjunto evaluacion] [--motores tesseract trocr]

import argparse
import json
import platform
import time
from dataclasses import dataclass, field
from datetime import datetime

from piloto import config, reporte
from nucleo.errores import analizar
from nucleo.lenguajes import acierto_reservadas, detalle_reservadas
from nucleo.metricas import cer, cer_sin_espacios, wer
from nucleo.motores import MOTORES
from piloto.analisis.informe import generar_informe
from piloto.muestras import cargar_muestras


@dataclass
class ResultadoMotor:
    filas: list = field(default_factory=list)
    errores: list = field(default_factory=list)
    reservadas: list = field(default_factory=list)
    fallidas: int = 0


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
    carpeta_transcripciones.mkdir(parents=True, exist_ok=True)
    resultado = ResultadoMotor()

    for muestra in muestras:
        inicio = time.perf_counter()
        try:
            texto = motor.transcribir(muestra.imagen)
        except Exception as error:
            # Un fallo en una imagen no debe detener el resto del piloto
            print(f"    error en {muestra.imagen.name}: {error}")
            resultado.fallidas += 1
            continue
        segundos = time.perf_counter() - inicio

        (carpeta_transcripciones / f"{muestra.id}.txt").write_text(texto, encoding="utf-8")
        resultado.filas.append({
            "herramienta": motor.nombre,
            **muestra.metadatos(),
            "cer": cer(muestra.referencia, texto),
            "cer_sin_espacios": cer_sin_espacios(muestra.referencia, texto),
            "wer": wer(muestra.referencia, texto),
            "acierto_reservadas": acierto_reservadas(muestra.referencia, texto, muestra.lenguaje),
            "segundos": segundos,
        })

        identificacion = {"herramienta": motor.nombre, "muestra": muestra.id, "lenguaje": muestra.lenguaje}
        for error_caracter in analizar(muestra.referencia, texto):
            resultado.errores.append({**identificacion, **error_caracter})
        for palabra in detalle_reservadas(muestra.referencia, texto, muestra.lenguaje):
            resultado.reservadas.append({**identificacion, **palabra})

    return resultado


def guardar_registro(carpeta, args, muestras, resumen):
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
    total = ResultadoMotor()
    resumen = []

    for clave in args.motores:
        motor = MOTORES[clave]()
        es_disponible, motivo = motor.disponible()
        if not es_disponible:
            print(f"[{motor.nombre}] no disponible: {motivo}")
            resumen.append({"herramienta": motor.nombre, "estado": f"no disponible ({motivo})"})
            continue

        print(f"[{motor.nombre}] procesando {len(muestras)} muestras...")
        resultado = evaluar_motor(motor, muestras, corrida / "transcripciones" / clave)
        total.filas.extend(resultado.filas)
        total.errores.extend(resultado.errores)
        total.reservadas.extend(resultado.reservadas)
        resumen.append(reporte.resumir(motor.nombre, resultado.filas, resultado.fallidas))

    carpeta_tablas = corrida / "tablas"
    reporte.guardar_csv(carpeta_tablas / "resultados_por_muestra.csv", total.filas)
    reporte.guardar_csv(carpeta_tablas / "resumen_herramientas.csv", resumen)
    reporte.guardar_csv(carpeta_tablas / "errores.csv", total.errores)
    reporte.guardar_csv(carpeta_tablas / "reservadas.csv", total.reservadas)
    guardar_registro(corrida, args, muestras, resumen)
    reporte.imprimir_tabla(resumen)
    generar_informe(corrida)
    print(f"\nResultados guardados en {corrida}")


if __name__ == "__main__":
    main()
