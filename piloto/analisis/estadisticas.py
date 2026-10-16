"""Estadisticas descriptivas de los resultados.

El alcance de la investigacion es descriptivo, por eso aqui solo se resumen
los datos (media, mediana, dispersion); no se hacen pruebas de hipotesis.
El intervalo de confianza de la media indica que tan precisa es esa media
con la cantidad de muestras disponible.
"""

import numpy as np

REMUESTREOS_BOOTSTRAP = 2000
SEMILLA = 2026

METRICAS = ["cer", "cer_sin_espacios", "wer", "acierto_reservadas"]
AGRUPACIONES = ["lenguaje", "categoria", "captura", "escritor"]


def intervalo_bootstrap(valores, nivel=0.95):
    """Intervalo de confianza de la media por bootstrap de percentiles.

    No supone que los datos sigan una distribucion normal, lo que conviene
    porque el CER suele estar cargado hacia valores bajos. La semilla es fija
    para que el resultado sea reproducible.
    """
    valores = np.asarray(valores, dtype=float)
    valores = valores[~np.isnan(valores)]
    if len(valores) < 2:
        return float("nan"), float("nan")

    generador = np.random.default_rng(SEMILLA)
    indices = generador.integers(0, len(valores), size=(REMUESTREOS_BOOTSTRAP, len(valores)))
    medias = valores[indices].mean(axis=1)
    alfa = (1 - nivel) / 2
    return float(np.quantile(medias, alfa)), float(np.quantile(medias, 1 - alfa))


def descriptivas(detalle, metrica, por=("herramienta",)):
    """Media con su IC 95 %, mediana, desviacion estandar, minimo, maximo y n."""
    grupos = detalle.groupby(list(por))[metrica]
    tabla = grupos.agg(
        n="count",
        media="mean",
        mediana="median",
        desv_est="std",
        minimo="min",
        maximo="max",
    )
    intervalos = grupos.apply(intervalo_bootstrap)
    tabla["ic95_inf"] = [inferior for inferior, _ in intervalos]
    tabla["ic95_sup"] = [superior for _, superior in intervalos]
    return tabla.reset_index().sort_values(list(por))


def comparacion_por_factor(detalle, factor, metrica="cer"):
    """Media de la metrica por herramienta (filas) y factor (columnas)."""
    if factor not in detalle or detalle[factor].nunique() < 2:
        return None
    return detalle.pivot_table(index="herramienta", columns=factor, values=metrica, aggfunc="mean")


def distribucion_errores(errores):
    """Proporcion de cada clase de error dentro del total de cada herramienta."""
    conteo = errores.groupby(["herramienta", "clase"]).size().unstack(fill_value=0)
    return conteo.div(conteo.sum(axis=1), axis=0)


def confusiones_frecuentes(errores, limite=15):
    """Sustituciones mas repetidas (esperado -> obtenido) de cada herramienta."""
    sustituciones = errores[errores["tipo"] == "sustitucion"]
    conteo = (
        sustituciones.groupby(["herramienta", "esperado", "obtenido"])
        .size()
        .rename("veces")
        .reset_index()
        .sort_values(["herramienta", "veces"], ascending=[True, False])
    )
    return conteo.groupby("herramienta").head(limite)


def reservadas_mas_falladas(reservadas, limite=10):
    """Palabras reservadas que cada herramienta reconoce mal con mas frecuencia.

    Es la base para decidir que palabras debe priorizar el corrector.
    """
    reservadas = reservadas.assign(fallo=~reservadas["correcta"])
    tabla = (
        reservadas.groupby(["herramienta", "palabra"])
        .agg(apariciones=("fallo", "size"), fallos=("fallo", "sum"))
        .reset_index()
    )
    tabla["tasa_fallo"] = tabla["fallos"] / tabla["apariciones"]
    tabla = tabla[tabla["fallos"] > 0].sort_values(
        ["herramienta", "fallos", "tasa_fallo"], ascending=[True, False, False]
    )
    return tabla.groupby("herramienta").head(limite)


def tipos_de_error(errores):
    """Cantidad de sustituciones, eliminaciones e inserciones por herramienta."""
    return errores.groupby(["herramienta", "tipo"]).size().unstack(fill_value=0)


def calcular_todo(detalle, errores, reservadas=None):
    """Arma todas las tablas del analisis en un diccionario {nombre: tabla}."""
    # Las corridas antiguas pueden no tener todas las metricas
    tablas = {
        f"descriptivas_{metrica}": descriptivas(detalle, metrica)
        for metrica in METRICAS
        if metrica in detalle
    }
    tablas["tiempo_por_muestra"] = descriptivas(detalle, "segundos")

    for factor in AGRUPACIONES:
        tabla = comparacion_por_factor(detalle, factor)
        if tabla is not None:
            tablas[f"cer_por_{factor}"] = tabla.reset_index()

    if "acierto_reservadas" in detalle:
        tabla = comparacion_por_factor(detalle, "lenguaje", "acierto_reservadas")
        if tabla is not None:
            tablas["reservadas_por_lenguaje"] = tabla.reset_index()

    if reservadas is not None and not reservadas.empty:
        tablas["reservadas_mas_falladas"] = reservadas_mas_falladas(reservadas)

    if not errores.empty:
        tablas["distribucion_errores"] = distribucion_errores(errores).reset_index()
        tablas["tipos_de_error"] = tipos_de_error(errores).reset_index()
        tablas["confusiones_frecuentes"] = confusiones_frecuentes(errores)

    return tablas
