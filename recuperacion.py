import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Reutiliza las rutas del proyecto sin ejecutar la indexación.
from indexar_corpus import RAIZ, DIRECTORIO_INDICE


# Instruye al modelo para responder usando el contexto y citarlo.
PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo.
Cita la fuente de cada afirmación con su número entre corchetes, como [1].
Si el contexto no alcanza para responder, dilo explícitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    """Numera los fragmentos y relaciona cada número con su fuente."""
    lineas = []
    citas = {}

    for numero, documento in enumerate(chunks_recuperados, start=1):
        fuente = documento.metadata.get("fuente", "desconocida")

        lineas.append(f"[{numero}] {documento.page_content}")
        citas[numero] = fuente

    contexto = "\n\n".join(lineas)
    return contexto, citas


def construir_prompt(pregunta, persist_directory=DIRECTORIO_INDICE, k=3):
    """Recupera los fragmentos relevantes y construye el prompt."""
    load_dotenv(RAIZ / ".env")
    clave = os.getenv("API_KEY")

    if not clave or not clave.strip():
        raise ValueError("Configura API_KEY en tu archivo .env.")

    # Usa el mismo modelo de embeddings empleado al indexar.
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=clave.strip(),
    )

    # Abre el índice existente; no vuelve a indexar el corpus.
    indice = Chroma(
        collection_name="corpus_proyecto",
        persist_directory=str(persist_directory),
        embedding_function=embeddings,
    )

    # Recupera los k fragmentos más cercanos a la pregunta.
    recuperador = indice.as_retriever(search_kwargs={"k": k})
    chunks_recuperados = recuperador.invoke(pregunta)

    # Prepara el contexto numerado y su mapa de fuentes.
    contexto, citas = formatear_contexto(chunks_recuperados)

    prompt = PROMPT_TEMPLATE.format(
        contexto=contexto,
        pregunta=pregunta,
    )

    return prompt, citas


if __name__ == "__main__":
    pregunta = input("Escribe tu pregunta sobre el proyecto: ")
    prompt, citas = construir_prompt(pregunta)

    print("\nPrompt construido:")
    print(prompt)

    print("\nMapa de citas:")
    print(citas)