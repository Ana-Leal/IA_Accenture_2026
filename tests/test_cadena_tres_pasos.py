from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from src.cadena_tres_pasos import construir_cadena


def test_cadena_conecta_los_tres_pasos():
    # Simula las tres respuestas del modelo, en orden.
    respuestas = [
        "Reparar la puerta del baño sin reemplazarla.",
        "Se necesita un carpintero para reparar la puerta sin reemplazarla.",
        "- Contacta a un carpintero para reparar la puerta sin reemplazarla.",
    ]

    modelo_falso = MagicMock(
        side_effect=[
            AIMessage(content=texto)
            for texto in respuestas
        ]
    )

    # Construye la cadena utilizando el modelo simulado.
    cadena = construir_cadena(modelo_falso)

    entrada = (
        "Necesito reparar la puerta del baño, "
        "pero no quiero reemplazarla."
    )
    resultado = cadena.invoke({"texto": entrada})

    # Debe llamar al modelo exactamente tres veces.
    assert modelo_falso.call_count == 3

    # Obtiene las instrucciones recibidas en cada paso.
    prompts = [
        llamada.args[0].to_string()
        for llamada in modelo_falso.call_args_list
    ]

    # Verifica que cada paso reciba la información correspondiente.
    assert entrada in prompts[0]
    assert respuestas[0] in prompts[1]
    assert respuestas[1] in prompts[2]

    # Verifica que la salida final sea el texto de la tercera respuesta.
    assert isinstance(resultado, str)
    assert resultado == respuestas[2]