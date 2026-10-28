# Permite mostrar el JSON y medir el tiempo de la consulta.
import json
from time import perf_counter

# Reutiliza las instrucciones y el esquema de respuesta.
from prompts.banco import BANCO_DE_PROMPTS

# Importa el módulo para consultar los costos actualizados de la sesión.
from src import cliente


# Referencia del bloque anterior:
# El cálculo se realizaba aquí mediante calcular_costo().
# Ahora las tarifas, el cálculo y el acumulado están en src/cliente.py.
#
# from src.consumir_gemini import calcular_costo
# PRECIO_ENTRADA = 0.30 / 1_000_000
# PRECIO_SALIDA = 2.50 / 1_000_000
#
# tokens_salida = tokens_respuesta + tokens_razonamiento
# datos_costo = {
#     "usageMetadata": {
#         "promptTokenCount": tokens_entrada,
#         "candidatesTokenCount": tokens_salida,
#     }
# }
# costo = calcular_costo(datos_costo, PRECIO_ENTRADA, PRECIO_SALIDA)


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

        resultado, datos = cliente.consultar_modelo(
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

        # El cliente ya comprobó los conteos al registrar el costo.
        if cliente.costo_ultima_consulta is not None:
            uso = datos["usageMetadata"]

            print(f"Tokens de entrada: {uso['promptTokenCount']}")
            print(f"Tokens de respuesta: {uso['candidatesTokenCount']}")
            print(f"Tokens de razonamiento: {uso.get('thoughtsTokenCount', 0)}")
        else:
            # Conserva la respuesta aunque no haya datos de uso válidos.
            print(
                "No se pudo calcular el consumo y el costo: "
                "faltan datos de uso válidos."
            )

    # El cliente comunica los errores con mensajes controlados.
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)

    # También muestra el consumo conocido si falló la validación del JSON.
    if cliente.costo_ultima_consulta is not None:
        print(
            "Costo estimado de la respuesta recibida "
            f"con tarifas de referencia: USD {cliente.costo_ultima_consulta:.8f}"
        )

    print(
        "Costo estimado acumulado conocido de esta sesión: "
        f"USD {cliente.costo_total_sesion:.8f}"
    )
    print("La estimación no implica un cobro en el nivel gratuito.")
    print(
        "El acumulado solo incluye respuestas con datos de uso válidos; "
        "excluye consumos desconocidos de intentos fallidos."
    )


# Inicia la aplicación solo al ejecutar este archivo directamente.
if __name__ == "__main__":
    main()