# Permite leer variables de entorno.
import os

# Permite enviar peticiones HTTP a Gemini.
import requests

# Importa la función que lee el archivo .env.
from dotenv import load_dotenv

# Carga las variables guardadas en tu archivo .env.
load_dotenv()


# Define la función que recibirá una pregunta.
def consultar_gemini(pregunta):

    # Lee API_KEY desde el entorno y guarda su valor en api_key.
    api_key = os.getenv("API_KEY")
    modelo = "gemini-3.8-flash"
    
    # Construye la url a la que se enviará la pregunta
    # La permite reemplazar el modelo por el valor de esa variable
    # GenerateContent es la operacion que solicita generar una respuesta
    url = (f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent"
    )
        # Crea un diccionario con los encabezados de la petición.
    headers = {
        # Indica que se enviará el contenido en formato JSON.
        "Content-Type": "application/json",

        # Envía la clave desde el archivo .env.
        "x-goog-api-key": api_key
    }

    # Crea el cuerpo de la petición con la estructura que espera Gemini.
    body = {
        # contents contiene los mensajes que se envian al modelo.
        "contents": [
            {
                # parts contiene las partes del mensaje.
                "parts": [
                    {
                        # Usa la pregunta que recibió la función.
                        "text": pregunta
                    }
                ]
            }
        ]
    }
     # Envía la petición POST a la URL de Gemini.
    # headers lleva la clave y el tipo de contenido.
    # json=body convierte el diccionario al formato JSON que enviaremos.
    # timeout=60 limita la espera de respuesta para evitar esperar indefinidamente.
    respuesta = requests.post(url, headers=headers, json=body, timeout=60)

    # Convierte el cuerpo JSON de la respuesta en un diccionario de Python.
    # Recorre la estructura de Gemini y devuelve el texto generado.
    # [0] selecciona el primer elemento de cada lista.
    datos = respuesta.json()
    return datos["candidates"][0]["content"]["parts"][0]["text"]
    
    # Ejecuta esta prueba solo cuando se abre este archivo como programa principal.
# Si después se importa desde otro archivo, la prueba no se ejecutará.
if __name__ == "__main__":

    # Llama a la función y guarda el texto que devuelve Gemini.
    resultado = consultar_gemini(
        "Confirma en una frase corta que esta conexión funciona."
    )

    # Muestra el texto generado en la terminal.
    print(resultado)