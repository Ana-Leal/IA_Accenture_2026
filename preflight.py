from pathlib import Path

# Localiza la raíz del proyecto.
RAIZ = Path(__file__).resolve().parent


def preflight_check():
    """Comprueba que el índice exista y esté excluido de Git."""
    problemas = []

    # Comprueba que exista la carpeta del índice.
    if not (RAIZ / "vectorstore").is_dir():
        problemas.append("No existe la carpeta vectorstore/.")

    archivo_gitignore = RAIZ / ".gitignore"

    # Comprueba que Git tenga una regla para ignorar el índice.
    if not archivo_gitignore.is_file():
        problemas.append("No existe el archivo .gitignore.")
    else:
        reglas = archivo_gitignore.read_text(
            encoding="utf-8-sig"
        ).splitlines()

        if "vectorstore/" not in {linea.strip() for linea in reglas}:
            problemas.append("Falta vectorstore/ en .gitignore.")

    return problemas


if __name__ == "__main__":
    problemas = preflight_check()

    if problemas:
        print("Preflight con problemas:")
        for problema in problemas:
            print("-", problema)
    else:
        print("Preflight OK: el índice existe y está en .gitignore.")