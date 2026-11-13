# Límites de autonomía del agente de oficios y servicios

## Herramientas y nivel de riesgo

- `consultar_oficio`: riesgo bajo. Consulta un catálogo local
  de oficios; no modifica datos ni contrata trabajadores.
- `calcular_superficie`: riesgo bajo. Calcula el área de una
  pared rectangular con las medidas recibidas; no realiza
  compras ni ejecuta trabajos.

Una elección incorrecta o argumentos equivocados pueden producir
una orientación incorrecta, aunque estas herramientas no ejecuten
acciones externas.

## Herramientas que requieren aprobación humana

Actualmente ninguna de las dos herramientas requiere aprobación
humana previa, porque únicamente consultan información o calculan.

El agente no tiene herramientas para enviar mensajes, contratar
servicios, efectuar pagos ni modificar registros de terceros.

Si se incorporan herramientas con consecuencias de riesgo alto,
se deberá implementar y comprobar la aprobación humana antes de
habilitarlas. Esa aprobación no está implementada en la versión actual.

## Revisión de trazas

- Frecuencia prevista: semanal durante el uso del prototipo y
  después de modificar las herramientas o el prompt.
- Archivo: `trazas_agente.jsonl`, en la raíz del repositorio.
- Cada registro incluye fecha UTC, sesión, entrada, herramientas,
  argumentos, observaciones y respuesta final.

Se revisará:

- Si la herramienta elegida corresponde a la solicitud.
- Si sus argumentos coinciden con los datos proporcionados.
- Si existen llamadas consecutivas innecesarias a una herramienta.
- Si la respuesta final coincide con las observaciones recibidas.
- Si el agente agrega información que las herramientas no respaldan.

### Revisión realizada

Se revisaron dos interacciones reales:

1. Consulta sobre carpintería: utilizó `consultar_oficio` con
   `oficio="carpintero"`. La respuesta coincide con el catálogo.
2. Cálculo de una pared: utilizó `calcular_superficie` con
   ancho 4 y alto 2,5. La herramienta y la respuesta indicaron 10 m².

En estas dos interacciones no se observaron llamadas repetidas
ni discrepancias entre las observaciones y las respuestas finales.
Esto no garantiza el mismo comportamiento para todas las entradas.

Las ejecuciones se realizaron por separado. Ambas usan el
identificador fijo `sesion_1` del programa; compartir ese identificador
en el archivo no significa que se conservara memoria entre procesos.

## Qué hacer ante un comportamiento inesperado

1. Detener las consultas y conservar la traza del caso.
2. Identificar la herramienta, los argumentos y la observación
   asociados a la respuesta incorrecta.
3. Si el problema corresponde a una herramienta, retirarla
   temporalmente de la lista de herramientas disponibles.
4. Corregir la causa identificada: descripción, validación,
   lógica de la herramienta o instrucciones del prompt.
5. Repetir el caso y revisar la nueva traza antes de volver
   a habilitar la herramienta.