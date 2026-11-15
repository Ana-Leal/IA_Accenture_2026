import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# Localiza la raíz del proyecto y la carpeta del índice.
RAIZ = Path(__file__).resolve().parent
DIRECTORIO_INDICE = RAIZ / "vectorstore"


# Corpus técnico anterior, conservado como referencia.
# CORPUS = [
#     (
#         "El cliente modular realiza hasta tres intentos ante errores "
#         "temporales. Entre intentos aplica una espera creciente, "
#         "con variación aleatoria y un límite máximo."
#     ),
#     (
#         "Las credenciales ausentes o inválidas se informan sin reintentar. "
#         "El cliente reconoce HTTP 401, HTTP 403 y HTTP 400 "
#         "cuando el motivo es API_KEY_INVALID."
#     ),
#     (
#         "El costo estimado utiliza los tokens de entrada, respuesta "
#         "y razonamiento, con tarifas de referencia. Los costos conocidos "
#         "se acumulan mientras el programa está en ejecución."
#     ),
#     (
#         "El agente dispone de dos herramientas: consultar_oficio consulta "
#         "un catálogo de oficios y calcular_superficie multiplica el ancho "
#         "por el alto de una pared rectangular."
#     ),
#     (
#         "Las pruebas unitarias del cliente simulan peticiones y esperas. "
#         "Comprueban los reintentos, los errores de credenciales "
#         "y el cálculo de costos sin realizar llamadas reales a Gemini."
#     ),
# ]


# Corpus de oficios anterior, conservado como referencia.
# Ahora la información se obtiene desde el archivo Markdown.
# CORPUS = [
#     (
#         "El gasfíter atiende problemas de grifería, tuberías y desagües, "
#         "como una llave que gotea o un lavamanos tapado."
#     ),
#     (
#         "El carpintero fabrica y repara muebles y elementos de madera, "
#         "como mesas, repisas y puertas de madera que necesitan ajustes."
#     ),
#     (
#         "El electricista revisa y repara instalaciones eléctricas. "
#         "Puede atender solicitudes relacionadas con enchufes "
#         "e instalación de luminarias."
#     ),
#     (
#         "El pintor prepara y pinta paredes y cielos. Si hay humedad "
#         "de origen desconocido, primero se necesita evaluar su causa "
#         "antes de decidir pintar."
#     ),
#     (
#         "Si una solicitud no permite identificar el oficio, se pide "
#         "una aclaración. Este catálogo no incluye precios, "
#         "disponibilidad ni datos de trabajadores."
#     ),
# ]

# Fuente anterior, conservada como referencia.
# METADATAS = [
#     {"fuente": "indexar_corpus.py"}
#     for _ in CORPUS
# ]


# Lee el catálogo de oficios y servicios desde el Markdown.
ARCHIVO_CORPUS = RAIZ / "docs" / "catalogo_servicios.md"
texto_catalogo = ARCHIVO_CORPUS.read_text(encoding="utf-8-sig")

# Cada sección de nivel 2 representa un documento.
# La introducción anterior a la primera sección no se indexa.
CORPUS = [
    "## " + seccion.strip()
    for seccion in texto_catalogo.split("\n## ")[1:]
    if seccion.strip()
]

# Identifica el Markdown como fuente de cada documento.
METADATAS = [
    {"fuente": ARCHIVO_CORPUS.relative_to(RAIZ).as_posix()}
    for _ in CORPUS
]


def main():
    # Carga la misma credencial que ya utiliza el proyecto.
    load_dotenv(RAIZ / ".env")
    clave = os.getenv("API_KEY")

    if not clave or not clave.strip():
        raise SystemExit("Configura API_KEY en tu archivo .env.")

    if not CORPUS:
        raise SystemExit(
            "El catálogo debe contener secciones con encabezados '## '."
        )

    # Divide los documentos respetando párrafos y palabras.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
    )

    # Bloque 24: versión anterior sin fuentes.
    # chunks = splitter.create_documents(CORPUS)

    # Conserva la fuente de cada documento en sus fragmentos.
    chunks = splitter.create_documents(
        CORPUS,
        metadatas=METADATAS,
    )

    # Asigna un identificador predecible a cada fragmento.
    ids = [f"doc{i}" for i in range(len(chunks))]

    print(f"Documentos: {len(CORPUS)}")
    print(f"Fragmentos generados: {len(chunks)}")

    # Usa el mismo modelo de embeddings que la recuperación.
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=clave.strip(),
    )

    # Genera embeddings reales y guarda los fragmentos en disco.
    try:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            ids=ids,
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