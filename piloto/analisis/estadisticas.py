"""Estadisticas descriptivas de los resultados.

El alcance de la investigacion es descriptivo, por eso aqui solo se resumen
los datos (media, mediana, dispersion); no se hacen pruebas de hipotesis.
"""

METRICAS = ["cer", "cer_sin_espacios", "wer"]
AGRUPACIONES = ["lenguaje", "categoria", "captura", "escritor"]


def descriptivas(detalle, metrica, por=("herramienta",)):
    """Media, mediana, desviacion estandar, minimo, maximo y n por grupo."""
    grupos = detalle.groupby(list(por))[metrica]
    tabla = grupos.agg(
        n="count",
        media="mean",
        mediana="median",
        desv_est="std",
        minimo="min",
        maximo="max",
    )
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


def tipos_de_error(errores):
    """Cantidad de sustituciones, eliminaciones e inserciones por herramienta."""
    return errores.groupby(["herramienta", "tipo"]).size().unstack(fill_value=0)


def calcular_todo(detalle, errores):
    """Arma todas las tablas del analisis en un diccionario {nombre: tabla}."""
    tablas = {
        f"descriptivas_{metrica}": descriptivas(detalle, metrica) for metrica in METRICAS
    }
    tablas["tiempo_por_muestra"] = descriptivas(detalle, "segundos")

    for factor in AGRUPACIONES:
        tabla = comparacion_por_factor(detalle, factor)
        if tabla is not None:
            tablas[f"cer_por_{factor}"] = tabla.reset_index()

    if not errores.empty:
        tablas["distribucion_errores"] = distribucion_errores(errores).reset_index()
        tablas["tipos_de_error"] = tipos_de_error(errores).reset_index()
        tablas["confusiones_frecuentes"] = confusiones_frecuentes(errores)

    return tablas
