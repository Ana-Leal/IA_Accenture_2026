# Permite mostrar el JSON y medir el tiempo de la consulta.
import json
from time import perf_counter

# Reutiliza las instrucciones y el esquema de respuesta.
from prompts.banco import BANCO_DE_PROMPTS

# El cliente coordina la consulta, los reintentos y la validación.
from src.cliente import consultar_modelo

# Conserva la función existente para calcular el costo.
from src.consumir_gemini import calcular_costo


# Tarifas de referencia documentadas, en USD por token.
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000


def main():
    pregunta = input("Describe qué necesitas resolver: ")

    try:
        # Selecciona las instrucciones para identificar el oficio.
        prompt = next(
            elemento
            for elemento in BANCO_DE_PROMPTS
            if elemento["nombre"] == "identificar_oficio"
        )

        # Mide la consulta completa, incluidas las esperas por reintentos.
        inicio = perf_counter()

        resultado, datos = consultar_modelo(
            pregunta,
            system_instruction=prompt["system_instruction"],
            response_schema=prompt["response_schema"],
            tipos_esperados=prompt["tipos_esperados"],
        )

        duracion = perf_counter() - inicio

        # El cliente devuelve un resultado que ya superó la validación.
        print("\nRespuesta JSON validada:")
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        print(f"\nTiempo total de la consulta: {duracion:.2f} segundos")

        # Conserva la respuesta aunque falten los datos de consumo.
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

            # Incluye respuesta y razonamiento en los tokens de salida.
            tokens_salida = tokens_respuesta + tokens_razonamiento

            # Reutiliza calcular_costo sin modificar los datos originales.
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
            print(
                "Costo estimado de la respuesta recibida "
                f"con tarifas de referencia: USD {costo:.8f}"
            )
            print("La estimación no implica un cobro en el nivel gratuito.")
            print(
                "No incluye posibles consumos de intentos fallidos "
                "cuyos datos de uso no se recibieron."
            )

        except (KeyError, TypeError, ValueError, RuntimeError):
            print(
                "No se pudo calcular el consumo y el costo: "
                "faltan datos de uso válidos."
            )

    # El cliente comunica los errores con mensajes controlados.
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)


# Inicia la aplicación solo al ejecutar este archivo directamente.
if __name__ == "__main__":
    main()