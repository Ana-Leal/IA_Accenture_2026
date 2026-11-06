from unittest.mock import MagicMock
from langchain_core.runnables import RunnableLambda

from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_cadena_queja_segura,
    procesar_mensaje_seguro,
)


# Comprueba que una ruta fallida devuelva su respuesta de respaldo.
def test_cadena_queja_usa_fallback():
    def fallar(datos):
        raise ConnectionError("Fallo de conexión simulado")

    # Esta ruta falla siempre, sin realizar llamadas reales.
    cadena_rota = RunnableLambda(fallar)
    cadena_segura = construir_cadena_queja_segura(cadena_rota)

    resultado = cadena_segura.invoke({"mensaje": "El servicio no funciona"})

    # Verifica el texto del respaldo, no solo la ausencia de errores.
    assert resultado == (
        "No pudimos generar una respuesta a tu queja en este momento. "
        "Intenta nuevamente más tarde."
    )


# Comprueba un fallo anterior a la selección de cualquier ruta.
def test_fallo_clasificacion_devuelve_respuesta_segura(capsys):
    clasificacion_falsa = MagicMock(
        side_effect=ConnectionError("Fallo de clasificación simulado")
    )

    queja = MagicMock()
    sugerencia = MagicMock()
    pregunta = MagicMock()

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=queja,
        cadena_sugerencia=sugerencia,
        cadena_pregunta=pregunta,
    )

    resultado = procesar_mensaje_seguro(cadena, "Mensaje de prueba")

    assert resultado == (
        "No pudimos procesar tu mensaje en este momento. "
        "Intenta de nuevo más tarde."
    )

    # Confirma que el error quedó informado en la consola.
    salida = capsys.readouterr()
    assert "Fallo de clasificación simulado" in salida.out

    # Si falla la clasificación, ninguna ruta debe ejecutarse.
    queja.assert_not_called()
    sugerencia.assert_not_called()
    pregunta.assert_not_called()