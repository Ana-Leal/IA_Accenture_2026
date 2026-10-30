# Permite importar los módulos desde la raíz del proyecto.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from datetime import datetime, timezone

from prompts.banco import BANCO_DE_PROMPTS
from src.cliente import consultar_modelo
from src.pipeline_texto import procesar_texto


# Las referencias se definen antes de consultar al modelo.
CASOS = [
    {
        "consulta": "Necesito reparar la llave del lavaplatos que gotea.",
        "referencia": "Reparar la llave del lavaplatos que gotea.",
    },
    {
        "consulta": (
            "Necesito fabricar e instalar un mueble de madera "
            "a medida para mi dormitorio."
        ),
        "referencia": "Fabricar e instalar un mueble de madera a medida.",
    },
    {
        "consulta": (
            "Necesito pintar las paredes del living "
            "porque la pintura está desgastada."
        ),
        "referencia": "Pintar las paredes del living.",
    },
]


def calcular_coincidencia(referencia, respuesta):
    """Calcula la proporción de palabras únicas compartidas."""
    palabras_referencia = set(referencia)
    palabras_respuesta = set(respuesta)

    # Evita dividir por cero cuando no hay palabras de referencia.
    if not palabras_referencia:
        return 0.0

    comunes = palabras_referencia & palabras_respuesta
    return len(comunes) / len(palabras_referencia)


def main():
    prompt = next(
        elemento
        for elemento in BANCO_DE_PROMPTS
        if elemento["nombre"] == "resumir_necesidad"
    )

    registro = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt["nombre"],
        "campo_evaluado": "resumen",
        "resultados": [],
    }

    for numero, caso in enumerate(CASOS, start=1):
        print(f"\nCASO {numero}/3", flush=True)
        entrada = dict(caso)

        try:
            resultado, datos = consultar_modelo(
                caso["consulta"],
                system_instruction=prompt["system_instruction"],
                response_schema=prompt["response_schema"],
                tipos_esperados=prompt["tipos_esperados"],
            )

            # Evalúa el resumen, no el diccionario JSON completo.
            respuesta = resultado["resumen"]
            referencia = caso["referencia"]

            crudo = calcular_coincidencia(
                referencia.split(), respuesta.split()
            )
            procesado = calcular_coincidencia(
                procesar_texto(referencia),
                procesar_texto(respuesta),
            )

            entrada.update({
                "respuesta_json": resultado,
                "coincidencia_cruda": crudo,
                "coincidencia_procesada": procesado,
            })

            print("Referencia:", referencia)
            print("Resumen generado:", respuesta)
            print(f"Coincidencia sin limpiar: {crudo:.1%}")
            print(f"Coincidencia tras procesar: {procesado:.1%}")

        except (ValueError, RuntimeError) as error:
            entrada["error"] = str(error)
            print("Consulta fallida:", error)

        registro["resultados"].append(entrada)

    # Guarda las respuestas y las métricas como evidencia.
    destino = (
        Path(__file__).resolve().parents[1]
        / "docs/evidencias_bloque15/comparacion_textos.json"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nRegistro guardado en:", destino)


if __name__ == "__main__":
    main()