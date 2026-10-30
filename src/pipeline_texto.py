import re
def limpiar_texto(texto: str) -> str:
    """Normaliza mayúsculas, puntuación y espacios."""
    # Rechaza valores que no sean texto.
    if not isinstance(texto, str):
        raise TypeError("limpiar_texto espera un texto.")

    texto = texto.lower()  # Convierte a minúsculas.

    # Elimina puntuación y símbolos; conserva tildes, ñ y números.
    texto = re.sub(r"[^\w\s]", "", texto)

    # Reduce espacios repetidos y elimina los de los extremos.
    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto_limpio: str) -> list[str]:
    """Separa el texto limpio en palabras."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Aplica la limpieza y después la tokenización."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)