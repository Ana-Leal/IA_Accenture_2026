# Cuenta cuántas veces aparece cada palabra.
from collections import Counter

# Reutiliza la limpieza y tokenización del bloque 15.
from src.pipeline_texto import procesar_texto


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las palabras compartidas considerando repeticiones."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)

    # Toma la menor cantidad de cada palabra entre ambos textos.
    coincidencias = conteo_referencia & conteo_respuesta
    return sum(coincidencias.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 sobre palabras."""
    # Evita divisiones por cero cuando alguno de los textos está vacío.
    if not tokens_referencia or not tokens_respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(
        tokens_referencia,
        tokens_respuesta,
    )

    # Cuánto de lo respondido coincide con la referencia.
    precision = coincidencias / len(tokens_respuesta)

    # Cuánto de la referencia aparece en la respuesta.
    cobertura = coincidencias / len(tokens_referencia)

    # Combina ambas métricas mediante la media armónica.
    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }


def calcular_metricas(
    texto_referencia: str,
    texto_respuesta: str,
) -> dict[str, float]:
    """Limpia y tokeniza ambos textos antes de compararlos."""
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)

    return calcular_precision_cobertura_f1(
        tokens_referencia,
        tokens_respuesta,
    )


def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Calcula el promedio de cada métrica de los casos evaluados."""
    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }

    cantidad = len(resultados)

    return {
        "precision_promedio": sum(
            caso["precision"] for caso in resultados
        ) / cantidad,
        "cobertura_promedio": sum(
            caso["cobertura"] for caso in resultados
        ) / cantidad,
        "f1_promedio": sum(
            caso["f1"] for caso in resultados
        ) / cantidad,
    }