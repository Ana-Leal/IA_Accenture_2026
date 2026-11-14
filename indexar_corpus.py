import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# Localiza la raíz del proyecto y la carpeta del índice.
RAIZ = Path(__file__).resolve().parent
DIRECTORIO_INDICE = RAIZ / "vectorstore"

# Cinco documentos cortos sobre nuestra aplicación.
CORPUS = [
    (
        "El cliente modular realiza hasta tres intentos ante errores "
        "temporales. Entre intentos aplica una espera creciente, "
        "con variación aleatoria y un límite máximo."
    ),
    (
        "Las credenciales ausentes o inválidas se informan sin reintentar. "
        "El cliente reconoce HTTP 401, HTTP 403 y HTTP 400 "
        "cuando el motivo es API_KEY_INVALID."
    ),
    (
        "El costo estimado utiliza los tokens de entrada, respuesta "
        "y razonamiento, con tarifas de referencia. Los costos conocidos "
        "se acumulan mientras el programa está en ejecución."
    ),
    (
        "El agente dispone de dos herramientas: consultar_oficio consulta "
        "un catálogo de oficios y calcular_superficie multiplica el ancho "
        "por el alto de una pared rectangular."
    ),
    (
        "Las pruebas unitarias del cliente simulan peticiones y esperas. "
        "Comprueban los reintentos, los errores de credenciales "
        "y el cálculo de costos sin realizar llamadas reales a Gemini."
    ),
]


def main():
    # Carga la misma credencial que ya utiliza el proyecto.
    load_dotenv(RAIZ / ".env")
    clave = os.getenv("API_KEY")

    if not clave or not clave.strip():
        raise SystemExit("Configura API_KEY en tu archivo .env.")

    # El corte recursivo intenta respetar párrafos y palabras.
    # El solapamiento conserva contexto entre fragmentos contiguos.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
    )
    chunks = splitter.create_documents(CORPUS)

    print(f"Documentos: {len(CORPUS)}")
    print(f"Fragmentos generados: {len(chunks)}")

    # Utiliza el modelo de embeddings indicado en el curso.
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=clave.strip(),
    )

    # Genera embeddings reales y guarda los fragmentos en disco.
    try:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="corpus_proyecto",
            persist_directory=str(DIRECTORIO_INDICE),
        )
    except Exception as error:
        print("No se pudo completar la indexación:", type(error).__name__)
        raise SystemExit(1) from None

    print("Fragmentos guardados:", vectorstore._collection.count())
    print("Índice guardado en:", DIRECTORIO_INDICE)


if __name__ == "__main__":
    main()