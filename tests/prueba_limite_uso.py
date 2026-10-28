# Comprueba el comportamiento del cliente con consultas reales.
import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import cliente, consumir_gemini


def main():
    # Conserva las funciones reales: no se simulan peticiones ni esperas.
    post_real = consumir_gemini.requests.post
    sleep_real = cliente.sleep

    registro = {
        "fecha": datetime.now().astimezone().isoformat(),
        "consultas_planificadas": 10,
        "consultas": [],
    }

    cliente.costo_total_sesion = 0.0

    for numero in range(1, 11):
        detalle = {
            "consulta": numero,
            "estados_http": [],
            "esperas_segundos": [],
        }

        # Registra el estado de cada respuesta HTTP sin guardar credenciales.
        def enviar_y_registrar(*args, **kwargs):
            respuesta = post_real(*args, **kwargs)
            detalle["estados_http"].append(respuesta.status_code)
            print(f"Estado HTTP: {respuesta.status_code}", flush=True)
            return respuesta

        # Registra y realiza las esperas solicitadas por el cliente.
        def esperar_y_registrar(segundos):
            detalle["esperas_segundos"].append(segundos)
            sleep_real(segundos)

        print(f"\nCONSULTA {numero}/10", flush=True)

        with patch(
            "src.consumir_gemini.requests.post",
            side_effect=enviar_y_registrar,
        ) as envio, patch(
            "src.cliente.sleep",
            side_effect=esperar_y_registrar,
        ):
            try:
                resultado, datos = cliente.consultar_modelo(
                    "Responde solamente: OK."
                )
                detalle["resultado"] = "correcto"
                print("Respuesta recibida.", flush=True)

            except (ValueError, RuntimeError) as error:
                detalle["resultado"] = "fallido"
                detalle["error"] = str(error)
                print("Consulta fallida:", error, flush=True)

            detalle["intentos"] = envio.call_count

        detalle["costo_estimado_usd"] = cliente.costo_ultima_consulta
        registro["consultas"].append(detalle)
        registro["costo_acumulado_conocido_usd"] = cliente.costo_total_sesion

        # Guarda el progreso después de cada consulta.
        ruta = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "evidencias_bloque13"
            / "prueba_limite_uso.json"
        )
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(
            json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # Una credencial incorrecta no se resuelve enviando más consultas.
        if detalle.get("resultado") == "fallido" and (
            "Credencial" in detalle.get("error", "")
            or "credencial" in detalle.get("error", "")
        ):
            print("Prueba detenida por un problema de credenciales.")
            break

    consultas_con_429 = [
        detalle["consulta"]
        for detalle in registro["consultas"]
        if 429 in detalle["estados_http"]
    ]

    print("\nConsultas realizadas:", len(registro["consultas"]))
    print(
        "Intentos de envío:",
        sum(detalle["intentos"] for detalle in registro["consultas"]),
    )
    if consultas_con_429:
        print("Primer HTTP 429 en la consulta:", consultas_con_429[0])
    else:
        print("No se observó HTTP 429 durante esta ejecución.")

    print(
        "Costo acumulado conocido: "
        f"USD {cliente.costo_total_sesion:.8f}"
    )
    print("Excluye consumos cuyos datos de uso no se recibieron.")
    print("Registro guardado en:", ruta)


if __name__ == "__main__":
    main()