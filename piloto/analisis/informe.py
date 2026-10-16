import pandas as pd

from piloto.analisis import graficas, tablas_latex
from piloto.analisis.estadisticas import calcular_todo


def _leer_csv(ruta):
    if not ruta.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(ruta, keep_default_na=False, na_values=[""])
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


# Solo lee los CSV de la corrida, asi el analisis se repite sin volver a transcribir
def generar_informe(corrida):
    carpeta_tablas = corrida / "tablas"
    detalle = _leer_csv(carpeta_tablas / "resultados_por_muestra.csv")
    errores = _leer_csv(carpeta_tablas / "errores.csv")
    reservadas = _leer_csv(carpeta_tablas / "reservadas.csv")

    if detalle.empty:
        print("La corrida no tiene resultados para analizar.")
        return

    # Un espacio esperado u obtenido no debe leerse como celda vacia
    for columna in ("esperado", "obtenido"):
        if columna in errores:
            errores[columna] = errores[columna].fillna("").astype(str)

    if "correcta" in reservadas:
        reservadas["correcta"] = reservadas["correcta"].astype(str).str.lower() == "true"

    tablas = calcular_todo(detalle, errores, reservadas)

    carpeta_estadisticas = carpeta_tablas / "estadisticas"
    carpeta_latex = carpeta_tablas / "latex"
    carpeta_graficas = corrida / "graficas"
    for carpeta in (carpeta_estadisticas, carpeta_latex, carpeta_graficas):
        carpeta.mkdir(parents=True, exist_ok=True)

    for nombre, tabla in tablas.items():
        tabla.to_csv(carpeta_estadisticas / f"{nombre}.csv", index=False, float_format="%.4f")

    tablas_latex.exportar_todas(tablas, carpeta_latex)
    graficas.generar_todas(detalle, tablas, carpeta_graficas)
    print(f"Informe generado: {len(tablas)} tablas y graficas en {corrida}")
