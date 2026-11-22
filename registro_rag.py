import argparse
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

# Reutiliza las rutas, el prompt y las citas del proyecto.
from recuperacion import (
    RAIZ,
    DIRECTORIO_INDICE,
    PROMPT_TEMPLATE,
    formatear_contexto,
)


@contextmanager
def medir(tiempos, etapa):
    """Mide la duración de una etapa en segundos."""
    inicio = time.perf_counter()
    try:
        yield
    finally:
        tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta, k=3):
    """Ejecuta una consulta RAG real y registra tiempos y tokens."""
    load_dotenv(RAIZ / ".env")
    clave = os.getenv("API_KEY")

    if not clave or not clave.strip():
        raise ValueError("Configura API_KEY en tu archivo .env.")

    if not DIRECTORIO_INDICE.is_dir():
        raise ValueError("No existe el índice en vectorstore/.")

    # Usa el mismo modelo empleado al indexar el catálogo.
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=clave.strip(),
    )

    # Conserva el modelo que ya utiliza el proyecto.
    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=clave.strip(),
    )

    # Abre la colección existente sin volver a indexar documentos.
    indice = Chroma(
        collection_name="corpus_proyecto",
        persist_directory=str(DIRECTORIO_INDICE),
        embedding_function=embeddings,
        create_collection_if_not_exists=False,
    )

    tiempos = {}

    # Etapa 1: convierte la pregunta en un vector mediante la API.
    with medir(tiempos, "embed_query"):
        vector = embeddings.embed_query(pregunta)

    # Etapa 2: busca localmente usando ese mismo vector.
    with medir(tiempos, "busqueda_vectorial"):
        fragmentos = indice.similarity_search_by_vector(
            embedding=vector,
            k=k,
        )

    # Construye el contexto y conserva el mapa de fuentes.
    contexto, citas = formatear_contexto(fragmentos)
    prompt = PROMPT_TEMPLATE.format(
        contexto=contexto,
        pregunta=pregunta,
    )

    # Etapa 3: genera la respuesta mediante una llamada real.
    with medir(tiempos, "generacion"):
        respuesta = modelo.invoke(prompt)

    # Conserva los datos reales de uso; si faltan, registra null.
    tokens = (
        dict(respuesta.usage_metadata)
        if respuesta.usage_metadata
        else None
    )

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {
            etapa: round(segundos * 1000, 2)
            for etapa, segundos in tiempos.items()
        },
        # Suma las tres etapas, sin incluir la preparación inicial.
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": tokens,
    }

    return registro, respuesta.content, citas


def main():
    # Permite comparar k=3 y k=6 sin editar el archivo.
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, choices=[3, 6], default=3)
    argumentos = parser.parse_args()

    pregunta = input("Escribe tu consulta sobre oficios y servicios: ").strip()

    if not pregunta:
        raise SystemExit("Debes escribir una pregunta.")

    print("\nEjecutando consulta RAG...", flush=True)
    registro, salida, citas = registrar_consulta(
        pregunta,
        k=argumentos.k,
    )

    # Extrae el texto si el modelo devuelve una lista de bloques.
    if isinstance(salida, list):
        salida = "\n".join(
            bloque["text"]
            for bloque in salida
            if isinstance(bloque, dict)
            and bloque.get("type") == "text"
            and isinstance(bloque.get("text"), str)
        )

    print("\nRespuesta:")
    print(salida)

    print("\nMapa de citas:")
    print(citas)

    print("\nRegistro:")
    print(json.dumps(registro, ensure_ascii=False, indent=2))

    # Agrega una línea por consulta sin borrar registros anteriores.
    destino = RAIZ / "registros_latencia_costo.jsonl"
    with destino.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print("\nRegistro guardado en:", destino)


if __name__ == "__main__":
    main()