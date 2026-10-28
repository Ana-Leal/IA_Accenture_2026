# Permite localizar el proyecto e importar sus módulos.
import sys
from pathlib import Path

# Permite guardar los resultados y registrar cuándo se ejecutó la prueba.
import json
from datetime import datetime, timezone

# Permite separar las consultas para reducir errores por cuota.
from time import sleep

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

# Reutiliza el banco de prompts y las funciones existentes.
from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

MODELO = "gemini-3.5-flash-lite"
REPETICIONES = 3
ARCHIVO_RESULTADOS = RAIZ / "prompts" / "registro_resultados.json"


# Guarda el progreso después de cada intento, incluso si hubo un fallo.
def guardar_registro(registro):
    ARCHIVO_RESULTADOS.write_text(
        json.dumps(registro, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# Ejecuta tres consultas reales por prompt y valida las respuestas.
def main():
    registro = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo": MODELO,
        "repeticiones_por_prompt": REPETICIONES,
        "ejecucion_completa": False,
        "resultados": {},
    }

    # Conserva una copia del registro anterior si se repite la prueba.
    if ARCHIVO_RESULTADOS.exists():
        marca = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        respaldo = ARCHIVO_RESULTADOS.with_name(f"registro_resultados_{marca}.json")
        respaldo.write_bytes(ARCHIVO_RESULTADOS.read_bytes())
        print("Registro anterior conservado en:", respaldo.name, flush=True)

    total = len(BANCO_DE_PROMPTS) * REPETICIONES
    realizados = 0
    print(f"Se realizarán {total} consultas reales a {MODELO}.", flush=True)

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]
        resultado = {
            "entrada": prompt["ejemplo_usuario"],
            "system_instruction": prompt["system_instruction"],
            "response_schema": prompt["response_schema"],
            "intentos": 0,
            "exitos": 0,
            "fallos": 0,
            "detalle": [],
        }
        registro["resultados"][nombre] = resultado
        print(f"\nPROMPT: {nombre}", flush=True)

        for numero in range(1, REPETICIONES + 1):
            print(f"Intento {numero}/{REPETICIONES}...", flush=True)
            detalle = {"intento": numero, "valido": False}

            try:
                # Mantiene separadas las instrucciones y la entrada del usuario.
                url, headers, body = armar_peticion(
                    prompt["ejemplo_usuario"],
                    modelo=MODELO,
                    system_instruction=prompt["system_instruction"],
                    response_schema=prompt["response_schema"],
                )
                respuesta = enviar_peticion(url, headers, body)
                texto = extraer_texto(respuesta)
                detalle["texto_recibido"] = texto

                # Valida JSON, campos obligatorios y tipos de datos.
                datos = parsear_respuesta_json(texto, prompt["tipos_esperados"])
                detalle["valido"] = True
                detalle["respuesta_json"] = datos
                resultado["exitos"] += 1
                print("CORRECTO: JSON con las claves y tipos esperados.", flush=True)

            except (ValueError, RuntimeError, TypeError, TimeoutError) as error:
                # Cuenta el fallo y continúa con las consultas restantes.
                detalle["error"] = str(error)
                resultado["fallos"] += 1
                print("FALLO:", error, flush=True)

            resultado["intentos"] += 1
            resultado["detalle"].append(detalle)
            guardar_registro(registro)
            realizados += 1

            # Espera entre consultas, salvo después de la última.
            if realizados < total:
                sleep(2)

        print(
            f"Resultado: {resultado['exitos']}/{REPETICIONES} respuestas válidas.",
            flush=True,
        )

    # Completa la ejecución aunque alguna consulta haya fallado.
    registro["ejecucion_completa"] = True
    guardar_registro(registro)
    print("\nRegistro guardado en prompts/registro_resultados.json", flush=True)
    print("Revisa también el contenido de las respuestas: JSON válido no garantiza calidad.")


# Ejecuta las consultas solamente al iniciar este archivo directamente.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrueba interrumpida. Se conserva el registro de los intentos terminados.")
        sys.exit(130)
