# Permite leer las opciones indicadas al ejecutar el archivo.
import sys
# Permite localizar la raíz del repositorio.
from pathlib import Path

# Permite medir cuánto tarda cada petición.
from time import perf_counter

# Agrega la raíz del repositorio a las rutas de importación.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Reutiliza las funciones que ya construimos.
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
)


# Prueba un candidato alternativo porque las mediciones de
# Gemini 3.8 Flash quedaron incompletas por errores del servicio.
modelos = [
    "gemini-3.6-flash",
]

# Usa las mismas consultas que dejamos en el Markdown.
consultas = [
    (
        "La llave del lavaplatos gotea incluso cuando la cierro. "
        "¿Qué tipo de trabajador necesito?"
    ),
    (
        "Necesito fabricar e instalar un mueble de madera a medida "
        "para mi dormitorio. ¿Qué tipo de trabajador necesito?"
    ),
    (
        "Hay una mancha de humedad en la pared del dormitorio "
        "y no sé de dónde viene. ¿Qué tipo de trabajador necesito?"
    ),
]


# Envía una consulta y devuelve su texto y el tiempo empleado.
def medir_consulta(pregunta, modelo):
    # Prepara la petición para el modelo indicado.
    url, headers, body = armar_peticion(pregunta, modelo=modelo)

    # Inicia el cronómetro justo antes del envío.
    inicio = perf_counter()

    # Envía la petición con nuestro manejo de errores existente.
    datos = enviar_peticion(url, headers, body)

    # Calcula el tiempo transcurrido en segundos.
    duracion = perf_counter() - inicio

    # Obtiene el texto usando nuestra función existente.
    texto = extraer_texto(datos)

    # Devuelve ambos resultados.
    return texto, duracion


# Ejecuta las pruebas únicamente al iniciar este archivo directamente.
if __name__ == "__main__":

    # Detecta si pedimos ejecutar solamente la consulta del mueble.
    if "--solo-mueble" in sys.argv:
        # Selecciona el modelo cuya respuesta falta evaluar.
        modelo = "gemini-3.6-flash"

        # La posición 1 corresponde a la segunda consulta: el mueble.
        pregunta = consultas[1]

        # Muestra qué modelo y consulta estamos usando.
        print(f"\nMODELO: {modelo}", flush=True)
        print("CONSULTA:", pregunta, flush=True)

        try:
            # Reutiliza la función existente para consultar y medir.
            texto, duracion = medir_consulta(pregunta, modelo)

            # Muestra el tiempo y la respuesta obtenida.
            print(f"Tiempo: {duracion:.2f} segundos")
            print("Respuesta:", texto, flush=True)

        except (ValueError, RuntimeError, TimeoutError  ) as error:
            # Muestra el fallo controlado si la consulta no resulta.
            print("Consulta fallida:", error, flush=True)

            # Termina el programa indicando que la consulta falló.
            sys.exit(1)

        # Termina aquí para no repetir las demás consultas.
        sys.exit(0)

    # Sin la opción --solo-mueble, ejecuta la comparación completa.
    # Recorre los modelos que estén incluidos en la lista.
    for modelo in modelos:
        print(f"\nMODELO: {modelo}", flush=True)
        tiempos = []

        # Repite la primera consulta cuatro veces para medir la latencia.
        for intento in range(1, 5):
            print(f"\nConsulta 1 — intento {intento}/4", flush=True)

            try:
                texto, duracion = medir_consulta(consultas[0], modelo)

                # Guarda el tiempo solo si la consulta terminó correctamente.
                tiempos.append(duracion)
                print(f"Tiempo: {duracion:.2f} segundos")
                print("Respuesta:", texto, flush=True)

            except (ValueError, RuntimeError, TimeoutError) as error:
                # Registra el fallo sin presentarlo como una respuesta válida.
                print("Intento fallido:", error, flush=True)

        # Publica el promedio únicamente si se completaron los cuatro intentos.
        if len(tiempos) == 4:
            promedio = sum(tiempos) / len(tiempos)
            print(
                f"\nLATENCIA PROMEDIO: {promedio:.2f} segundos",
                flush=True,
            )
        else:
            print(
                "\nMEDICIÓN INCOMPLETA: se requieren cuatro intentos exitosos.",
                flush=True,
            )

        # Prueba los otros dos casos para evaluar la calidad.
        for numero, pregunta in enumerate(consultas[1:], start=2):
            print(f"\nConsulta {numero}: {pregunta}", flush=True)

            try:
                texto, duracion = medir_consulta(pregunta, modelo)
                print(f"Tiempo: {duracion:.2f} segundos")
                print("Respuesta:", texto, flush=True)

            except (ValueError, RuntimeError, TimeoutError) as error:
                print("Consulta fallida:", error, flush=True)

    print("\nComparación terminada. Revisa los resultados y posibles fallos.")