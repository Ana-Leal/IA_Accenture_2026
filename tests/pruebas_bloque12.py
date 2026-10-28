# Permite importar los módulos del proyecto.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest.mock import Mock, patch
import requests

from src.cliente import consultar_modelo


# Construye respuestas HTTP simuladas.
def crear_respuesta(codigo, datos):
    respuesta = Mock()
    respuesta.status_code = codigo
    respuesta.json.return_value = datos

    if codigo >= 400:
        respuesta.raise_for_status.side_effect = requests.exceptions.HTTPError()
    else:
        respuesta.raise_for_status.return_value = None

    return respuesta


# Simula una respuesta válida del modelo.
DATOS_VALIDOS = {
    "candidates": [
        {
            "content": {
                "parts": [{"text": "Respuesta simulada correcta"}]
            }
        }
    ]
}


def probar_recuperacion(codigo):
    # Simula dos fallos y una respuesta correcta.
    with patch.dict("os.environ", {"API_KEY": "clave_ficticia"}), patch(
        "src.consumir_gemini.requests.post",
        side_effect=[
            crear_respuesta(codigo, {}),
            crear_respuesta(codigo, {}),
            crear_respuesta(200, DATOS_VALIDOS),
        ],
    ) as envio, patch("src.cliente.sleep") as pausa, patch(
        "src.cliente.uniform", return_value=0
    ):
        resultado, datos = consultar_modelo("Necesito reparar una llave.")

        assert resultado == "Respuesta simulada correcta"
        assert datos == DATOS_VALIDOS
        assert envio.call_count == 3
        assert pausa.call_count == 2

        # Comprobación anterior del bloque 12: espera fija.
        # assert all(
        #     llamada.args == (2,) for llamada in pausa.call_args_list
        # )

        # Ahora comprueba esperas crecientes, sin variación aleatoria.
        assert [
            llamada.args[0] for llamada in pausa.call_args_list
        ] == [2, 4]

    print(f"CORRECTO: HTTP {codigo}, recuperación en el tercer intento.")
#def probar_recuperacion(codigo):
#    # Simula dos fallos y una respuesta correcta.
#    with patch.dict("os.environ", {"API_KEY": "clave_ficticia"}), patch(
#        "src.consumir_gemini.requests.post",
#        side_effect=[
#            crear_respuesta(codigo, {}),
#            crear_respuesta(codigo, {}),
#            crear_respuesta(200, DATOS_VALIDOS),
#        ],
#    ) as envio, patch("src.cliente.sleep") as pausa:
#        resultado, datos = consultar_modelo("Necesito reparar una llave.")
#
#        assert resultado == "Respuesta simulada correcta"
#        assert datos == DATOS_VALIDOS
#        assert envio.call_count == 3
#        assert pausa.call_count == 2
#        assert all(
#            llamada.args == (2,) for llamada in pausa.call_args_list
#       )
#
#    print(f"CORRECTO: HTTP {codigo}, recuperación en el tercer intento.")


def probar_agotamiento():
    with patch.dict("os.environ", {"API_KEY": "clave_ficticia"}), patch(
        "src.consumir_gemini.requests.post",
        return_value=crear_respuesta(503, {}),
    ) as envio, patch("src.cliente.sleep") as pausa:
        try:
            consultar_modelo("Necesito reparar una llave.")
        except RuntimeError as error:
            assert str(error) == (
                "El servicio no respondió tras los intentos permitidos. "
                "Intenta más tarde."
            )
        else:
            raise AssertionError("No se informó el agotamiento.")

        assert envio.call_count == 3
        assert pausa.call_count == 2

    print("CORRECTO: se detiene al agotar los tres intentos.")


def probar_credencial(codigo, datos):
    with patch.dict("os.environ", {"API_KEY": "clave_ficticia"}), patch(
        "src.consumir_gemini.requests.post",
        return_value=crear_respuesta(codigo, datos),
    ) as envio, patch("src.cliente.sleep") as pausa:
        try:
            consultar_modelo("Necesito reparar una llave.")
        except ValueError as error:
            assert str(error) == (
                "Credencial inválida o sin permiso. Revisa tu API_KEY."
            )
        else:
            raise AssertionError("No se detectó la credencial inválida.")

        assert envio.call_count == 1
        pausa.assert_not_called()

    print(f"CORRECTO: credencial inválida HTTP {codigo}, sin reintentos.")


if __name__ == "__main__":
    probar_recuperacion(429)
    probar_recuperacion(503)
    probar_agotamiento()

    probar_credencial(401, {})
    probar_credencial(403, {})
    probar_credencial(
        400,
        {
            "error": {
                "status": "INVALID_ARGUMENT",
                "details": [{"reason": "API_KEY_INVALID"}],
            }
        },
    )

    print("\nTodas las pruebas del bloque 12 pasaron.")