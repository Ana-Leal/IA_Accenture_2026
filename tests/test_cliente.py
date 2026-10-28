# Pruebas unitarias del cliente modular.
# Las peticiones y las esperas se simulan: no utilizan Internet.
from unittest.mock import Mock, call

import pytest

from src import cliente
from src import consumir_gemini


@pytest.fixture(autouse=True)
def entorno_aislado(monkeypatch):
    # Cada prueba empieza con los costos en cero.
    monkeypatch.setattr(cliente, "costo_total_sesion", 0.0)
    monkeypatch.setattr(cliente, "costo_ultima_consulta", None)

    # Usa una credencial ficticia y evita llamadas reales por accidente.
    monkeypatch.setenv("API_KEY", "clave_ficticia")
    monkeypatch.setattr(
        consumir_gemini.requests,
        "post",
        Mock(side_effect=AssertionError("No debe realizarse una petición real.")),
    )

    # Las pruebas son inmediatas y tienen tiempos predecibles.
    monkeypatch.setattr(cliente, "sleep", Mock())
    monkeypatch.setattr(cliente, "uniform", Mock(return_value=0))


def respuesta_simulada(codigo, datos):
    respuesta = Mock()
    respuesta.status_code = codigo
    respuesta.json.return_value = datos
    return respuesta


def datos_validos():
    # Una respuesta válida con consumo conocido.
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                '{"oficio": "Gasfíter", '
                                '"motivo": "Revisar la llave."}'
                            )
                        }
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 150,
            "candidatesTokenCount": 32,
            "thoughtsTokenCount": 10,
        },
    }


# Pruebas de enviar_peticion.
def test_enviar_peticion_devuelve_json(monkeypatch):
    datos = datos_validos()
    envio = Mock(return_value=respuesta_simulada(200, datos))
    monkeypatch.setattr(consumir_gemini.requests, "post", envio)

    resultado = consumir_gemini.enviar_peticion(
        "https://ejemplo.test",
        {"x-goog-api-key": "clave_ficticia"},
        {},
    )

    assert resultado == datos
    envio.assert_called_once()


@pytest.mark.parametrize("codigo", [401, 403])
def test_enviar_peticion_rechaza_credencial(monkeypatch, codigo):
    monkeypatch.setattr(
        consumir_gemini.requests,
        "post",
        Mock(return_value=respuesta_simulada(codigo, {})),
    )

    with pytest.raises(ValueError, match="Credencial inválida"):
        consumir_gemini.enviar_peticion(
            "https://ejemplo.test",
            {"x-goog-api-key": "clave_ficticia"},
            {},
        )


def test_enviar_peticion_reconoce_clave_invalida_http400(monkeypatch):
    datos = {
        "error": {
            "details": [{"reason": "API_KEY_INVALID"}],
        }
    }
    monkeypatch.setattr(
        consumir_gemini.requests,
        "post",
        Mock(return_value=respuesta_simulada(400, datos)),
    )

    with pytest.raises(ValueError, match="Credencial inválida"):
        consumir_gemini.enviar_peticion(
            "https://ejemplo.test",
            {"x-goog-api-key": "clave_ficticia"},
            {},
        )


@pytest.mark.parametrize("codigo", [429, 500, 503])
def test_enviar_peticion_clasifica_error_temporal(monkeypatch, codigo):
    monkeypatch.setattr(
        consumir_gemini.requests,
        "post",
        Mock(return_value=respuesta_simulada(codigo, {})),
    )

    with pytest.raises(TimeoutError):
        consumir_gemini.enviar_peticion(
            "https://ejemplo.test",
            {"x-goog-api-key": "clave_ficticia"},
            {},
        )


# Pruebas de con_reintento.
def test_reintento_recupera_con_esperas_crecientes():
    operacion = Mock(side_effect=[
        TimeoutError("Temporal"),
        TimeoutError("Temporal"),
        "Respuesta correcta",
    ])

    resultado = cliente.con_reintento(operacion)

    assert resultado == "Respuesta correcta"
    assert operacion.call_count == 3
    assert cliente.sleep.call_args_list == [call(2), call(4)]


def test_reintento_aplica_variacion_y_respeta_limite(monkeypatch):
    # Devuelve el máximo de variación permitido en cada espera.
    monkeypatch.setattr(
        cliente,
        "uniform",
        Mock(side_effect=lambda minimo, maximo: maximo),
    )
    operacion = Mock(side_effect=[
        TimeoutError("Temporal"),
        TimeoutError("Temporal"),
        "Respuesta correcta",
    ])

    cliente.con_reintento(
        operacion,
        espera_segundos=2,
        espera_maxima=3,
    )

    esperas = [
        llamada.args[0]
        for llamada in cliente.sleep.call_args_list
    ]
    assert esperas == pytest.approx([2.2, 3.0])


def test_reintento_agotado_conserva_error_y_no_espera_al_final():
    error = TimeoutError("Temporal")
    operacion = Mock(side_effect=error)

    with pytest.raises(TimeoutError) as capturado:
        cliente.con_reintento(operacion)

    assert capturado.value is error
    assert operacion.call_count == 3
    assert cliente.sleep.call_count == 2


@pytest.mark.parametrize("tipo_error", [ValueError, RuntimeError])
def test_reintento_no_repite_otros_errores(tipo_error):
    error = tipo_error("Error no temporal")
    operacion = Mock(side_effect=error)

    with pytest.raises(tipo_error) as capturado:
        cliente.con_reintento(operacion)

    assert capturado.value is error
    operacion.assert_called_once()
    cliente.sleep.assert_not_called()


# Pruebas de registrar_costo.
def test_registrar_costo_incluye_razonamiento_y_acumula():
    datos = datos_validos()

    primero = cliente.registrar_costo(datos)
    segundo = cliente.registrar_costo(datos)

    # 150 × 0.30 / 1.000.000 + 42 × 2.50 / 1.000.000.
    assert primero == pytest.approx(0.000150)
    assert segundo == pytest.approx(0.000150)
    assert cliente.costo_total_sesion == pytest.approx(0.000300)

    # El cálculo no debe modificar los conteos originales.
    assert datos["usageMetadata"]["candidatesTokenCount"] == 32


def test_registrar_costo_sin_datos_no_altera_total():
    cliente.costo_total_sesion = 0.000150

    assert cliente.registrar_costo({}) is None
    assert cliente.costo_total_sesion == pytest.approx(0.000150)


# Pruebas de consultar_modelo.
def test_consultar_modelo_recupera_y_registra_costo_una_vez(monkeypatch):
    datos = datos_validos()
    envio = Mock(side_effect=[
        TimeoutError("Temporal"),
        TimeoutError("Temporal"),
        datos,
    ])
    monkeypatch.setattr(cliente, "enviar_peticion", envio)

    resultado, originales = cliente.consultar_modelo(
        "Necesito reparar una llave.",
        tipos_esperados={"oficio": str, "motivo": str},
    )

    assert resultado["oficio"] == "Gasfíter"
    assert originales == datos
    assert envio.call_count == 3
    assert cliente.costo_ultima_consulta == pytest.approx(0.000150)
    assert cliente.costo_total_sesion == pytest.approx(0.000150)


def test_consultar_modelo_convierte_agotamiento_en_runtimeerror(monkeypatch):
    envio = Mock(side_effect=TimeoutError("Temporal"))
    monkeypatch.setattr(cliente, "enviar_peticion", envio)

    with pytest.raises(RuntimeError, match="tras los intentos permitidos"):
        cliente.consultar_modelo("Necesito reparar una llave.")

    assert envio.call_count == 3
    assert cliente.sleep.call_count == 2
    assert cliente.costo_ultima_consulta is None
    assert cliente.costo_total_sesion == 0


def test_consultar_modelo_propaga_valueerror_sin_reintentar(monkeypatch):
    error = ValueError("Credencial inválida")
    envio = Mock(side_effect=error)
    monkeypatch.setattr(cliente, "enviar_peticion", envio)

    with pytest.raises(ValueError) as capturado:
        cliente.consultar_modelo("Necesito reparar una llave.")

    assert capturado.value is error
    envio.assert_called_once()
    cliente.sleep.assert_not_called()
    assert cliente.costo_total_sesion == 0