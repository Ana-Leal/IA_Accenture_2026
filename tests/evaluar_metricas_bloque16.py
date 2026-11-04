# Permite localizar e importar los módulos del proyecto.
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

# Permite leer y guardar los registros JSON.
import json

# Reutiliza las funciones que acabamos de probar.
from src.metricas_texto import calcular_metricas, resumir_metricas


def main():
    # Lee las respuestas reales conservadas en el bloque 15.
    origen = (
        RAIZ
        / "docs/evidencias_bloque15/comparacion_textos.json"
    )
    registro_original = json.loads(
        origen.read_text(encoding="utf-8")
    )

    resultados = []

    for numero, caso in enumerate(
        registro_original["resultados"], start=1
    ):
        # Un intento fallido no se evalúa como una respuesta válida.
        if "error" in caso:
            print(f"Caso {numero}: omitido por error registrado.")
            continue

        # Evalúa el mismo campo de texto utilizado en el bloque 15.
        referencia = caso["referencia"]
        respuesta = caso["respuesta_json"]["resumen"]

        # Limpia ambos textos y calcula precisión, cobertura y F1.
        metricas = calcular_metricas(referencia, respuesta)

        # Conserva los textos para poder comprobar los resultados.
        resultados.append({
            "caso": numero,
            "consulta": caso["consulta"],
            "referencia": referencia,
            "respuesta": respuesta,
            **metricas,
        })

    # Incorpora las 17 consultas nuevas del bloque 17.
    from casos_bloque17 import CASOS_BLOQUE17
    from prompts.banco import BANCO_DE_PROMPTS
    from src.cliente import consultar_modelo

    # Usa el mismo prompt con el que obtuvimos las tres respuestas anteriores.
    prompt = next(
        elemento
        for elemento in BANCO_DE_PROMPTS
        if elemento["nombre"] == "resumir_necesidad"
    )

    for caso in CASOS_BLOQUE17:
        print(f"\nConsultando caso {caso['caso']}/20...", flush=True)

        # Obtiene la respuesta mediante nuestro cliente existente.
        respuesta_json, datos = consultar_modelo(
            caso["consulta"],
            system_instruction=prompt["system_instruction"],
            response_schema=prompt["response_schema"],
            tipos_esperados=prompt["tipos_esperados"],
        )

        # Compara el resumen generado con la referencia preparada.
        referencia = caso["referencia"]
        respuesta = respuesta_json["resumen"]
        metricas = calcular_metricas(referencia, respuesta)

        # Agrega el caso a la misma lista de resultados del bloque 16.
        resultados.append({
            "caso": caso["caso"],
            "consulta": caso["consulta"],
            "referencia": referencia,
            "respuesta": respuesta,
            **metricas,
        })

        print("Resumen:", respuesta, flush=True)

    # Calcula los promedios únicamente de los casos evaluados.
    promedios = resumir_metricas(resultados)

    # Ordena de menor a mayor F1 para facilitar la revisión.
    ordenados = sorted(resultados, key=lambda caso: caso["f1"])

    print("\nCaso | Precisión | Cobertura | F1")
    for caso in ordenados:
        print(
            f"{caso['caso']} | "
            f"{caso['precision']:.2%} | "
            f"{caso['cobertura']:.2%} | "
            f"{caso['f1']:.2%}"
        )

    print("\nPromedios:")
    for nombre, valor in promedios.items():
        print(f"{nombre}: {valor:.2%}")

    # Identifica el origen para no presentar estas respuestas como nuevas.
    registro = {
        "origen": origen.relative_to(RAIZ).as_posix(),
        "fecha_respuestas_bloque15_utc": registro_original["fecha_utc"],
        "prompt": registro_original["prompt"],
        "campo_evaluado": "resumen",
        "metodo": "Coincidencias de palabras con Counter",
        "resultados": ordenados,
        "promedios": promedios,
    }

    # Guarda la evidencia del bloque 16 en su propia carpeta.
    destino = (
        RAIZ
        / "docs/evidencias_bloque16/resultados_metricas.json"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nRegistro guardado en:", destino)
    print("Se evaluaron tres respuestas guardadas "
        "y 17 respuestas nuevas obtenidas de Gemini."
    )


if __name__ == "__main__":
    main()