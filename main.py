# Importa la función que ya prepara y envía la consulta a Gemini.
from src.consumir_gemini import consultar_gemini


# Define el punto de entrada de la aplicación.
def main():
    # Recibe la necesidad que quiere resolver la persona.
    pregunta = input("Describe qué necesitas resolver: ")

    try:
        # Reutiliza la consulta y el manejo de errores existentes.
        resultado = consultar_gemini(pregunta)

        # Muestra la respuesta generada.
        print("\nRespuesta:")
        print(resultado)

    except (ValueError, RuntimeError) as error:
        # Muestra los errores controlados sin un traceback.
        print("No se pudo completar la operación:", error)


# Inicia la aplicación únicamente al ejecutar este archivo.
if __name__ == "__main__":
    main()