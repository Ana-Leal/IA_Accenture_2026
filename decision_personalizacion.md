# Decisión de personalización

## 1. El problema

La aplicación necesita orientar al usuario sobre el oficio adecuado
para su solicitud, utilizando información del catálogo y evitando
inventar servicios, precios o disponibilidad.

Se aplicó el cuestionario del bloque 30 con estos fundamentos:

- Información que cambia seguido: False. No contamos con evidencia
  de actualizaciones mensuales del catálogo. Es un supuesto provisional.
- Problema de formato o tono: False para el criterio revisado.
  Los 20 resúmenes conservados en
  docs/evidencias_bloque16/resultados_metricas.json mantienen un tono
  breve y directo, sin comentarios adicionales.
  Esta revisión no comprueba los 20 JSON completos, porque ese registro
  conserva únicamente sus resúmenes.
- Dataset grande y de calidad: False. dataset_tuning.py contiene
  10 ejemplos; no alcanza los 200 del criterio orientativo del curso.
- Presupuesto limitado o necesidad de iterar rápido: True.
  Para esta etapa académica se adopta el objetivo de comprobar
  cambios en menos de un día.
- Múltiples variantes: False. Actualmente se desarrolla una sola
  versión de la aplicación.

La revisión del tono no demuestra ausencia de errores de contenido.
Las omisiones o los errores al extraer el lugar requieren una
evaluación diferente.

## 2. Resultado del método de decisión

Al ejecutar decision.py se obtuvieron estos puntajes:

- RAG: 2 puntos.
- PEFT: 1 punto.
- Fine-tuning completo: 0 puntos.

RAG obtuvo el mayor puntaje, sin empate.

También se modificó únicamente la respuesta sobre problemas de
formato o tono, cambiándola a True como escenario hipotético:

- PEFT: 3 puntos.
- RAG: 2 puntos.
- Fine-tuning completo: 1 punto.

Esta comprobación muestra que la elección es sensible a ese criterio.
No demuestra que exista actualmente un problema que requiera PEFT.

## 3. Técnica elegida y por qué

Se elige mantener RAG para el alcance actual de orientación basada
en el catálogo de servicios.

El proyecto ya dispone de recuperación semántica y construcción de
contexto con citas. Esto permite actualizar la información consultada
sin entrenar el modelo y aprovechar el trabajo existente.

La elección implica mantener actualizado el catálogo y su índice,
además del consumo de embeddings y generación durante las consultas.

No se inicia un entrenamiento con PEFT ni fine-tuning completo.
Actualmente hay 10 ejemplos preparados y la revisión disponible
no basta para justificar ese entrenamiento.

La decisión es provisional: si una revisión de 20 respuestas completas
detecta al menos 3 incumplimientos de formato o tono, se repetirá
el cuestionario y se analizará si conviene incorporar PEFT.

RAG no corrige por sí solo los errores de formato ni garantiza
que todas las respuestas sean correctas.

## 4. Qué necesitaríamos para ejecutarla

Para el alcance actual:

- Existe 1 archivo fuente: docs/catalogo_servicios.md.
- La indexación registrada produjo 5 documentos y 8 fragmentos.
- Faltan 0 documentos adicionales para reproducir la demostración
  actual con ese catálogo.
- El índice local se genera mediante indexar_corpus.py.
- La recuperación se encuentra en recuperacion.py y la consulta RAG
  con generación se ejecuta mediante registro_rag.py.

Esto describe la demostración existente, no un catálogo completo
de todos los oficios ni su integración automática en main.py.

Si se reconsidera el entrenamiento, existen 10 ejemplos etiquetados.
Para alcanzar el umbral orientativo de 200 del cuestionario faltarían
190, además de revisar su calidad. Ese umbral del curso no es un
requisito oficial del proveedor ni garantiza un buen entrenamiento.