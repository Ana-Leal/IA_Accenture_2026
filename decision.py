# Método de puntuación proporcionado en el bloque 30.
def recomendar_estrategia(respuestas):
    puntos = {
        "RAG": 0,
        "Fine-tuning completo": 0,
        "PEFT": 0,
    }

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3

    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1

    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1

    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1

    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    # Conserva todas las técnicas empatadas en el puntaje máximo.
    maximo = max(puntos.values())
    ganadoras = [
        tecnica
        for tecnica, puntaje in puntos.items()
        if puntaje == maximo
    ]

    return puntos, ganadoras


respuestas_mi_caso = {
    # Supuesto provisional: no hay evidencia de cambios mensuales.
    "informacion_cambia_seguido": False,

    # Revisión limitada al tono breve y directo de 20 resúmenes.
    # No equivale a revisar sus 20 respuestas JSON completas.
    "problema_de_formato_o_tono": False,

    # El dataset del bloque 29 contiene 10 ejemplos, no 200.
    "dataset_grande_y_de_calidad": False,

    # Objetivo adoptado: comprobar cambios en menos de un día.
    "presupuesto_limitado_o_iterar_rapido": True,

    # Una sola versión de la aplicación.
    "necesita_multiples_variantes": False,
}


if __name__ == "__main__":
    puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)

    print("Resultado para nuestro proyecto:")
    for tecnica, puntaje in puntos.items():
        print(f"{tecnica}: {puntaje} puntos")

    print("Candidatas:", ", ".join(ganadoras))

    # Comprueba la respuesta cuya evidencia es más limitada.
    # Es un escenario hipotético, no un fallo observado.
    variante = dict(respuestas_mi_caso)
    variante["problema_de_formato_o_tono"] = True

    puntos_variante, ganadoras_variante = recomendar_estrategia(variante)

    print("\nSi se confirmara un problema de formato o tono:")
    for tecnica, puntaje in puntos_variante.items():
        print(f"{tecnica}: {puntaje} puntos")

    print("Candidatas:", ", ".join(ganadoras_variante))