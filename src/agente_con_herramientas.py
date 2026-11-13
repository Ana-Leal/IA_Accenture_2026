import os
from math import isfinite
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
# Bloque 22: guarda los mensajes de cada conversación.
from langchain_core.chat_history import InMemoryChatMessageHistory
# Bloque 23: permite guardar registros JSON con fecha y hora.
import json
from datetime import datetime, timezone
# Conecta el historial con el agente.
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
# Herramienta 1: consulta información definida en nuestro catálogo.
@tool
def consultar_oficio(oficio: str) -> str:
    """Consulta qué trabajos atiende un oficio del catálogo.
    Úsala cuando se necesite información sobre gasfíter,
    carpintero, electricista o pintor.
    """
    catalogo = {
        "gasfíter": "Atiende problemas de grifería, tuberías y desagües.",
        "carpintero": "Fabrica y repara muebles y elementos de madera.",
        "electricista": "Revisa y repara instalaciones eléctricas.",
        "pintor": "Prepara y pinta superficies como paredes y cielos.",
    }

    nombre = oficio.strip().lower()

    # Reconoce nombres equivalentes para consultar la misma entrada.
    equivalencias = {
        "gasfiter": "gasfíter",
        "plomero": "gasfíter",
        "fontanero": "gasfíter",
    }
    nombre = equivalencias.get(nombre, nombre)

    return catalogo.get(
        nombre,
        "Ese oficio no está registrado en el catálogo.",
    )


# Herramienta 2: realiza un cálculo con las medidas proporcionadas.
# Bloque 21: conservamos el decorador anterior como referencia.
# @tool
# Bloque 22: describe cada medida que recibe la herramienta.
class ArgumentosSuperficie(BaseModel):
    ancho: float = Field(
        description="Ancho de la pared rectangular en metros."
    )
    alto: float = Field(
        description="Alto de la pared rectangular en metros."
    )


@tool(args_schema=ArgumentosSuperficie)

def calcular_superficie(ancho: float, alto: float) -> str:
    """Calcula la superficie de una pared rectangular en metros cuadrados.
    Úsala cuando el usuario proporcione ancho y alto en metros.
    Calcula la superficie completa, sin descontar puertas ni ventanas.
    """
    if not isfinite(ancho) or not isfinite(alto):
        return "Las medidas deben ser números finitos."

    if ancho <= 0 or alto <= 0:
        return "El ancho y el alto deben ser mayores que cero."

    superficie = ancho * alto

    if not isfinite(superficie):
        return "Las medidas son demasiado grandes para realizar el cálculo."

    return f"La superficie completa es de {superficie:.2f} m²."


# Prepara el agente con las dos herramientas disponibles.
def construir_agente(modelo):
    herramientas = [consultar_oficio, calcular_superficie]
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente sobre oficios y servicios en Chile. "
            "Usa consultar_oficio para consultar el catálogo de oficios. "
            "Usa calcular_superficie para calcular superficies de paredes. "
            "Si faltan medidas, solicítalas; no las inventes. "
            "No inventes precios, disponibilidad ni nombres de trabajadores. "
            "Responde brevemente y utiliza las herramientas cuando corresponda.",
        ),

        # Bloque 21: estructura anterior, conservada como referencia.
        # ("human", "{entrada}"),
        # MessagesPlaceholder("agent_scratchpad"),

        # Bloque 22: historial de las interacciones anteriores.
        MessagesPlaceholder("chat_history"),

        # Mensaje actual del usuario.
        ("human", "{entrada}"),

        # Acciones y resultados de la interacción actual.
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(
        modelo,
        herramientas,
        prompt,
    )

    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        return_intermediate_steps=True,
    )
# Bloque 22: conserva las conversaciones mientras el programa está abierto.
historiales = {}


def obtener_historial(session_id: str):
    # Crea un historial vacío cuando la sesión todavía no existe.
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()

    # Devuelve únicamente el historial de la sesión solicitada.
    return historiales[session_id]

# Convierte los bloques de Gemini en texto antes de guardar el historial.
def normalizar_respuesta(resultado):
    salida = resultado["output"]

    if isinstance(salida, list):
        salida = "\n".join(
            bloque["text"]
            for bloque in salida
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        )

    # Conserva los demás datos, incluidas las herramientas utilizadas.
    return {**resultado, "output": salida}


# Conecta el agente existente con el historial de cada sesión.
def construir_agente_con_memoria(modelo):
    ejecutor = construir_agente(modelo)
    agente_normalizado = ejecutor | RunnableLambda(normalizar_respuesta)

    return RunnableWithMessageHistory(
        agente_normalizado,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )

# Bloque 23: guarda una interacción del agente para revisarla después.
def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
) -> None:
    """Agrega una interacción al archivo trazas_agente.jsonl."""
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get(
                "intermediate_steps", []
            )
        ],
        # Nuestro agente ya devuelve la respuesta normalizada como texto.
        "respuesta_final": resultado["output"],
    }

    # El modo "a" agrega registros sin borrar los anteriores.
    with open("trazas_agente.jsonl", "a", encoding="utf-8") as archivo:
        archivo.write(
            json.dumps(registro, ensure_ascii=False) + "\n"
        )


def main():
    # Reutiliza API_KEY del archivo .env del proyecto.
    load_dotenv()
    clave = os.getenv("API_KEY")

    if not clave or not clave.strip():
        raise ValueError("Configura API_KEY en tu archivo .env.")

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=clave.strip(),
    )
    # Bloque 21: agente sin memoria.
    #ejecutor = construir_agente(modelo)
    #entrada = input("Escribe tu consulta: ")
    #resultado = ejecutor.invoke({"entrada": entrada})
    # Bloque 22: agente con historial por sesión.
    ejecutor = construir_agente_con_memoria(modelo)
    config = {"configurable": {"session_id": "sesion_1"}}

    entrada = input("Escribe tu consulta: ")

    # Bloque 21: consulta independiente.
    # resultado = ejecutor.invoke({"entrada": entrada})

    # Bloque 22: consulta asociada a una sesión.
    resultado = ejecutor.invoke({"entrada": entrada}, config)
    # Guarda la consulta, las herramientas utilizadas y la respuesta.
    registrar_traza(
        session_id=config["configurable"]["session_id"],
        entrada=entrada,
        resultado=resultado,
    )
    print("\nRespuesta:")
    salida = resultado["output"]

    # Extrae el texto cuando la respuesta llega como bloques.
    if isinstance(salida, list):
        salida = "\n".join(
            bloque["text"]
            for bloque in salida
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        )

    print(salida)

    # Muestra qué herramienta eligió el agente.
    print("\nHerramientas utilizadas:")
    if not resultado["intermediate_steps"]:
        print("No se utilizaron herramientas.")

    for accion, observacion in resultado["intermediate_steps"]:
        print("Herramienta:", accion.tool)
        print("Argumentos:", accion.tool_input)
        print("Resultado:", observacion)


if __name__ == "__main__":
    main()