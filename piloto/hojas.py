"""Genera el PDF con los ejercicios que copian a mano los escritores del piloto.

Uso:
    python -m piloto.hojas

La primera pagina tiene las instrucciones y una hoja de control para marcar
las capturas hechas; despues van los ejercicios, dos por pagina.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from piloto import config  # noqa: E402
from piloto.analisis.graficas import ETIQUETAS  # noqa: E402
from piloto.muestras import cargar_catalogo  # noqa: E402

TAMANO_A4 = (8.27, 11.69)
EJERCICIOS_POR_PAGINA = 2
FUENTE_CODIGO = "DejaVu Sans Mono"
TEXTO = "#0b0b0b"
TEXTO_SECUNDARIO = "#52514e"
LINEA = "#c3c2b7"

INSTRUCCIONES = [
    "1. Copie cada ejercicio a mano, en hoja blanca o cuadriculada, con bolígrafo azul o negro.",
    "2. Escriba como lo haría en un examen. Respete la indentación del original.",
    "3. Si se equivoca, tache y siga. No corrija encima ni use corrector.",
    "4. Un ejercicio por hoja o por recuadro, con su código (por ejemplo J01) en una esquina.",
    "5. Capture cada hoja con foto y con escaneo, y nombre el archivo así:",
    "      <ejercicio>_<escritor>_<captura>.jpg      ej. J01_E03_foto.jpg",
]


def _etiqueta(texto):
    return ETIQUETAS.get(texto, texto)


def _pagina_control(pdf, catalogo):
    figura = plt.figure(figsize=TAMANO_A4)
    figura.text(0.08, 0.94, "Prueba piloto: ejercicios para copiar a mano", fontsize=15,
                weight="bold", color=TEXTO)
    figura.text(0.08, 0.915, "Escritor: ________      Fecha: ____________", fontsize=10, color=TEXTO_SECUNDARIO)

    for i, linea in enumerate(INSTRUCCIONES):
        figura.text(0.08, 0.87 - i * 0.022, linea, fontsize=9.5, color=TEXTO,
                    family=FUENTE_CODIGO if linea.startswith("   ") else None)

    figura.text(0.08, 0.715, "Hoja de control", fontsize=11, weight="bold", color=TEXTO)
    filas = [[e["id"], e["lenguaje"], _etiqueta(e["categoria"]), "☐", "☐"] for e in catalogo.values()]
    eje = figura.add_axes([0.08, 0.05, 0.84, 0.65])
    eje.axis("off")
    tabla = eje.table(cellText=filas, colLabels=["Ejercicio", "Lenguaje", "Categoría", "Foto", "Escaneo"],
                      loc="upper center", cellLoc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    tabla.scale(1, 1.25)
    for celda in tabla.get_celld().values():
        celda.set_edgecolor(LINEA)

    pdf.savefig(figura)
    plt.close(figura)


def _dibujar_ejercicio(figura, ejercicio, arriba):
    figura.text(0.08, arriba, f"{ejercicio['id']}", fontsize=16, weight="bold", color=TEXTO)
    figura.text(0.17, arriba + 0.002, f"{ejercicio['lenguaje'].capitalize()} · {_etiqueta(ejercicio['categoria'])}",
                fontsize=10, color=TEXTO_SECUNDARIO)
    figura.text(0.08, arriba - 0.025, ejercicio["descripcion"], fontsize=9.5, color=TEXTO_SECUNDARIO)

    lineas = ejercicio["codigo"].rstrip("\n").split("\n")
    for i, linea in enumerate(lineas):
        figura.text(0.10, arriba - 0.065 - i * 0.022, linea, fontsize=11, family=FUENTE_CODIGO, color=TEXTO)


def generar(destino):
    catalogo = cargar_catalogo()
    ejercicios = list(catalogo.values())
    destino.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(destino) as pdf:
        _pagina_control(pdf, catalogo)
        for inicio in range(0, len(ejercicios), EJERCICIOS_POR_PAGINA):
            figura = plt.figure(figsize=TAMANO_A4)
            for posicion, ejercicio in enumerate(ejercicios[inicio:inicio + EJERCICIOS_POR_PAGINA]):
                _dibujar_ejercicio(figura, ejercicio, 0.93 - posicion * 0.47)
            # Separa visualmente los dos ejercicios de la pagina
            figura.add_artist(plt.Line2D([0.08, 0.92], [0.5, 0.5], color=LINEA, linewidth=0.8))
            pdf.savefig(figura)
            plt.close(figura)

    return destino


def main():
    destino = generar(config.CARPETA_RESULTADOS / "hojas" / "ejercicios_para_copiar.pdf")
    print(f"Hojas generadas en {destino}")


if __name__ == "__main__":
    main()
