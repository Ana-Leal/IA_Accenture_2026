# Límites de la métrica de evaluación

## Qué mide

Calcula precisión, cobertura y F1 mediante coincidencias de palabras
entre el resumen generado y una referencia, contando repeticiones
después de limpiar y tokenizar ambos textos.

Mide coincidencia textual; no comprueba por sí sola el significado,
la veracidad ni la importancia de la información omitida.

## Modos de falla conocidos

- **Una reformulación correcta puede perder puntaje.**
  En el caso 12, “Pintar solo una pared del dormitorio” conserva
  la restricción de no pintar las cuatro paredes. Sin embargo,
  obtiene F1 de 75 % porque no repite todas las palabras de la
  referencia.

- **Una precisión perfecta no garantiza una respuesta completa.**
  En el caso 14, el resumen conserva la revisión de la humedad,
  pero omite que todavía no se debe pintar. Obtiene precisión
  de 100 % y F1 de 76,19 %, aunque falta una condición importante.

- **Evaluar un campo no permite juzgar toda la respuesta JSON.**
  En los casos 5, 8 y 9, el resumen omite el lugar incluido en
  la referencia. El prompt también solicita un campo `lugar`,
  por lo que esa omisión no demuestra que el dato falte en el
  JSON completo. Nuestra evaluación solo abarca `resumen`.

No se observaron datos inventados ni contradicciones explícitas
en los diez casos revisados. Esto no demuestra que la métrica
pueda detectar esos errores en otras respuestas.

## Muestra revisada

Se revisaron diez casos de un conjunto de veinte respuestas:
los primeros cinco y los últimos cinco de la lista ordenada
de menor a mayor F1.

- Menor F1: casos 5, 8, 9, 12 y 14.
- Mayor F1: casos 13, 15, 16, 18 y 19.

El grupo superior presenta un empate en 100 %. Se conservó
el orden del registro para seleccionar sus últimos cinco casos.

Cada resumen se valoró por corrección factual, completitud
y contradicción, con una nota justificativa.

La muestra es pequeña y corresponde a solicitudes de servicios.
No representa todas las entradas posibles de la aplicación.

[Ver revisión manual](revision_manual.md).

[Ver respuestas, referencias y métricas](evidencias_bloque16/resultados_metricas.json).

## Recomendación de uso

Usar estas métricas como apoyo para comparar resúmenes bajo las
mismas condiciones y referencias, sin interpretarlas como una
calificación automática de calidad.

Revisar manualmente las cantidades, restricciones y negaciones,
además de casos con F1 alto y bajo. Para evaluar la ubicación,
revisar también el campo `lugar` del JSON, no solo el resumen.