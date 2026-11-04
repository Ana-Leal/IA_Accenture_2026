# Casos nuevos para completar las 20 respuestas de la evaluación.
# Los tres primeros casos ya están guardados desde el bloque 15.
#
# Se va trabajar el campo "resumen" del prompt "resumir_necesidad".
# Las referencias se escriben antes de consultar a Gemini.
# Son respuestas esperadas para comparar, no respuestas del modelo.
#
# Se incluyen solicitudes simples, cantidades, negaciones y varios trabajos
# para observar si el resumen conserva la información importante.

CASOS_BLOQUE17 = [
    {
        "caso": 4,
        "consulta": "Necesito cambiar la cerradura de la puerta principal.",
        "referencia": "Cambiar la cerradura de la puerta principal.",
    },
    {
        "caso": 5,
        "consulta": "Necesito instalar una lámpara en el comedor.",
        "referencia": "Instalar una lámpara en el comedor.",
    },
    {
        "caso": 6,
        "consulta": "Necesito reparar una ventana que no cierra en la cocina.",
        "referencia": "Reparar una ventana que no cierra en la cocina.",
    },
    {
        "caso": 7,
        "consulta": "Necesito limpiar la canaleta del techo del patio.",
        "referencia": "Limpiar la canaleta del techo del patio.",
    },
    {
        "caso": 8,
        "consulta": "Necesito armar un escritorio que compré para mi dormitorio.",
        "referencia": "Armar un escritorio para el dormitorio.",
    },
    {
        "caso": 9,
        "consulta": "Necesito cambiar tres enchufes del living.",
        "referencia": "Cambiar tres enchufes del living.",
    },
    {
        "caso": 10,
        "consulta": "Necesito instalar dos repisas de madera en la cocina.",
        "referencia": "Instalar dos repisas de madera en la cocina.",
    },
    {
        "caso": 11,
        "consulta": (
            "Necesito fabricar una mesa de madera de 120 centímetros "
            "de largo para el comedor."
        ),
        "referencia": (
            "Fabricar una mesa de madera de 120 centímetros "
            "de largo para el comedor."
        ),
    },
    {
        "caso": 12,
        "consulta": (
            "Necesito pintar solo una pared del dormitorio, "
            "no las cuatro paredes."
        ),
        "referencia": (
            "Pintar solo una pared del dormitorio, no las cuatro paredes."
        ),
    },
    {
        "caso": 13,
        "consulta": (
            "Necesito reparar la puerta del baño, "
            "pero no quiero reemplazarla."
        ),
        "referencia": "Reparar la puerta del baño sin reemplazarla.",
    },
    {
        "caso": 14,
        "consulta": (
            "Necesito revisar una mancha de humedad en el dormitorio. "
            "Todavía no quiero pintar la pared."
        ),
        "referencia": (
            "Revisar una mancha de humedad en el dormitorio "
            "sin pintar la pared todavía."
        ),
    },
    {
        "caso": 15,
        "consulta": (
            "Necesito reparar la llave del baño "
            "y destapar el desagüe del lavamanos."
        ),
        "referencia": (
            "Reparar la llave del baño "
            "y destapar el desagüe del lavamanos."
        ),
    },
    {
        "caso": 16,
        "consulta": (
            "Necesito lijar y barnizar una mesa de madera del comedor."
        ),
        "referencia": "Lijar y barnizar una mesa de madera del comedor.",
    },
    {
        "caso": 17,
        "consulta": (
            "Necesito retirar una repisa rota "
            "e instalar una nueva en el dormitorio."
        ),
        "referencia": (
            "Retirar una repisa rota "
            "e instalar una nueva en el dormitorio."
        ),
    },
    {
        "caso": 18,
        "consulta": (
            "La puerta del dormitorio roza el piso cuando la abro. "
            "Necesito que la ajusten."
        ),
        "referencia": "Ajustar la puerta del dormitorio que roza el piso.",
    },
    {
        "caso": 19,
        "consulta": (
            "El lavamanos del baño está tapado y el agua no baja. "
            "Necesito que lo destapen."
        ),
        "referencia": "Destapar el lavamanos del baño.",
    },
    {
        "caso": 20,
        "consulta": (
            "Necesito cambiar las bisagras de un mueble. "
            "Son cuatro bisagras y quiero conservar las puertas."
        ),
        "referencia": (
            "Cambiar cuatro bisagras de un mueble "
            "conservando las puertas."
        ),
    },
]