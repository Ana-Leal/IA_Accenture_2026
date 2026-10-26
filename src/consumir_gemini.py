# Permite leer variables de entorno.
import os

# Permite interpretar el JSON generado por el modelo.
import json

# Permite reconocer bloques de código Markdown.
import re

# Permite enviar peticiones HTTP.
import requests

# Permite cargar las variables del archivo .env.
from dotenv import load_dotenv

load_dotenv()


# Prepara los datos necesarios para consultar Gemini.
def armar_peticion(
    pregunta,
    modelo="gemini-3.5-flash-lite",
    *,
    system_instruction=None,
    response_schema=None,
):
    # Comprueba que la pregunta sea un texto.
    if not isinstance(pregunta, str):
        raise ValueError("La pregunta debe ser un texto.")

    # Elimina espacios al inicio y al final.
    pregunta = pregunta.strip()

    # Rechaza una pregunta vacía.
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")

    # Lee la clave desde el entorno.
    api_key = os.getenv("API_KEY")

    # Construye la dirección para consultar al modelo.
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent"
    )

    # Prepara el formato del contenido y la autenticación.
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    # Coloca la pregunta en la estructura que espera Gemini.
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    # Agrega las instrucciones de sistema cuando se proporcionan.
    if system_instruction is not None:
        if (
            not isinstance(system_instruction, str)
            or not system_instruction.strip()
        ):
            raise ValueError(
                "Las instrucciones de sistema deben ser un texto no vacío."
            )

        body["systemInstruction"] = {
            "parts": [{"text": system_instruction.strip()}]
        }

    # Solicita una respuesta JSON con el esquema indicado.
    if response_schema is not None:
        if not isinstance(response_schema, dict) or not response_schema:
            raise ValueError(
                "El esquema de respuesta debe ser un diccionario no vacío."
            )

        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    # Devuelve los datos preparados sin enviar la petición.
    return url, headers, body


# Envía una petición y clasifica los errores del servicio.
def enviar_peticion(url, headers, body):
    # Comprueba que exista una credencial antes de enviar.
    api_key = headers.get("x-goog-api-key")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError(
            "Falta la credencial. Configura API_KEY en tu archivo .env."
        )

    try:
        # Envía los datos y conserva el tiempo de espera.
        respuesta = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=60,
        )

    # Clasifica el tiempo de espera como un error temporal.
    except requests.exceptions.Timeout:
        raise TimeoutError(
            "El servicio tardó demasiado en responder. Intenta nuevamente."
        ) from None

    # Clasifica los problemas de conexión como errores temporales.
    except requests.exceptions.ConnectionError:
        raise TimeoutError(
            "No se pudo conectar con el servicio. Revisa tu conexión."
        ) from None

    # Obtiene el estado HTTP sin mostrar credenciales.
    codigo = respuesta.status_code

        # Reconoce la credencial inválida que Gemini informa como HTTP 400.
    if codigo == 400:
        try:
            datos_error = respuesta.json()
        except requests.exceptions.JSONDecodeError:
            datos_error = {}

        # Comprueba la estructura antes de consultar los detalles.
        error = (
            datos_error.get("error", {})
            if isinstance(datos_error, dict)
            else {}
        )
        detalles = error.get("details", []) if isinstance(error, dict) else []

        if isinstance(detalles, list) and any(
            isinstance(detalle, dict)
            and detalle.get("reason") == "API_KEY_INVALID"
            for detalle in detalles
        ):
            raise ValueError(
                "Credencial inválida o sin permiso. Revisa tu API_KEY."
            )

    # Los errores de autenticación o permisos no se reintentan.
    if codigo in (401, 403):
        raise ValueError(
            "Credencial inválida o sin permiso. Revisa tu API_KEY."
        )

    # El límite de uso permite un reintento con espera.
    if codigo == 429:
        raise TimeoutError(
            "Límite de peticiones excedido. Hay que esperar y reintentar."
        )

    # Los fallos del servidor se clasifican como temporales.
    if 500 <= codigo < 600:
        raise TimeoutError(
            f"El proveedor no pudo atender la petición (HTTP {codigo}). "
            "Hay que esperar y reintentar."
        )

    # Controla los demás errores HTTP.
    try:
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError:
        raise RuntimeError(
            f"El servicio rechazó la petición (HTTP {codigo})."
        ) from None

    # Convierte la respuesta recibida en datos de Python.
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
            "La respuesta del servicio no llegó en formato JSON válido."
        ) from None


# Extrae únicamente el texto generado.
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]

    # Controla campos ausentes o listas vacías.
    except (KeyError, IndexError):
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        ) from None


# Convierte el texto generado en JSON y valida campos y tipos.
def parsear_respuesta_json(texto, tipos_esperados=None):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("La respuesta del modelo no contiene texto JSON.")

    contenido = texto.strip()

    # Acepta JSON directo o envuelto en un bloque Markdown.
    bloque = re.fullmatch(
        r"```(?:json)?\s*\n?(.*?)\s*```",
        contenido,
        re.DOTALL | re.IGNORECASE,
    )
    if bloque:
        contenido = bloque.group(1).strip()

    # Rechaza constantes que no pertenecen al JSON estándar.
    def rechazar_constante(valor):
        raise ValueError(
            "La respuesta contiene un valor que no es JSON válido."
        )

    try:
        datos = json.loads(
            contenido,
            parse_constant=rechazar_constante,
        )
    except json.JSONDecodeError:
        raise ValueError(
            "La respuesta del modelo no es JSON válido."
        ) from None

    # La respuesta debe ser un objeto con campos identificados.
    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto.")

    # Comprueba las claves obligatorias y sus tipos.
    if tipos_esperados is not None:
        for clave, tipo in tipos_esperados.items():
            if clave not in datos:
                raise ValueError(
                    f"La respuesta JSON no contiene el campo '{clave}'."
                )

            # La comparación exacta evita aceptar bool como int.
            tipos = tipo if isinstance(tipo, tuple) else (tipo,)
            if type(datos[clave]) not in tipos:
                raise ValueError(
                    f"El campo '{clave}' tiene un tipo incorrecto."
                )

    return datos


# Calcula el costo con precios expresados por un solo token.
def calcular_costo(datos, precio_entrada, precio_salida):
    try:
        # Obtiene los conteos registrados en la respuesta.
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]

    except KeyError:
        raise RuntimeError(
            "La respuesta no contiene los datos de uso necesarios "
            "para calcular el costo."
        ) from None

    costo_entrada = tokens_entrada * precio_entrada
    costo_salida = tokens_salida * precio_salida

    return costo_entrada + costo_salida


# Conserva la consulta sencilla de los bloques anteriores.
def consultar_gemini(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


# Ejecuta esta prueba solo al iniciar el archivo directamente.
if __name__ == "__main__":
    try:
        resultado = consultar_gemini(
            "Confirma en una frase corta que esta conexión funciona."
        )
        print(resultado)

    # Incluye los nuevos errores temporales del bloque 12.
    except (ValueError, TimeoutError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)