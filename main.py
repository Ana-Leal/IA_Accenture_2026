# Permite medir el tiempo de la petición.
from time import perf_counter

# Reutiliza las funciones existentes del proyecto.
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costo,
)

# Tarifas de referencia documentadas para Gemini 3.5 Flash-Lite.
# Están expresadas en USD por un token.
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000


# Inicia la aplicación y muestra la respuesta y su consumo.
def main():
    pregunta = input("Describe qué necesitas resolver: ")

    try:
        # Prepara la consulta usando el modelo predeterminado.
        url, headers, body = armar_peticion(pregunta)

        # Mide el envío y la recepción de la respuesta.
        inicio = perf_counter()
        datos = enviar_peticion(url, headers, body)
        duracion = perf_counter() - inicio

        # Extrae y muestra el texto generado.
        texto = extraer_texto(datos)
        print("\nRespuesta:")
        print(texto)
        print(f"\nTiempo de respuesta: {duracion:.2f} segundos")

        # Obtiene los datos de consumo sin perder la respuesta
        # si el servicio no incluye estos campos.
        try:
            uso = datos["usageMetadata"]
            tokens_entrada = uso["promptTokenCount"]
            tokens_respuesta = uso["candidatesTokenCount"]
            tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

            # Comprueba que los conteos sean enteros no negativos.
            conteos = (
                tokens_entrada,
                tokens_respuesta,
                tokens_razonamiento,
            )
            if any(type(valor) is not int or valor < 0 for valor in conteos):
                raise ValueError("Conteos de tokens inválidos.")

            # La tarifa de salida incluye respuesta y razonamiento.
            tokens_salida = tokens_respuesta + tokens_razonamiento

            # Prepara una copia para reutilizar calcular_costo().
            # No modifica los datos originales recibidos de Gemini.
            datos_costo = {
                "usageMetadata": {
                    "promptTokenCount": tokens_entrada,
                    "candidatesTokenCount": tokens_salida,
                }
            }

            costo = calcular_costo(
                datos_costo,
                PRECIO_ENTRADA,
                PRECIO_SALIDA,
            )

            print(f"Tokens de entrada: {tokens_entrada}")
            print(f"Tokens de respuesta: {tokens_respuesta}")
            print(f"Tokens de razonamiento: {tokens_razonamiento}")
            print(f"Costo estimado con tarifas de referencia: USD {costo:.8f}")
            print("La estimación no implica un cobro en el nivel gratuito.")

        except (KeyError, TypeError, ValueError, RuntimeError):
            print(
                "No se pudo calcular el consumo y el costo: "
                "faltan datos de uso válidos."
            )

    # Muestra los fallos controlados por el módulo existente.
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)


# Ejecuta la aplicación solo al iniciar este archivo directamente.
if __name__ == "__main__":
    main()