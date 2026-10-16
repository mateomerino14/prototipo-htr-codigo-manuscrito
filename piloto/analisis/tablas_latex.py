ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}

ENCABEZADOS = {
    "herramienta": "Herramienta", "n": "n", "media": "Media", "mediana": "Mediana",
    "desv_est": "Desv. est.", "minimo": "Mín.", "maximo": "Máx.", "ic95": "IC 95 %",
    "esperado": "Esperado", "obtenido": "Obtenido", "veces": "Veces",
    "sustitucion": "Sustitución", "eliminacion": "Eliminación", "insercion": "Inserción",
    "palabra": "Palabra", "apariciones": "Apariciones", "fallos": "Fallos", "tasa_fallo": "Tasa de fallo",
}

TABLAS = {
    "descriptivas_cer": "Estadísticas descriptivas del CER por herramienta",
    "descriptivas_cer_sin_espacios": "Estadísticas descriptivas del CER sin espacios por herramienta",
    "descriptivas_wer": "Estadísticas descriptivas del WER por herramienta",
    "descriptivas_acierto_reservadas": "Estadísticas descriptivas del acierto en palabras reservadas por herramienta",
    "reservadas_por_lenguaje": "Acierto promedio en palabras reservadas por herramienta y lenguaje",
    "reservadas_mas_falladas": "Palabras reservadas reconocidas con error con mayor frecuencia",
    "tiempo_por_muestra": "Tiempo de transcripción por muestra (segundos)",
    "cer_por_lenguaje": "CER promedio por herramienta y lenguaje",
    "cer_por_captura": "CER promedio por herramienta y tipo de captura",
    "cer_por_categoria": "CER promedio por herramienta y categoría de ejercicio",
    "tipos_de_error": "Cantidad de errores por tipo de operación",
    "confusiones_frecuentes": "Sustituciones de caracteres más frecuentes por herramienta",
}


def escapar(texto):
    texto = str(texto)
    # Se marcan espacios y saltos para que se vean en la tabla
    if texto == " ":
        return r"\textvisiblespace"
    if texto == "\n":
        return r"$\hookleftarrow$"
    return "".join(ESCAPES.get(caracter, caracter) for caracter in texto)


def _celda(valor):
    if isinstance(valor, float):
        return f"{valor:.3f}"
    return escapar(valor)


# El numero queda como X porque depende del orden final del documento
def tabla_a_latex(tabla, titulo, nota="Elaboración propia."):
    columnas = list(tabla.columns)
    formato = "|" + "|".join("l" if i == 0 else "c" for i in range(len(columnas))) + "|"
    encabezado = " & ".join(rf"\textbf{{{escapar(ENCABEZADOS.get(c, c))}}}" for c in columnas)

    lineas = [
        r"\begin{flushleft}",
        r"\textbf{Tabla X}\\",
        rf"\textit{{{titulo}}}",
        r"\end{flushleft}",
        "",
        r"\begin{center}",
        r"\small",
        r"\renewcommand{\arraystretch}{1.3}",
        rf"\begin{{tabular}}{{{formato}}}",
        r"\hline",
        encabezado + r" \\",
        r"\hline",
    ]
    for fila in tabla.itertuples(index=False):
        lineas.append(" & ".join(_celda(valor) for valor in fila) + r" \\")
        lineas.append(r"\hline")
    lineas += [
        r"\end{tabular}",
        r"\end{center}",
        "",
        r"\begin{flushleft}",
        rf"\footnotesize \textit{{Nota.}} {nota}",
        r"\end{flushleft}",
    ]
    return "\n".join(lineas) + "\n"


def _unir_intervalo(tabla):
    if not {"ic95_inf", "ic95_sup"} <= set(tabla.columns):
        return tabla
    tabla = tabla.copy()
    posicion = list(tabla.columns).index("media") + 1
    intervalo = [f"[{i:.3f}; {s:.3f}]" for i, s in zip(tabla["ic95_inf"], tabla["ic95_sup"])]
    tabla = tabla.drop(columns=["ic95_inf", "ic95_sup"])
    tabla.insert(posicion, "ic95", intervalo)
    return tabla


def exportar_todas(tablas, carpeta):
    for nombre, titulo in TABLAS.items():
        if nombre not in tablas:
            continue
        tabla = _unir_intervalo(tablas[nombre])
        if nombre in ("confusiones_frecuentes", "reservadas_mas_falladas"):
            tabla = tabla.groupby("herramienta").head(5)
        (carpeta / f"{nombre}.tex").write_text(tabla_a_latex(tabla, titulo), encoding="utf-8")
