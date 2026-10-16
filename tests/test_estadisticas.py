import pandas as pd
import pytest

from piloto.analisis.estadisticas import (
    calcular_todo, comparacion_por_factor, confusiones_frecuentes, descriptivas,
    distribucion_errores, reservadas_mas_falladas,
)


@pytest.fixture
def detalle():
    return pd.DataFrame([
        {"herramienta": "A", "lenguaje": "java", "captura": "foto", "cer": 0.2, "cer_sin_espacios": 0.1, "wer": 0.3, "segundos": 1.0},
        {"herramienta": "A", "lenguaje": "python", "captura": "foto", "cer": 0.4, "cer_sin_espacios": 0.2, "wer": 0.5, "segundos": 2.0},
        {"herramienta": "B", "lenguaje": "java", "captura": "foto", "cer": 0.1, "cer_sin_espacios": 0.1, "wer": 0.2, "segundos": 3.0},
        {"herramienta": "B", "lenguaje": "python", "captura": "foto", "cer": 0.3, "cer_sin_espacios": 0.1, "wer": 0.4, "segundos": 1.0},
    ])


@pytest.fixture
def errores():
    return pd.DataFrame([
        {"herramienta": "A", "tipo": "sustitucion", "clase": "digito", "esperado": "0", "obtenido": "O"},
        {"herramienta": "A", "tipo": "sustitucion", "clase": "digito", "esperado": "0", "obtenido": "O"},
        {"herramienta": "A", "tipo": "eliminacion", "clase": "indentacion", "esperado": " ", "obtenido": ""},
        {"herramienta": "B", "tipo": "sustitucion", "clase": "puntuacion", "esperado": ";", "obtenido": ":"},
    ])


def test_descriptivas(detalle):
    tabla = descriptivas(detalle, "cer").set_index("herramienta")
    assert tabla.loc["A", "media"] == pytest.approx(0.3)
    assert tabla.loc["A", "n"] == 2


def test_factor_con_un_solo_valor_se_omite(detalle):
    assert comparacion_por_factor(detalle, "captura") is None
    assert comparacion_por_factor(detalle, "lenguaje").loc["B", "python"] == pytest.approx(0.3)


def test_distribucion_suma_uno(errores):
    distribucion = distribucion_errores(errores)
    assert distribucion.sum(axis=1).tolist() == pytest.approx([1.0, 1.0])


def test_confusion_mas_frecuente(errores):
    fila = confusiones_frecuentes(errores).iloc[0]
    assert (fila["esperado"], fila["obtenido"], fila["veces"]) == ("0", "O", 2)


def test_calcular_todo(detalle, errores):
    tablas = calcular_todo(detalle, errores)
    assert "cer_por_lenguaje" in tablas
    assert "cer_por_captura" not in tablas
    assert "confusiones_frecuentes" in tablas


def test_reservadas_mas_falladas():
    reservadas = pd.DataFrame([
        {"herramienta": "A", "palabra": "while", "correcta": False},
        {"herramienta": "A", "palabra": "while", "correcta": True},
        {"herramienta": "A", "palabra": "return", "correcta": False},
        {"herramienta": "A", "palabra": "return", "correcta": False},
        {"herramienta": "A", "palabra": "if", "correcta": True},
    ])
    tabla = reservadas_mas_falladas(reservadas)
    assert tabla["palabra"].tolist() == ["return", "while"]
    assert tabla.iloc[1]["tasa_fallo"] == pytest.approx(0.5)
