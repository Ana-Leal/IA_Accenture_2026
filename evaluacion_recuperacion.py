# Casos del bloque 27 adaptados al catálogo de oficios y servicios.
# Las etiquetas se definieron leyendo los fragmentos del índice,
# antes de consultar al recuperador.

CASOS_EVALUACION = [
    {
        "pregunta": "La llave del lavaplatos gotea. ¿Qué oficio atiende la grifería?",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "Necesito reparar un mueble de madera. ¿A qué oficio corresponde?",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "¿Quién puede revisar y reparar la instalación eléctrica?",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "Quiero preparar y pintar las paredes y el cielo. ¿Qué oficio necesito?",
        "ids_relevantes": {"doc3"},
    },
    {
        "pregunta": "Necesito reparar una tubería y un mueble de madera. ¿Qué oficios atienden esos trabajos?",
        "ids_relevantes": {"doc0", "doc1"},
    },
    {
        "pregunta": "¿La aplicación orienta sobre el trabajador que necesito y pide aclaraciones si mi descripción es insuficiente?",
        "ids_relevantes": {"doc4", "doc5"},
    },
    {
        "pregunta": "¿El catálogo contiene precios y disponibilidad de trabajadores? ¿Qué debe hacer la aplicación si no tiene información para responder?",
        "ids_relevantes": {"doc6", "doc7"},
    },
           {
        "pregunta": "¿Cuál es la capital de Noruega?",
        "ids_relevantes": set(),
    },
]

import argparse
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from indexar_corpus import RAIZ, DIRECTORIO_INDICE


def precision_at_k(ids_recuperados, ids_relevantes):
    """Calcula qué proporción de los fragmentos recuperados es pertinente."""
    if not ids_recuperados:
        return 0.0

    acertados = set(ids_recuperados) & ids_relevantes
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """Calcula qué proporción de los fragmentos pertinentes se recuperó."""
    if not ids_relevantes:
        # No hay respuesta en el corpus: recall no aplicable.
        return None

    acertados = set(ids_recuperados) & ids_relevantes
    return len(acertados) / len(ids_relevantes)


def promediar(valores):
    """Excluye los valores no aplicables del promedio."""
    validos = [valor for valor in valores if valor is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(recuperador, casos):
    """Ejecuta las preguntas y compara los ids con las etiquetas previas."""
    resultados = []

    for numero, caso in enumerate(casos, start=1):
        print(f"Evaluando pregunta {numero}/{len(casos)}...", flush=True)

        fragmentos = recuperador.invoke(caso["pregunta"])
        ids_recuperados = [fragmento.id for fragmento in fragmentos]

        if any(identificador is None for identificador in ids_recuperados):
            raise ValueError("Un fragmento recuperado no tiene identificador.")

        resultados.append({
            "pregunta": caso["pregunta"],
            "ids_recuperados": ids_recuperados,
            "ids_relevantes": sorted(caso["ids_relevantes"]),
            "precision": precision_at_k(
                ids_recuperados, caso["ids_relevantes"]
            ),
            "recall": recall_at_k(
                ids_recuperados, caso["ids_relevantes"]
            ),
        })

    precision_promedio = promediar(
        resultado["precision"] for resultado in resultados
    )
    recall_promedio = promediar(
        resultado["recall"] for resultado in resultados
    )

    return resultados, precision_promedio, recall_promedio


def main():
    # Permite comparar k=3 y k=5 sin editar el código.
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--k", type=int, choices=[3, 5], default=3)
    k = argumentos.parse_args().k

    load_dotenv(RAIZ / ".env")
    clave = os.getenv("API_KEY")

    if not clave or not clave.strip():
        raise ValueError("Configura API_KEY en tu archivo .env.")

    if not DIRECTORIO_INDICE.exists():
        raise ValueError("No se encuentra el índice del catálogo.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=clave.strip(),
    )

    # Abre el índice existente; no vuelve a indexar.
    indice = Chroma(
        collection_name="corpus_proyecto",
        persist_directory=str(DIRECTORIO_INDICE),
        embedding_function=embeddings,
    )

    # Comprueba que las etiquetas correspondan a ids del índice.
    ids_existentes = set(indice.get()["ids"])
    if not ids_existentes:
        raise ValueError("El índice está vacío.")

    for caso in CASOS_EVALUACION:
        if not caso["ids_relevantes"].issubset(ids_existentes):
            raise ValueError(
                f"Hay etiquetas que no existen en el índice: {caso['pregunta']}"
            )

    recuperador = indice.as_retriever(search_kwargs={"k": k})

    resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
        recuperador, CASOS_EVALUACION
    )

    ahora = datetime.now()
    lineas = [
        f"Fecha: {ahora.isoformat(timespec='seconds')}",
        f"Configuracion: k={k}, chunk_size=200, chunk_overlap=30",
        "Corpus: docs/catalogo_servicios.md",
        "",
        "Precision | Recall | Pregunta",
    ]

    for resultado in resultados:
        recall = resultado["recall"]
        recall_texto = "n/a" if recall is None else f"{recall:.3f}"

        lineas.append(
            f"{resultado['precision']:.3f} | "
            f"{recall_texto} | {resultado['pregunta']}"
        )
        lineas.append(
            f"  Recuperados: {resultado['ids_recuperados']}"
        )
        lineas.append(
            f"  Relevantes: {resultado['ids_relevantes']}"
        )

    lineas.append(
        f"\nPromedios: precision={precision_promedio:.3f}, "
        f"recall={recall_promedio:.3f}"
    )

    contenido = "\n".join(lineas) + "\n"
    print("\n" + contenido)

    # Conserva el primer registro y guarda las siguientes corridas aparte.
    destino = RAIZ / "resultados_evaluacion.txt"
    if destino.exists():
        fecha_archivo = ahora.strftime("%Y%m%d_%H%M%S_%f")
        destino = RAIZ / f"resultados_evaluacion_{fecha_archivo}_k{k}.txt"

    with destino.open("x", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print("Resultados guardados en:", destino)


if __name__ == "__main__":
    main()