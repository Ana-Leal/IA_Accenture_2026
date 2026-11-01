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
        "fecha_generacion_respuestas_utc": registro_original["fecha_utc"],
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
    print("Se reutilizaron respuestas guardadas; no se llamó a Gemini.")


if __name__ == "__main__":
    main()