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


def barras_por_factor(tabla, factor, carpeta, nombre, titulo, etiqueta_y, limite_y=None):
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
    eje.set_ylabel(etiqueta_y)
    eje.set_title(titulo, pad=24)
    _leyenda_arriba(eje, herramientas)
    if limite_y is not None:
        eje.set_ylim(0, limite_y)
    else:
        eje.margins(y=0.12)
    eje.grid(axis="x", visible=False)
    _guardar(figura, carpeta, nombre)


def cer_por_factor(tabla, factor, carpeta):
    barras_por_factor(tabla, factor, carpeta, f"cer_por_{factor}",
                      f"CER promedio por {_etiqueta(factor)}", "CER promedio")


def mapa_calor(tabla, titulo, nombre, carpeta, formato="{:.2f}", etiqueta_barra=""):
    from matplotlib.colors import LinearSegmentedColormap

    mapa = LinearSegmentedColormap.from_list("secuencial", RAMPA_SECUENCIAL)
    tabla = _ordenar_filas(tabla)
    valores = tabla.to_numpy(dtype=float)
    alto = 0.5 * len(tabla.index) + 1.6
    ancho = max(6.5, 0.75 * len(tabla.columns) + 2.5)

    # La escala parte de 0 para que el tono mas claro signifique "sin error"
    maximo = np.nanmax(valores) if np.isfinite(np.nanmax(valores)) else 1.0
    figura, eje = plt.subplots(figsize=(ancho, alto))
    imagen = eje.imshow(valores, cmap=mapa, aspect="auto", vmin=0, vmax=maximo)
    eje.set_xticks(range(len(tabla.columns)), [_etiqueta(c) for c in tabla.columns], rotation=30, ha="right")
    eje.set_yticks(range(len(tabla.index)), tabla.index)
    eje.grid(False)

    umbral = maximo * 0.55
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


def _barras_horizontales(herramienta, etiquetas, valores, titulo, etiqueta_x, carpeta, nombre):
    color, trama = _estilo(herramienta)
    figura, eje = plt.subplots(figsize=(5.5, 0.32 * len(etiquetas) + 1.2))
    barras = eje.barh(etiquetas[::-1], valores[::-1], color=color, hatch=trama,
                      edgecolor=SUPERFICIE, height=0.6)
    eje.bar_label(barras, padding=3, fontsize=8, color=TEXTO)
    eje.set_xlabel(etiqueta_x)
    eje.set_title(titulo)
    eje.grid(axis="y", visible=False)
    _guardar(figura, carpeta, nombre)


def _nombre_archivo(herramienta):
    return herramienta.lower().replace(" ", "_")


def confusiones(tabla, carpeta, limite=10):
    def visible(caracter):
        return {" ": "␣", "\n": "↵"}.get(caracter, caracter)

    for herramienta, grupo in tabla.groupby("herramienta"):
        grupo = grupo.head(limite)
        etiquetas = [f"{visible(e)}  →  {visible(o)}" for e, o in zip(grupo["esperado"], grupo["obtenido"])]
        _barras_horizontales(herramienta, etiquetas, list(grupo["veces"]),
                             f"Confusiones más frecuentes: {herramienta}", "Veces",
                             carpeta, f"confusiones_{_nombre_archivo(herramienta)}")


def reservadas_falladas(tabla, carpeta):
    for herramienta, grupo in tabla.groupby("herramienta"):
        etiquetas = [f"{p}  ({f}/{a})" for p, f, a in zip(grupo["palabra"], grupo["fallos"], grupo["apariciones"])]
        _barras_horizontales(herramienta, etiquetas, list(grupo["fallos"]),
                             f"Palabras reservadas más falladas: {herramienta}",
                             "Veces mal reconocida (fallos/apariciones en la etiqueta)",
                             carpeta, f"reservadas_falladas_{_nombre_archivo(herramienta)}")


def generar_todas(detalle, tablas, carpeta):
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

    if "reservadas_por_lenguaje" in tablas:
        barras_por_factor(tablas["reservadas_por_lenguaje"].set_index("herramienta"), "lenguaje", carpeta,
                          "reservadas_por_lenguaje", "Acierto en palabras reservadas por lenguaje",
                          "Proporción reconocida sin error", limite_y=1.1)

    if "reservadas_mas_falladas" in tablas:
        reservadas_falladas(tablas["reservadas_mas_falladas"], carpeta)
