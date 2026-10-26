# Permite esperar entre intentos.
from time import sleep

# Reutiliza las funciones del módulo existente.
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)


# Reintenta únicamente las operaciones que fallan temporalmente.
def con_reintento(operacion, intentos=3, espera_segundos=2):
    if type(intentos) is not int or intentos < 1:
        raise ValueError("La cantidad de intentos debe ser un entero positivo.")

    if (
        type(espera_segundos) not in (int, float)
        or not 0 <= espera_segundos < float("inf")
    ):
        raise ValueError("La espera debe ser un número finito no negativo.")

    # Incluye el primer intento dentro del límite.
    for intento in range(1, intentos + 1):
        try:
            return operacion()

        except TimeoutError:
            # No espera ni repite después del último intento.
            if intento == intentos:
                raise

            print(
                f"Intento {intento} de {intentos} falló por un error temporal. "
                f"Reintentando en {espera_segundos} segundos...",
                flush=True,
            )
            sleep(espera_segundos)


# Coordina la consulta y devuelve el resultado procesado y los datos de uso.
def consultar_modelo(
    pregunta,
    *,
    system_instruction=None,
    response_schema=None,
    tipos_esperados=None,
    intentos=3,
    espera_segundos=2,
):
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

    # Conserva los datos originales para calcular tokens y costo.
    return resultado, datos