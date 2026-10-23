# Permite mostrar el JSON validado y medir la petición.
import json
from time import perf_counter

# Reutiliza el banco de prompts existente.
from prompts.banco import BANCO_DE_PROMPTS

# Reutiliza las funciones existentes del proyecto.
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
    calcular_costo,
)

# Tarifas de referencia documentadas, en USD por token.
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000


# Inicia la aplicación y muestra la respuesta y su consumo.
def main():
    pregunta = input("Describe qué necesitas resolver: ")

    try:
        # Selecciona el prompt existente para identificar el oficio.
        prompt = next(
            elemento
            for elemento in BANCO_DE_PROMPTS
            if elemento["nombre"] == "identificar_oficio"
        )

        # Envía las instrucciones separadas de la pregunta del usuario.
        url, headers, body = armar_peticion(
            pregunta,
            system_instruction=prompt["system_instruction"],
            response_schema=prompt["response_schema"],
        )

        # Mide el envío y la recepción de la respuesta.
        inicio = perf_counter()
        datos = enviar_peticion(url, headers, body)
        duracion = perf_counter() - inicio

        # Extrae el texto y valida sus campos y tipos.
        texto = extraer_texto(datos)
        resultado = parsear_respuesta_json(
            texto,
            tipos_esperados=prompt["tipos_esperados"],
        )

        # Muestra únicamente el resultado que superó la validación.
        print("\nRespuesta JSON validada:")
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        print(f"\nTiempo de respuesta: {duracion:.2f} segundos")

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

            # La tarifa de salida incluye respuesta y razonamiento.
            tokens_salida = tokens_respuesta + tokens_razonamiento

            # Reutiliza calcular_costo sin modificar la respuesta original.
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

    # Muestra los errores de validación y del servicio.
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)


# Ejecuta la aplicación solo al iniciar este archivo directamente.
if __name__ == "__main__":
    main()