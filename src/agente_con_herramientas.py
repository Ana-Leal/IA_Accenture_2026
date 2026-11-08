import os
from math import isfinite

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
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
@tool
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
        ("human", "{entrada}"),
        # LangChain coloca aquí las acciones y resultados intermedios.
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

    ejecutor = construir_agente(modelo)
    entrada = input("Escribe tu consulta: ")

    resultado = ejecutor.invoke({"entrada": entrada})

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