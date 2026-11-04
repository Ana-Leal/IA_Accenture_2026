# Revisión manual de respuestas — Bloque 17

## Alcance y selección

Se revisan diez de las veinte respuestas evaluadas.

Se seleccionaron los primeros cinco y los últimos cinco casos de
la lista ordenada de menor a mayor F1:

- Menor F1: casos 5, 8, 9, 12 y 14.
- Mayor F1: casos 13, 15, 16, 18 y 19.

Los casos del grupo superior tienen F1 de 100 %. Para resolver el
empate se conservó el orden del registro y se tomaron sus últimos
cinco elementos, siguiendo el procedimiento de selección del curso.

Fuente: [Resultados y referencias](evidencias_bloque16/resultados_metricas.json).

Se evalúa únicamente el campo `resumen`, comparándolo con la
referencia y la solicitud. No se evalúa el JSON completo ni el
campo `lugar`.

## Criterios

- Corrección factual: la información expresada coincide con la solicitud.
- Completitud: conserva la información importante de la referencia.
- Contradicción: afirma algo contrario a la solicitud o referencia.
- Nota: justifica la valoración; una omisión no implica necesariamente
  una contradicción.

## Revisión de los diez casos

| Caso | F1 | Corrección factual | Completitud | Contradicción | Nota |
|---|---:|---|---|---|---|
| 5 | 66,67 % | Sí | Parcialmente | No | “Instalar una lámpara” conserva el trabajo solicitado, pero omite “en el comedor”, presente en la referencia. |
| 8 | 66,67 % | Sí | Parcialmente | No | “Armar un escritorio” identifica el trabajo, pero omite que es para el dormitorio. |
| 9 | 75,00 % | Sí | Parcialmente | No | “Cambiar tres enchufes” conserva la acción y la cantidad, pero omite el living. |
| 12 | 75,00 % | Sí | Sí | No | “Pintar solo una pared del dormitorio” conserva la restricción. Aunque omite “no las cuatro paredes”, la palabra “solo” mantiene ese significado. El puntaje baja por una diferencia de redacción, sin perder la condición principal. |
| 14 | 76,19 % | Sí | Parcialmente | No | “Revisar una mancha de humedad en el dormitorio” conserva el trabajo y el lugar, pero omite que todavía no se debe pintar. No ordena pintar: omite la restricción, sin contradecirla explícitamente. |
| 13 | 100,00 % | Sí | Sí | No | Conserva la reparación de la puerta del baño y la condición de no reemplazarla. |
| 15 | 100,00 % | Sí | Sí | No | Incluye ambos trabajos: reparar la llave del baño y destapar el desagüe del lavamanos. |
| 16 | 100,00 % | Sí | Sí | No | Conserva las dos acciones, lijar y barnizar, junto con el material y la identificación de la mesa del comedor. |
| 18 | 100,00 % | Sí | Sí | No | Conserva el ajuste solicitado y el problema de la puerta del dormitorio que roza el piso. |
| 19 | 100,00 % | Sí | Sí | No | Resume correctamente la necesidad de destapar el lavamanos del baño. |

## Hallazgos

- En el caso 12, el F1 de 75 % penaliza una formulación más breve
  que conserva el significado importante.
- En el caso 14, una precisión de 100 % no garantiza completitud:
  falta la condición de no pintar todavía.
- Los casos 5, 8 y 9 omiten el lugar en el resumen. Como el prompt
  solicita también un campo `lugar`, esta revisión no permite
  concluir que esa información falte en el JSON completo.
- Los cinco casos seleccionados con F1 de 100 % conservaron
  la información de sus referencias.
- No se observaron datos inventados ni contradicciones explícitas
  en estos diez resúmenes. Esto no garantiza que no puedan aparecer
  en otros casos.