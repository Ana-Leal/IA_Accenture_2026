# Permite importar el módulo desde la raíz del repositorio.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Permite simular respuestas y errores sin acceder a Internet.
from unittest.mock import Mock, patch
import requests

from src.consumir_gemini import enviar_peticion, extraer_texto


# Clave ficticia para las peticiones simuladas.
HEADERS_PRUEBA = {"x-goog-api-key": "clave_ficticia"}


# Comprueba el tipo de error y su mensaje.
def comprobar_error(nombre, operacion, mensaje_esperado, tipo_error=RuntimeError):
    print("\nPRUEBA:", nombre)

    try:
        operacion()
    except tipo_error as error:
        assert str(error) == mensaje_esperado, str(error)
        print("CORRECTO:", error)
    else:
        raise AssertionError("No se produjo el error esperado.")


# Simula un fallo de conexión.
with patch(
    "src.consumir_gemini.requests.post",
    side_effect=requests.exceptions.ConnectionError("Fallo simulado"),
):
    comprobar_error(
        "Error de conexión",
        lambda: enviar_peticion("https://ejemplo.test", HEADERS_PRUEBA, {}),
        "No se pudo conectar con el servicio. Revisa tu conexión.",
        tipo_error=TimeoutError,
    )


# Simula una respuesta HTTP exitosa con contenido JSON inválido.
respuesta_simulada = Mock()
respuesta_simulada.status_code = 200
respuesta_simulada.raise_for_status.return_value = None
respuesta_simulada.json.side_effect = requests.exceptions.JSONDecodeError(
    "JSON inválido", "contenido no JSON", 0
)

with patch(
    "src.consumir_gemini.requests.post",
    return_value=respuesta_simulada,
):
    comprobar_error(
        "Formato JSON inválido",
        lambda: enviar_peticion("https://ejemplo.test", HEADERS_PRUEBA, {}),
        "La respuesta del servicio no llegó en formato JSON válido.",
    )


# Comprueba una respuesta sin el campo candidates.
comprobar_error(
    "Campo faltante",
    lambda: extraer_texto({}),
    "La respuesta no trae el texto generado en el lugar esperado.",
)


# Comprueba una lista de candidatos vacía.
comprobar_error(
    "Lista de candidatos vacía",
    lambda: extraer_texto({"candidates": []}),
    "La respuesta no trae el texto generado en el lugar esperado.",
)


# Simula un tiempo de espera agotado.
with patch(
    "src.consumir_gemini.requests.post",
    side_effect=requests.exceptions.Timeout("Timeout simulado"),
):
    comprobar_error(
        "Tiempo de espera agotado",
        lambda: enviar_peticion("https://ejemplo.test", HEADERS_PRUEBA, {}),
        "El servicio tardó demasiado en responder. Intenta nuevamente.",
        tipo_error=TimeoutError,
    )


print("\nTodas las pruebas controladas pasaron.")