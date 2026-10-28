# Permite esperar entre intentos.
from time import sleep

# Agrega una pequeña variación aleatoria a la espera.
from random import uniform

# Reutiliza las funciones del módulo existente.
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
    calcular_costo,
)


# Conserva las tarifas de referencia, expresadas en USD por token.
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000

# Acumula los costos conocidos durante esta ejecución del programa.
costo_total_sesion = 0.0

# None indica que no hay un costo disponible para la última consulta.
costo_ultima_consulta = None


# Versión anterior del bloque 12: espera fija.
# Se conserva como referencia y no se ejecuta.
#
# def con_reintento(operacion, intentos=3, espera_segundos=2):
#     if type(intentos) is not int or intentos < 1:
#         raise ValueError("La cantidad de intentos debe ser un entero positivo.")
#
#     if (
#         type(espera_segundos) not in (int, float)
#         or not 0 <= espera_segundos < float("inf")
#     ):
#         raise ValueError("La espera debe ser un número finito no negativo.")
#
#     for intento in range(1, intentos + 1):
#         try:
#             return operacion()
#
#         except TimeoutError:
#             if intento == intentos:
#                 raise
#
#             print(
#                 f"Intento {intento} de {intentos} falló por un error temporal. "
#                 f"Reintentando en {espera_segundos} segundos...",
#                 flush=True,
#             )
#             sleep(espera_segundos)


# Reintenta errores temporales con espera creciente, límite y variación.
def con_reintento(
    operacion,
    intentos=3,
    espera_segundos=2,
    espera_maxima=30,
):
    if type(intentos) is not int or intentos < 1:
        raise ValueError("La cantidad de intentos debe ser un entero positivo.")

    if (
        type(espera_segundos) not in (int, float)
        or not 0 <= espera_segundos < float("inf")
    ):
        raise ValueError("La espera debe ser un número finito no negativo.")

    if (
        type(espera_maxima) not in (int, float)
        or not 0 <= espera_maxima < float("inf")
    ):
        raise ValueError(
            "La espera máxima debe ser un número finito no negativo."
        )

    # Comienza con la espera base, respetando el límite.
    espera_base = min(espera_segundos, espera_maxima)

    # Incluye el primer intento dentro del límite.
    for intento in range(1, intentos + 1):
        try:
            return operacion()

        except TimeoutError:
            # No espera ni repite después del último intento.
            if intento == intentos:
                raise

            # Agrega hasta un 10 % de variación aleatoria.
            variacion = uniform(0, espera_base * 0.10)

            # La espera final nunca supera el máximo configurado.
            espera = min(espera_base + variacion, espera_maxima)

            print(
                f"Intento {intento} de {intentos} falló por un error temporal. "
                f"Reintentando en {espera:.2f} segundos...",
                flush=True,
            )
            sleep(espera)

            # Duplica la espera base para el siguiente reintento.
            espera_base = min(espera_base * 2, espera_maxima)


# Calcula y acumula el costo de una respuesta recibida.
def registrar_costo(datos):
    global costo_total_sesion

    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        tokens_respuesta = uso["candidatesTokenCount"]
        tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

        # Acepta únicamente conteos enteros no negativos.
        conteos = (
            tokens_entrada,
            tokens_respuesta,
            tokens_razonamiento,
        )
        if any(type(valor) is not int or valor < 0 for valor in conteos):
            return None

    except (KeyError, TypeError, AttributeError):
        # Un costo desconocido no se registra como si fuera cero.
        return None

    # Incluye el razonamiento sin modificar los datos originales.
    datos_costo = {
        "usageMetadata": {
            "promptTokenCount": tokens_entrada,
            "candidatesTokenCount": tokens_respuesta + tokens_razonamiento,
        }
    }

    costo = calcular_costo(
        datos_costo,
        PRECIO_ENTRADA,
        PRECIO_SALIDA,
    )

    # Acumula el costo de esta respuesta.
    costo_total_sesion += costo
    return costo


# Coordina la consulta y devuelve el resultado procesado y los datos originales.
def consultar_modelo(
    pregunta,
    *,
    system_instruction=None,
    response_schema=None,
    tipos_esperados=None,
    intentos=3,
    espera_segundos=2,
):
    global costo_ultima_consulta

    # Evita conservar el costo de una consulta anterior si esta falla.
    costo_ultima_consulta = None

    # Reutiliza el modelo predeterminado y la configuración existente.
    url, headers, body = armar_peticion(
        pregunta,
        system_instruction=system_instruction,
        response_schema=response_schema,
    )

    try:
        # Los reintentos quedan dentro del cliente.
        datos = con_reintento(
            lambda: enviar_peticion(url, headers, body),
            intentos=intentos,
            espera_segundos=espera_segundos,
        )
    except TimeoutError:
        raise RuntimeError(
            "El servicio no respondió tras los intentos permitidos. "
            "Intenta más tarde."
        ) from None

    # Registra una sola vez el consumo de la respuesta recibida.
    # Se registra incluso si después falla la validación del texto.
    costo_ultima_consulta = registrar_costo(datos)

    # Procesa la respuesta después de completar el envío.
    texto = extraer_texto(datos)

    # Valida el JSON cuando se ha solicitado una respuesta estructurada.
    if response_schema is not None or tipos_esperados is not None:
        resultado = parsear_respuesta_json(
            texto,
            tipos_esperados=tipos_esperados,
        )
    else:
        resultado = texto

    # Conserva los dos valores que espera el resto del proyecto.
    return resultado, datos