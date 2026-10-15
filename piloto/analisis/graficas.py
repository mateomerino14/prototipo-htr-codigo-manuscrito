"""Graficas del analisis, pensadas para el documento impreso.

Cada grafica se guarda en PNG (300 dpi) y en PDF (vectorial, para LaTeX).
Cada herramienta tiene siempre el mismo color y la misma trama, asi se
reconoce igual en todas las figuras y tambien en impresion en blanco y negro.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SUPERFICIE = "#ffffff"
TEXTO = "#0b0b0b"
TEXTO_SECUNDARIO = "#52514e"
GRILLA = "#e4e3df"

# Orden fijo: el color sigue a la herramienta, no a su posicion en la grafica
ESTILO_HERRAMIENTA = {
    "Tesseract": ("#2a78d6", ""),
    "PaddleOCR": ("#eb6834", "//"),
    "TrOCR": ("#1baf7a", "\\\\"),
    "Google Cloud Vision": ("#eda100", "xx"),
    "Azure AI Vision": ("#e87ba4", ".."),
}
COLOR_SECUNDARIO = "#eb6834"
COLOR_SIN_ESTILO = ("#8a8984", "")

ETIQUETAS = {
    "digito": "dígito", "indentacion": "indentación", "puntuacion": "puntuación",
    "salto_linea": "salto de línea", "categoria": "categoría",
    "busqueda": "búsqueda", "recursion": "recursión",
}

RAMPA_SECUENCIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "axes.edgecolor": GRILLA,
    "axes.labelcolor": TEXTO_SECUNDARIO,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlecolor": TEXTO,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRILLA,
    "grid.linewidth": 0.6,
    "xtick.color": TEXTO_SECUNDARIO,
    "ytick.color": TEXTO_SECUNDARIO,
    "font.size": 9,
    "font.family": "DejaVu Sans",
    "legend.frameon": False,
    "hatch.linewidth": 0.6,
})


def _etiqueta(texto):
    return ETIQUETAS.get(texto, texto)


def _leyenda_arriba(eje, nombres):
    # Fuera del area de datos para que nunca tape barras ni valores
    eje.legend(nombres, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=len(nombres), fontsize=8)


def _ordenar_filas(tabla):
    orden = [h for h in ESTILO_HERRAMIENTA if h in tabla.index]
    return tabla.loc[orden + [h for h in tabla.index if h not in orden]]


def _estilo(herramienta):
    return ESTILO_HERRAMIENTA.get(herramienta, COLOR_SIN_ESTILO)


def _guardar(figura, carpeta, nombre):
    figura.tight_layout()
    for extension in ("png", "pdf"):
        figura.savefig(carpeta / f"{nombre}.{extension}", dpi=300)
    plt.close(figura)


def _herramientas(detalle):
    presentes = list(detalle["herramienta"].unique())
    orden = [h for h in ESTILO_HERRAMIENTA if h in presentes]
    return orden + [h for h in presentes if h not in orden]


def distribucion_cer(detalle, carpeta):
    """Diagrama de caja del CER: muestra la dispersion, no solo el promedio."""
    herramientas = _herramientas(detalle)
    datos = [detalle.loc[detalle["herramienta"] == h, "cer"] for h in herramientas]

    figura, eje = plt.subplots(figsize=(6.5, 3.6))
    cajas = eje.boxplot(datos, patch_artist=True, widths=0.5, showmeans=True,
                        medianprops={"color": TEXTO, "linewidth": 1.2},
                        meanprops={"marker": "D", "markerfacecolor": SUPERFICIE,
                                   "markeredgecolor": TEXTO, "markersize": 5},
                        flierprops={"marker": "o", "markersize": 4, "markerfacecolor": TEXTO_SECUNDARIO})
    for caja, herramienta in zip(cajas["boxes"], herramientas):
        color, trama = _estilo(herramienta)
        caja.set(facecolor=color, edgecolor=SUPERFICIE, hatch=trama, alpha=0.9)

    eje.set_xticks(range(1, len(herramientas) + 1), herramientas)
    eje.set_ylabel("CER (0 = transcripción perfecta)")
    eje.set_title("Distribución del CER por herramienta")
    eje.grid(axis="x", visible=False)
    eje.text(0.99, 0.98, "◇ media   — mediana", transform=eje.transAxes, ha="right", va="top",
             color=TEXTO_SECUNDARIO, fontsize=8)
    _guardar(figura, carpeta, "distribucion_cer")


def _barras_con_etiqueta(eje, posiciones, valores, ancho, color, trama, formato="{:.3f}"):
    barras = eje.bar(posiciones, valores, ancho, color=color, hatch=trama, edgecolor=SUPERFICIE, linewidth=1.5)
    for barra, valor in zip(barras, valores):
        if not np.isnan(valor):
            eje.annotate(formato.format(valor), (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                         xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, color=TEXTO)


def impacto_indentacion(detalle, carpeta):
    """CER con y sin espacios: la diferencia es lo que se pierde por indentacion."""
    medias = detalle.groupby("herramienta")[["cer", "cer_sin_espacios"]].mean()
    herramientas = [h for h in _herramientas(detalle) if h in medias.index]
    medias = medias.loc[herramientas]
    x = np.arange(len(herramientas))

    figura, eje = plt.subplots(figsize=(6.5, 3.6))
    _barras_con_etiqueta(eje, x - 0.19, medias["cer"], 0.36, "#2a78d6", "")
    _barras_con_etiqueta(eje, x + 0.19, medias["cer_sin_espacios"], 0.36, COLOR_SECUNDARIO, "//")
    eje.set_xticks(x, herramientas)
    eje.set_ylabel("CER promedio")
    eje.set_title("Efecto de espacios e indentación en el CER", pad=24)
    _leyenda_arriba(eje, ["CER completo", "CER sin espacios"])
    eje.margins(y=0.12)
    eje.grid(axis="x", visible=False)
    _guardar(figura, carpeta, "impacto_indentacion")


def cer_por_factor(tabla, factor, carpeta):
    """Barras agrupadas: una serie por herramienta, un grupo por valor del factor."""
    herramientas = [h for h in ESTILO_HERRAMIENTA if h in tabla.index] + \
                   [h for h in tabla.index if h not in ESTILO_HERRAMIENTA]
    valores = list(tabla.columns)
    x = np.arange(len(valores))
    ancho = 0.8 / len(herramientas)

    figura, eje = plt.subplots(figsize=(6.5, 3.6))
    for i, herramienta in enumerate(herramientas):
        color, trama = _estilo(herramienta)
        desplazamiento = (i - (len(herramientas) - 1) / 2) * ancho
        _barras_con_etiqueta(eje, x + desplazamiento, tabla.loc[herramienta, valores], ancho * 0.92, color, trama)

    eje.set_xticks(x, [_etiqueta(v) for v in valores])
    eje.set_ylabel("CER promedio")
    eje.set_title(f"CER promedio por {_etiqueta(factor)}", pad=24)
    _leyenda_arriba(eje, herramientas)
    eje.margins(y=0.12)
    eje.grid(axis="x", visible=False)
    _guardar(figura, carpeta, f"cer_por_{factor}")


def mapa_calor(tabla, titulo, nombre, carpeta, formato="{:.2f}", etiqueta_barra=""):
    """Mapa de calor de una sola tonalidad: mas oscuro es mayor valor."""
    from matplotlib.colors import LinearSegmentedColormap

    mapa = LinearSegmentedColormap.from_list("secuencial", RAMPA_SECUENCIAL)
    tabla = _ordenar_filas(tabla)
    valores = tabla.to_numpy(dtype=float)
    alto = 0.5 * len(tabla.index) + 1.6
    ancho = max(6.5, 0.75 * len(tabla.columns) + 2.5)

    figura, eje = plt.subplots(figsize=(ancho, alto))
    imagen = eje.imshow(valores, cmap=mapa, aspect="auto")
    eje.set_xticks(range(len(tabla.columns)), [_etiqueta(c) for c in tabla.columns], rotation=30, ha="right")
    eje.set_yticks(range(len(tabla.index)), tabla.index)
    eje.grid(False)

    umbral = np.nanmax(valores) * 0.55 if np.isfinite(np.nanmax(valores)) else 0
    for (fila, columna), valor in np.ndenumerate(valores):
        if not np.isnan(valor):
            color = SUPERFICIE if valor > umbral else TEXTO
            eje.text(columna, fila, formato.format(valor), ha="center", va="center", fontsize=8, color=color)

    barra = figura.colorbar(imagen, ax=eje, fraction=0.04)
    barra.set_label(etiqueta_barra)
    barra.outline.set_visible(False)
    eje.set_title(titulo)
    _guardar(figura, carpeta, nombre)


def tiempo_por_herramienta(detalle, carpeta):
    medias = detalle.groupby("herramienta")["segundos"].mean()
    herramientas = [h for h in _herramientas(detalle) if h in medias.index]

    figura, eje = plt.subplots(figsize=(6.5, 3.2))
    for i, herramienta in enumerate(herramientas):
        color, trama = _estilo(herramienta)
        _barras_con_etiqueta(eje, [i], [medias[herramienta]], 0.55, color, trama, "{:.2f} s")
    eje.set_xticks(range(len(herramientas)), herramientas)
    eje.set_ylabel("Segundos por muestra")
    eje.set_title("Tiempo promedio de transcripción")
    eje.grid(axis="x", visible=False)
    _guardar(figura, carpeta, "tiempo_por_herramienta")


def confusiones(tabla, carpeta, limite=10):
    """Una figura por herramienta con sus sustituciones mas frecuentes."""
    def visible(caracter):
        return {" ": "␣", "\n": "↵"}.get(caracter, caracter)

    for herramienta, grupo in tabla.groupby("herramienta"):
        grupo = grupo.head(limite).iloc[::-1]
        etiquetas = [f"{visible(e)}  →  {visible(o)}" for e, o in zip(grupo["esperado"], grupo["obtenido"])]
        color, trama = _estilo(herramienta)

        figura, eje = plt.subplots(figsize=(5.5, 0.32 * len(grupo) + 1.2))
        barras = eje.barh(etiquetas, grupo["veces"], color=color, hatch=trama, edgecolor=SUPERFICIE, height=0.6)
        eje.bar_label(barras, padding=3, fontsize=8, color=TEXTO)
        eje.set_xlabel("Veces")
        eje.set_title(f"Confusiones más frecuentes: {herramienta}")
        eje.grid(axis="y", visible=False)
        nombre = herramienta.lower().replace(" ", "_")
        _guardar(figura, carpeta, f"confusiones_{nombre}")


def generar_todas(detalle, tablas, carpeta):
    """Genera todas las graficas que los datos permitan."""
    if detalle.empty:
        return

    distribucion_cer(detalle, carpeta)
    impacto_indentacion(detalle, carpeta)
    tiempo_por_herramienta(detalle, carpeta)

    for factor in ("lenguaje", "captura"):
        clave = f"cer_por_{factor}"
        if clave in tablas:
            cer_por_factor(tablas[clave].set_index("herramienta"), factor, carpeta)

    if "cer_por_categoria" in tablas:
        mapa_calor(tablas["cer_por_categoria"].set_index("herramienta"),
                   "CER promedio por categoría de ejercicio", "cer_por_categoria", carpeta,
                   etiqueta_barra="CER")

    if "distribucion_errores" in tablas:
        mapa_calor(tablas["distribucion_errores"].set_index("herramienta") * 100,
                   "Distribución de errores por clase de carácter (%)", "distribucion_errores", carpeta,
                   formato="{:.0f}", etiqueta_barra="% de los errores")

    if "confusiones_frecuentes" in tablas:
        confusiones(tablas["confusiones_frecuentes"], carpeta)
