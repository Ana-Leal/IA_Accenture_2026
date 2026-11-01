# Permite ejecutar pruebas y comparar resultados decimales.
import pytest
from src.metricas_texto import calcular_metricas, resumir_metricas

# Comprueba que las diferencias de formato desaparezcan al limpiar.
def test_textos_iguales_tras_limpiar():
    # Ambos textos quedan como "reparar la llave".
    resultado = calcular_metricas(
        "¡Reparar la LLAVE!",
        "reparar la llave",
    )

    # Como todas las palabras coinciden, las tres métricas valen 1.
    assert resultado == {
        "precision": 1.0,
        "cobertura": 1.0,
        "f1": 1.0,
    }


# Comprueba una respuesta que contiene solo parte de la referencia.
def test_respuesta_incompleta():
    # La referencia tiene tres palabras; la respuesta incluye una.
    resultado = calcular_metricas("reparar la llave", "reparar")

    # Precisión: 1 coincidencia / 1 palabra respondida.
    # Cobertura: 1 coincidencia / 3 palabras de referencia.
    # F1: combina ambas métricas y da 0.5.
    # approx permite pequeñas diferencias de precisión decimal.
    assert resultado == pytest.approx({
        "precision": 1.0,
        "cobertura": 1 / 3,
        "f1": 0.5,
    })


# Comprueba que las palabras repetidas de más afecten la precisión.
def test_repeticiones_adicionales_reducen_precision():
    # La referencia contiene dos palabras.
    referencia = "reparar llave"

    # La respuesta repite ambas palabras: tiene cuatro en total.
    respuesta = "reparar llave reparar llave"

    resultado = calcular_metricas(referencia, respuesta)

    # Solo dos de las cuatro palabras cuentan como coincidencias.
    assert resultado["precision"] == pytest.approx(0.5)

    # La respuesta incluye todas las palabras de la referencia.
    assert resultado["cobertura"] == pytest.approx(1.0)

    # F1 combina la precisión y la cobertura.
    assert resultado["f1"] == pytest.approx(2 / 3)


# Comprueba textos que no comparten ninguna palabra.
def test_textos_sin_coincidencias():
    resultado = calcular_metricas("gasfíter", "carpintero")

    # Sin coincidencias, las tres métricas deben ser cero.
    assert resultado == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


# Ejecuta la siguiente función una vez por cada pareja de textos.
@pytest.mark.parametrize(
    "referencia,respuesta",
    [
        ("", "reparar"),          # Referencia vacía.
        ("reparar", ""),          # Respuesta vacía.
        ("¡¡¡...!!!", "???"),      # Ambos quedan vacíos al limpiarlos.
    ],
)
def test_textos_vacios_no_producen_division_por_cero(referencia, respuesta):
    # Calcula las métricas con la pareja recibida de parametrize.
    resultado = calcular_metricas(referencia, respuesta)

    # Debe devolver ceros sin provocar una división por cero.
    assert resultado == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


# Comprueba el promedio de las métricas de varios casos.
def test_promedios_de_varios_resultados():
    # Usa dos resultados conocidos para verificar los cálculos.
    resultados = [
        {"precision": 1.0, "cobertura": 1.0, "f1": 1.0},
        {"precision": 1.0, "cobertura": 1 / 3, "f1": 0.5},
    ]

    # Precisión promedio: (1 + 1) / 2 = 1.
    # Cobertura promedio: (1 + 1/3) / 2 = 2/3.
    # F1 promedio: (1 + 0.5) / 2 = 0.75.
    assert resumir_metricas(resultados) == pytest.approx({
        "precision_promedio": 1.0,
        "cobertura_promedio": 2 / 3,
        "f1_promedio": 0.75,
    })


# Comprueba qué ocurre cuando todavía no hay casos evaluados.
def test_promedios_sin_resultados():
    # La lista vacía debe producir promedios en cero, sin errores.
    assert resumir_metricas([]) == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }