import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from src.enrutamiento import (
    construir_paso_clasificacion,
    construir_cadena_con_enrutamiento,
)


# Ejecuta una prueba por cada categoría, incluida una desconocida.
@pytest.mark.parametrize(
    "categoria,ruta_esperada",
    [
        ("queja", "queja"),
        ("sugerencia", "sugerencia"),
        ("pregunta", "pregunta"),
        ("categoria_desconocida", "pregunta"),
    ],
)
def test_enrutamiento_selecciona_ruta(categoria, ruta_esperada):
    # Fuerza la clasificación sin consultar a Gemini.
    clasificacion_falsa = MagicMock(return_value=categoria)

    # Cada ruta devuelve un texto distinto para reconocerla.
    rutas = {
        "queja": MagicMock(return_value="Respuesta de queja"),
        "sugerencia": MagicMock(return_value="Respuesta de sugerencia"),
        "pregunta": MagicMock(return_value="Respuesta de pregunta"),
    }

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=rutas["queja"],
        cadena_sugerencia=rutas["sugerencia"],
        cadena_pregunta=rutas["pregunta"],
    )

    resultado = cadena.invoke({"mensaje": "Mensaje de prueba"})

    # Comprueba la respuesta y los datos recibidos por la ruta elegida.
    assert resultado == rutas[ruta_esperada].return_value
    rutas[ruta_esperada].assert_called_once_with({
        "mensaje": "Mensaje de prueba",
        "categoria": categoria,
    })

    # Las otras rutas no deben ejecutarse.
    for nombre, ruta in rutas.items():
        if nombre != ruta_esperada:
            ruta.assert_not_called()


def test_clasificacion_normaliza_antes_de_comparar():
    # Simula una categoría con mayúsculas, espacios y salto de línea.
    modelo_falso = MagicMock(
        return_value=AIMessage(content=" Queja \n")
    )

    paso = construir_paso_clasificacion(modelo_falso)
    resultado = paso.invoke({"mensaje": "Algo salió mal"})

    # La categoría debe quedar lista para compararse.
    assert resultado == "queja"