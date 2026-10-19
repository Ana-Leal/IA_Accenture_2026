# Permite importar el módulo desde la carpeta src.
import sys
from pathlib import Path

# Agrega la raíz del repositorio a las rutas de importación.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Permite simular respuestas y errores sin acceder a Internet.
from unittest.mock import Mock, patch
import requests

# Importa las funciones que vamos a comprobar.
from src.consumir_gemini import enviar_peticion, extraer_texto


# Comprueba que una operación produzca el error controlado esperado.
def comprobar_error(nombre, operacion, mensaje_esperado):
    print("\nPRUEBA:", nombre)

    try:
        operacion()
    except RuntimeError as error:
        # Verifica el mensaje; un mensaje diferente hace fallar la prueba.
        assert str(error) == mensaje_esperado, str(error)
        print("CORRECTO:", error)
    else:
        # Falla si la operación no detectó el problema.
        raise AssertionError("No se produjo el error esperado.")


# Simula un fallo de conexión en lugar de enviar una petición.
with patch(
    "src.consumir_gemini.requests.post",
    side_effect=requests.exceptions.ConnectionError("Fallo simulado")
):
    comprobar_error(
        "Error de conexión",
        lambda: enviar_peticion("https://ejemplo.test", {}, {}),
        "No se pudo conectar con el servicio. Revisa tu conexión."
    )


# Crea una respuesta simulada cuya conversión a JSON falla.
respuesta_simulada = Mock()
respuesta_simulada.json.side_effect = requests.exceptions.JSONDecodeError(
    "JSON inválido", "contenido no JSON", 0
)

# Sustituye la petición por esa respuesta simulada.
with patch(
    "src.consumir_gemini.requests.post",
    return_value=respuesta_simulada
):
    comprobar_error(
        "Formato JSON inválido",
        lambda: enviar_peticion("https://ejemplo.test", {}, {}),
        "La respuesta del servicio no llegó en formato JSON válido."
    )


# Comprueba una respuesta que no contiene el campo candidates.
comprobar_error(
    "Campo faltante",
    lambda: extraer_texto({}),
    "La respuesta no trae el texto generado en el lugar esperado."
)

# Comprueba una respuesta cuya lista de candidatos está vacía.
comprobar_error(
    "Lista de candidatos vacía",
    lambda: extraer_texto({"candidates": []}),
    "La respuesta no trae el texto generado en el lugar esperado."
)

print("\nTodas las pruebas controladas pasaron.")