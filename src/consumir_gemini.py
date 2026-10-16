# Permite leer variables de entorno.
import os

# Permite enviar peticiones HTTP.
import requests

# Permite cargar las variables del archivo .env.
from dotenv import load_dotenv

# Carga nuestra configuración.
load_dotenv()


# Prepara los datos necesarios para consultar Gemini.
def armar_peticion(pregunta):
    # Lee la clave desde el entorno.
    api_key = os.getenv("API_KEY")

    # Conserva el modelo que ya utilizamos.
    modelo = "gemini-3.8-flash"

    # Construye la dirección del modelo.
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent"
    )

    # Prepara el tipo de contenido y la autenticación.
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # Organiza la pregunta con la estructura que espera Gemini.
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    # Devuelve los tres elementos sin enviar ninguna petición.
    return url, headers, body


# Envía la petición y devuelve la respuesta como diccionario.
def enviar_peticion(url, headers, body):
   
    respuesta = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=60
    )

    
   

    # Convierte el cuerpo JSON recibido en un diccionario.
    return respuesta.json()


# Extrae únicamente el texto generado.
def extraer_texto(datos):
    # Selecciona el primer candidato y la primera parte de su contenido.
    return datos["candidates"][0]["content"]["parts"][0]["text"]


# Coordina las tres funciones anteriores.
def consultar_gemini(pregunta):
    # Prepara la URL, los encabezados y el cuerpo.
    url, headers, body = armar_peticion(pregunta)

    # Envía la petición y obtiene el diccionario de respuesta.
    datos = enviar_peticion(url, headers, body)


    # Extrae el texto y lo devuelve.
    return extraer_texto(datos)


# Ejecuta la prueba solo cuando iniciamos este archivo directamente.
if __name__ == "__main__":
    # Llama a la función que coordina la consulta.
    resultado = consultar_gemini(
        "Confirma en una frase corta que esta conexión funciona."
    )

  
    print(resultado)