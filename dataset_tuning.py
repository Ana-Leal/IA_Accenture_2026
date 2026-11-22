import json
from collections import Counter
from google.genai import types


# Cada ejemplo contiene:
# 1. La solicitud escrita por el usuario.
# 2. El JSON exacto que esperamos como respuesta.
#
# El resumen conserva el trabajo y sus condiciones.
# El lugar se toma de la solicitud, sin inventarlo.
# Si no se menciona, utilizamos "no indicado".
ejemplos_raw = [
    (
        "La llave del lavaplatos de la cocina gotea. Necesito repararla.",
        {
            "resumen": "Reparar la llave del lavaplatos que gotea.",
            "lugar": "cocina",
        },
    ),
    (
        "Quiero instalar dos repisas de madera en la cocina.",
        {
            "resumen": "Instalar dos repisas de madera.",
            "lugar": "cocina",
        },
    ),
    (
        "El lavamanos del baño está tapado. Necesito destaparlo.",
        {
            "resumen": "Destapar el lavamanos.",
            "lugar": "baño",
        },
    ),
    (
        "Necesito reparar la puerta del baño, pero sin reemplazarla.",
        {
            "resumen": "Reparar la puerta sin reemplazarla.",
            "lugar": "baño",
        },
    ),
    (
        "Quiero pintar solo una pared del dormitorio, no las cuatro.",
        {
            "resumen": "Pintar solo una pared, no las cuatro.",
            "lugar": "dormitorio",
        },
    ),
    (
        "Necesito armar un escritorio en el dormitorio.",
        {
            "resumen": "Armar un escritorio.",
            "lugar": "dormitorio",
        },
    ),
    (
        "Quiero cambiar tres enchufes del living.",
        {
            "resumen": "Cambiar tres enchufes.",
            "lugar": "living",
        },
    ),
    (
        "Necesito lijar y barnizar una mesa de madera en el living.",
        {
            "resumen": "Lijar y barnizar una mesa de madera.",
            "lugar": "living",
        },
    ),
    (
        "Necesito que revisen una mancha de humedad. No sé qué la causa.",
        {
            "resumen": "Revisar una mancha de humedad de causa desconocida.",
            "lugar": "no indicado",
        },
    ),
    (
        "Quiero fabricar un mueble de madera a medida.",
        {
            "resumen": "Fabricar un mueble de madera a medida.",
            "lugar": "no indicado",
        },
    ),
]


# Convierte cada solicitud y su respuesta al tipo utilizado por el curso.
# json.dumps transforma el diccionario en un texto JSON válido.
examples = [
    types.TuningExample(
        text_input=texto,
        output=json.dumps(salida, ensure_ascii=False),
    )
    for texto, salida in ejemplos_raw
]

def chequear_balance(ejemplos_raw: list[tuple[str, dict]], clave: str) -> Counter:
    """Cuenta cuántos ejemplos contienen cada valor del campo elegido."""
    return Counter(salida[clave] for _, salida in ejemplos_raw)

def validar_dataset(
    examples: list[types.TuningExample],
    claves_esperadas: tuple[str, ...],
) -> list[str]:
    """Detecta entradas vacías, duplicados y problemas en el JSON."""
    problemas = []
    vistos = set()

    for numero, ejemplo in enumerate(examples, start=1):
        # Comprueba que la solicitud tenga texto.
        entrada = ejemplo.text_input or ""

        if not entrada.strip():
            problemas.append(f"Ejemplo {numero}: entrada vacía.")

        # Detecta solicitudes repetidas.
        if entrada in vistos:
            problemas.append(f"Ejemplo {numero}: entrada duplicada.")
        vistos.add(entrada)

        # Comprueba que exista una respuesta esperada.
        if not ejemplo.output or not ejemplo.output.strip():
            problemas.append(f"Ejemplo {numero}: salida vacía.")
            continue

        # Comprueba que la respuesta sea JSON válido.
        try:
            salida = json.loads(ejemplo.output)
        except json.JSONDecodeError:
            problemas.append(f"Ejemplo {numero}: salida no es JSON válido.")
            continue

        # Nuestro formato exige un objeto con campos.
        if not isinstance(salida, dict):
            problemas.append(f"Ejemplo {numero}: la salida no es un objeto JSON.")
            continue

        # Comprueba que estén los campos requeridos.
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(
                    f"Ejemplo {numero}: falta el campo '{clave}'."
                )

    return problemas

if __name__ == "__main__":
    print(f"{len(examples)} ejemplos construidos")
    print("\nPrimera entrada:")
    print(examples[0].text_input)
    print("\nSalida esperada:")
    print(examples[0].output)

    print("\nEjemplos por lugar:")
    balance = chequear_balance(ejemplos_raw, "lugar")

    for lugar, cantidad in balance.most_common():
        print(f"{lugar}: {cantidad}")

    # Fuera del for: valida una sola vez el dataset completo.
    print("\nValidación del dataset:")
    problemas = validar_dataset(
        examples,
        claves_esperadas=("resumen", "lugar"),
    )

    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")

    for problema in problemas:
        print("-", problema)
        # Crea una lista de prueba sin modificar los diez ejemplos originales.
    examples_rotos = examples + [
        # Entrada vacía y salida sin el campo "lugar".
        types.TuningExample(
            text_input="",
            output='{"resumen": "Reparar una puerta."}',
        ),
        # Entrada repetida y salida que no es JSON.
        types.TuningExample(
            text_input=examples[0].text_input,
            output="Esto no es JSON",
        ),
    ]

    print("\nPrueba con errores intencionales:")
    problemas_prueba = validar_dataset(
        examples_rotos,
        claves_esperadas=("resumen", "lugar"),
    )

    for problema in problemas_prueba:
        print("-", problema)

    # Verifica que detecte exactamente los cuatro errores introducidos.
    assert problemas_prueba == [
        "Ejemplo 11: entrada vacía.",
        "Ejemplo 11: falta el campo 'lugar'.",
        "Ejemplo 12: entrada duplicada.",
        "Ejemplo 12: salida no es JSON válido.",
    ], problemas_prueba

    print("CORRECTO: el validador detectó los cuatro errores esperados.")