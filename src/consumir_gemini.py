# Permite leer variables de entorno.
import os

# Permite interpretar el JSON generado por el modelo.
import json

# Permite quitar las marcas de un bloque de código Markdown.
import re

# Permite enviar peticiones HTTP.
import requests

# Importa la función que carga las variables del archivo .env.
from dotenv import load_dotenv

# Carga las variables del archivo .env.
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
        # Informa que el tipo de dato no es válido.
        raise ValueError("La pregunta debe ser un texto.")

    # Elimina espacios al inicio y al final.
    pregunta = pregunta.strip()

    # Rechaza una pregunta vacía o que solo contenía espacios.
    if not pregunta:
        # Detiene la operación antes de enviar la petición.
        raise ValueError("La pregunta no puede estar vacía.")

    # Lee la clave desde la variable API_KEY del entorno.
    api_key = os.getenv("API_KEY")


    # Construye la dirección para consultar al modelo.
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent"
    )

    # Prepara el formato del contenido y la autenticación.
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
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

    # Agrega las instrucciones separadas del mensaje del usuario.
    # Son opcionales para conservar las llamadas de los bloques anteriores.
    if system_instruction is not None:
        if not isinstance(system_instruction, str) or not system_instruction.strip():
            raise ValueError("Las instrucciones de sistema deben ser un texto no vacío.")
        body["systemInstruction"] = {
            "parts": [{"text": system_instruction.strip()}]
        }

    # Solicita JSON con el esquema indicado cuando el llamador lo proporciona.
    if response_schema is not None:
        if not isinstance(response_schema, dict) or not response_schema:
            raise ValueError("El esquema de respuesta debe ser un diccionario no vacío.")
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    # Devuelve los datos preparados sin enviar la petición.
    return url, headers, body


# Envía la petición y devuelve la respuesta como diccionario.
def enviar_peticion(url, headers, body):
    # Intenta enviar la petición y comprobar su estado HTTP.
    try:
        # Envía los datos y limita el tiempo de espera.
        respuesta = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=60
        )

        # Genera un HTTPError ante una respuesta HTTP de error.
        respuesta.raise_for_status()

    # Captura cuando se supera el tiempo de espera.
    except requests.exceptions.Timeout:
        # Comunica el problema a quien llamó a esta función.
        raise RuntimeError(
            "El servicio tardó demasiado en responder. Intenta nuevamente."
        ) from None

    # Captura problemas al establecer o mantener la conexión.
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "No se pudo conectar con el servicio. Revisa tu conexión."
        ) from None

    # Captura respuestas HTTP de error.
    except requests.exceptions.HTTPError:
        # Obtiene el código de estado sin mostrar credenciales.
        codigo = respuesta.status_code

        # Informa que el servidor no pudo atender la petición.
        raise RuntimeError(
            f"El servicio rechazó la petición o no pudo atenderla "
            f"(HTTP {codigo})."
        ) from None

    # Intenta convertir el contenido recibido desde JSON.
    try:
        return respuesta.json()

    # Captura una respuesta cuyo contenido no sea JSON válido.
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
            "La respuesta del servicio no llegó en formato JSON válido."
        ) from None


# Extrae únicamente el texto generado.
def extraer_texto(datos):
    # Intenta acceder al texto de la primera respuesta.
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]

    # Captura campos ausentes o listas sin el elemento esperado.
    except (KeyError, IndexError):
        # Informa que no se encontró el texto esperado.
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        ) from None

# Convierte el texto generado en un objeto JSON y valida sus campos.
# tipos_esperados es un diccionario como {"oficio": str, "motivo": str}.
def parsear_respuesta_json(texto, tipos_esperados=None):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("La respuesta del modelo no contiene texto JSON.")

    # Acepta JSON directo o un único bloque Markdown que lo envuelva.
    contenido = texto.strip()
    bloque = re.fullmatch(r"```(?:json)?\s*\n?(.*?)\s*```", contenido, re.DOTALL | re.IGNORECASE)
    if bloque:
        contenido = bloque.group(1).strip()

    # Rechaza valores como NaN e Infinity, que no pertenecen al JSON estándar.
    def rechazar_constante(valor):
        raise ValueError("La respuesta contiene un valor que no es JSON válido.")

    try:
        datos = json.loads(contenido, parse_constant=rechazar_constante)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.") from None

    # El banco de prompts utilizará objetos con campos identificados por nombre.
    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto.")

    # Comprueba las claves obligatorias y sus tipos, si se han indicado.
    if tipos_esperados is not None:
        for clave, tipo in tipos_esperados.items():
            if clave not in datos:
                raise ValueError(f"La respuesta JSON no contiene el campo '{clave}'.")
            # La comprobación exacta evita aceptar True como un número entero.
            tipos = tipo if isinstance(tipo, tuple) else (tipo,)
            if type(datos[clave]) not in tipos:
                raise ValueError(f"El campo '{clave}' tiene un tipo incorrecto.")

    return datos


# Calcula el costo usando los tokens registrados en la respuesta.
# Los precios recibidos deben estar expresados por un solo token.
def calcular_costo(datos, precio_entrada, precio_salida):
    # Intenta obtener los conteos necesarios para calcular el costo.
    try:
        # Obtiene los metadatos de consumo de la respuesta.
        uso = datos["usageMetadata"]

        # Obtiene cuántos tokens se enviaron al modelo.
        tokens_entrada = uso["promptTokenCount"]

        # Obtiene cuántos tokens generó el modelo en su respuesta.
        tokens_salida = uso["candidatesTokenCount"]

    # Controla la ausencia de alguno de los campos necesarios.
    except KeyError:
        raise RuntimeError(
            "La respuesta no contiene los datos de uso necesarios "
            "para calcular el costo."
        ) from None

    # Multiplica los tokens enviados por su precio unitario.
    costo_entrada = tokens_entrada * precio_entrada

    # Multiplica los tokens generados por su precio unitario.
    costo_salida = tokens_salida * precio_salida

    # Devuelve la suma de ambos costos.
    return costo_entrada + costo_salida

# Coordina la preparación, el envío y la extracción.
def consultar_gemini(pregunta):
    # Prepara la URL, los encabezados y el cuerpo.
    url, headers, body = armar_peticion(pregunta)

    # Envía la petición y obtiene la respuesta.
    datos = enviar_peticion(url, headers, body)

    # Extrae el texto y lo devuelve.
    return extraer_texto(datos)


# Ejecuta la prueba solo al iniciar este archivo directamente.
if __name__ == "__main__":
    # Intenta completar la consulta.
    try:
        # Llama a la función que coordina la consulta.
        resultado = consultar_gemini(
            "Confirma en una frase corta que esta conexión funciona."
        )

        # Muestra el texto generado cuando la consulta es exitosa.
        print(resultado)

    # Captura errores de validación y los errores controlados.
    except (ValueError, RuntimeError) as error:
        # Muestra el motivo del fallo sin un traceback.
        print("No se pudo completar la operación:", error)
