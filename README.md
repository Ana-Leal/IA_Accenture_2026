# Miniaplicación de orientación de oficios — Accenture / Skillnest

La aplicación interpreta una necesidad descrita por el usuario e identifica
el tipo de trabajador adecuado. Utiliza Gemini y devuelve una respuesta
JSON validada con los campos `oficio` y `motivo`.

El proyecto se desarrolla progresivamente durante la Especialización
en Desarrollo con IA Generativa.

## Requisitos

- Python y Git instalados.
- Una clave de Gemini API.
- Conexión a Internet para las consultas reales.
- Entorno probado por la autora: Windows, Git Bash y Python 3.14.8.

## Instalación desde cero

Los siguientes comandos corresponden a Git Bash de Windows.

### 1. Clonar y entrar al repositorio

```bash
git clone https://github.com/Ana-Leal/IA_Accenture_2026.git
cd IA_Accenture_2026
```

Todos los comandos siguientes se ejecutan desde esta carpeta,
donde están `main.py` y `requirements.txt`.

Si descargaste un ZIP, extráelo y abre la terminal en la carpeta
que contiene esos dos archivos.

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
source venv/Scripts/activate
```

El indicador `(venv)` debe aparecer en la terminal.

### 3. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar la credencial

```bash
cp .env.example .env
```

Abre `.env` en el editor y configura tu clave:

```dotenv
API_KEY=tu_clave_real
```

Guarda el archivo en la misma carpeta que `main.py`.
No compartas su contenido ni lo subas a GitHub.

## Ejecutar la aplicación

Con el entorno virtual activo:

```bash
python main.py
```

Cuando aparezca `Describe qué necesitas resolver:`, escribe una necesidad
y presiona Enter. Por ejemplo:

```text
La llave del lavaplatos gotea incluso cuando la cierro. ¿Qué tipo de trabajador necesito?
```

La aplicación:

1. Selecciona `identificar_oficio` del banco de prompts.
2. Envía las instrucciones de sistema separadas de la pregunta.
3. Solicita una respuesta con esquema JSON.
4. Valida los campos y tipos recibidos.
5. Muestra la respuesta, el tiempo, los tokens y el costo estimado.

Ejemplo de una respuesta real validada:

```json
{
  "oficio": "Gasfíter",
  "motivo": "Para revisar y reparar la llave que gotea."
}
```

El modelo predeterminado es `gemini-3.5-flash-lite`.

### Activar el entorno en otra sesión

Si cerraste la terminal, vuelve a abrirla en la raíz del proyecto y ejecuta:

```bash
source venv/Scripts/activate
python main.py
```

Si aparece `ModuleNotFoundError: No module named 'requests'`, comprueba
que el entorno esté activo y que hayas instalado las dependencias en él.

## Alcance y limitaciones

- Orienta sobre el tipo de trabajador; no contrata ni contacta profesionales.
- No verifica disponibilidad, certificaciones ni precios de trabajadores.
- No diagnostica con certeza la causa de una avería.
- Si falta información, el prompt indica devolver `por determinar`
  y explicar qué información falta.
- La aplicación principal usa el prompt `identificar_oficio`.
  Los otros dos prompts se evalúan mediante el script de consistencia.
- La validación JSON comprueba estructura y tipos, no garantiza
  que toda respuesta sea correcta.
- Las consultas dependen de la disponibilidad y los límites de la API.
- Los errores controlados se muestran como mensajes; no equivalen
  a una consulta exitosa.

### Tiempo, tokens y costo

El tiempo mostrado corresponde a la consulta completa: preparación,
envío, reintentos, esperas y procesamiento de la respuesta, incluida
la validación JSON.

El costo usa las tarifas de referencia documentadas para el modelo:

- Entrada: USD 0.30 por 1.000.000 de tokens.
- Salida: USD 2.50 por 1.000.000 de tokens.

Para la salida se suman los tokens de respuesta y de razonamiento.
La estimación no implica un cobro en el nivel gratuito ni sustituye
la facturación del proveedor. Las tarifas pueden cambiar.

Si faltan datos de consumo válidos, se conserva la respuesta y se informa
que no fue posible calcular el consumo y el costo.

## Estructura del proyecto

- `main.py`: punto de entrada de la aplicación.
- `src/cliente.py`: coordinación de consultas, reintentos con espera
  creciente y registro del costo por respuesta y acumulado de sesión.
- `src/consumir_gemini.py`: preparación y envío de peticiones,
  extracción del texto, validación JSON y cálculo de costo.
- `prompts/banco.py`: instrucciones, ejemplos y esquemas de los prompts.
- `prompts/test_consistencia.py`: evaluación mediante consultas reales.
- `prompts/registro_resultados.json`: registro de la evaluación realizada.
- `tests/`: pruebas locales y comparación de modelos.
- `docs/`: documentación y evidencias.
- `docs/evidencias_bloque7/`: capturas de validación y manejo de errores.
- `docs/evidencias_bloque8/`: diagrama del bloque 8 y decisión del bloque 9.
- `requirements.txt`: dependencias del proyecto.
- `.env.example`: plantilla de configuración sin credenciales reales.
- `.gitignore`: exclusiones de Git, como `.env` y el entorno virtual.
- `prompts/`: banco de prompts de sistema, esquemas JSON, pruebas de consistencia y registro de resultados.

## Seguridad y versionamiento

- No incluir claves, contraseñas ni tokens en los archivos publicados.
- Mantener `.env` excluido mediante `.gitignore`.
- Utilizar un entorno virtual propio para el proyecto.
- Registrar los avances mediante commits y subirlos a GitHub.

## Evidencias de la primera petición autenticada

Estas evidencias están directamente dentro de `docs/`:

- [Registro de la primera petición](docs/evidencia-primera-peticion.md)
- [Captura de la petición](docs/peticion.png)
- [Captura de la respuesta](docs/respuesta.png)

## Bloque 7: validación y manejo de errores

El módulo valida la pregunta y controla errores de conexión,
tiempo de espera, estado HTTP, JSON inválido y campos o elementos
faltantes en la estructura esperada.

### Pruebas locales

```bash
python tests/pruebas_bloque_7.py
```

Simulan errores de conexión, timeout, JSON inválido, campos faltantes
y listas vacías. No realizan llamadas a la API.

### Prueba directa del módulo

```bash
python src/consumir_gemini.py
```

Realiza una consulta real de conexión. Es una prueba auxiliar;
el punto de entrada de la aplicación es `main.py`.

### Evidencias

- [Tiempo de espera controlado](docs/evidencias_bloque7/timeout01.png)
- [Credencial inválida, pregunta vacía y consulta válida](docs/evidencias_bloque7/02_tres_pruebas.png)
- [Errores controlados](docs/evidencias_bloque7/03_errores_controlados.png)
- [Commit y push](docs/evidencias_bloque7/04_commit_push.png)
- [Timeout simulado](docs/evidencias_bloque7/05_timeout_simulado.png)

## Bloque 8: arquitectura y cálculo de costo

- [Diagrama de arquitectura del bloque 8](docs/evidencias_bloque8/diagrama_arquitectura_bloque8.png)

El diagrama conserva la implementación de esa etapa.
El flujo actual de `main.py`, con prompt y validación JSON,
está descrito en la sección de ejecución.

```bash
python tests/pruebas_bloque_8.py
```

Estas pruebas utilizan datos y precios ficticios para comprobar
el cálculo, la duplicación de precios y la ausencia de datos de uso.
No realizan llamadas a la API.

## Bloque 9: comparación y elección del modelo

- [Comparación, resultados y decisión de arquitectura](docs/evidencias_bloque8/decision-arquitectura.md)

Se seleccionó Gemini 3.5 Flash-Lite para el prototipo.
El documento registra resultados, incidencias y limitaciones.

### Ejecutar la comparación

```bash
python -u tests/comparar_modelos_bloque_9.py
```

Este script realiza consultas reales a los modelos de su lista `modelos`.
Actualmente contiene Gemini 3.6 Flash como candidato alternativo.
Los resultados anteriores de los otros modelos se conservan
en el documento de decisión.

Realiza cuatro intentos de la consulta del lavaplatos y una consulta
para cada caso adicional: mueble y humedad. Solo imprime el promedio
de latencia si los cuatro primeros intentos son exitosos.

Para repetir únicamente el caso del mueble con Gemini 3.6 Flash:

```bash
python -u tests/comparar_modelos_bloque_9.py --solo-mueble
```

## Bloque 10: banco de prompts y respuestas JSON

El módulo admite instrucciones de sistema separadas del mensaje
del usuario, un esquema JSON y validación local de campos y tipos.

- [Banco de prompts](prompts/banco.py)
- [Script de consistencia](prompts/test_consistencia.py)
- [Resultados reales registrados](prompts/registro_resultados.json)

### Ejecutar la evaluación

```bash
python -u prompts/test_consistencia.py
```

Realiza nueve consultas reales: tres por cada prompt.
No es necesario ejecutar esta evaluación para iniciar la aplicación.

### Resultados del 22 de octubre de 2026 — hora de Chile

| Prompt | Respuestas válidas | Fallos |
|---|---:|---:|
| identificar_oficio | 3/3 | 0 |
| resumir_necesidad | 3/3 | 0 |
| aclarar_necesidad | 3/3 | 0 |

La revisión confirmó la identificación del oficio, el resumen de la necesidad
sin agregar datos y la solicitud de aclaraciones ante humedad de origen
desconocido.

Una aclaración mencionó al pintor entre posibles oficios, lo que reduce
la precisión de esa orientación.

Estos resultados corresponden a las nueve consultas registradas;
no garantizan el mismo comportamiento para cualquier entrada.
El registro conserva la fecha en UTC.

## Bloque 11 / Gate 1: verificación realizada

El 23 de octubre de 2026 se probó una copia descargada desde GitHub
en una carpeta separada, con un entorno virtual recién creado.

- Las dependencias de `requirements.txt` se instalaron correctamente.
- Las pruebas locales de los bloques 7 y 8 pasaron.
- Se integró en `main.py` el prompt `identificar_oficio` y la validación JSON.
- La ejecución principal obtuvo una respuesta real y validada.

En esa prueba, el entorno virtual se creó en la carpeta superior
a la del código y se activó desde la carpeta del proyecto con:

```bash
source ../venv/Scripts/activate
```

Esta ubicación corresponde únicamente a esa prueba.
La instalación recomendada al inicio del README crea `venv`
dentro de la raíz del proyecto.

### Resultado observado

| Dato | Resultado |
|---|---|
| Consulta | Llave del lavaplatos que gotea |
| Oficio | Gasfíter |
| Tiempo | 5.08 segundos |
| Tokens de entrada | 150 |
| Tokens de respuesta | 32 |
| Tokens de razonamiento | 0 |
| Costo estimado de referencia | USD 0.00012500 |

Antes de la ejecución exitosa se recibieron errores HTTP 503.
El mensaje del proveedor indicó alta demanda del modelo.
La aplicación mostró los errores de forma controlada.

La ejecución exitosa demuestra el funcionamiento observado en esa prueba;
no garantiza disponibilidad permanente del servicio.

### Verificación final desde un clon limpio — 23 de octubre de 2026

Se verificó el commit `6e06ce9` en una carpeta independiente,
con un entorno virtual nuevo y las dependencias instaladas
desde `requirements.txt`. Se configuró localmente `.env`.

La ejecución de `python main.py` finalizó correctamente:
devolvió JSON validado con el oficio Gasfíter, tardó 1.29 segundos
y registró 150 tokens de entrada, 32 de respuesta y 0 de razonamiento.
El costo estimado de referencia fue USD 0.00012500.
## Bloque 12: cliente modular con reintentos

`src/cliente.py` reúne la consulta al modelo mediante
`consultar_modelo()`. La aplicación se inicia con:

```bash
python main.py
```

El cliente reutiliza las funciones de `src/consumir_gemini.py`
y conserva la validación de la respuesta JSON.

### Manejo de errores

- Los errores de conexión, timeout, HTTP 429 y HTTP 5xx permiten
  hasta tres intentos totales. En el bloque 12 se utilizaba una espera
  fija de dos segundos; desde el bloque 13 se utiliza espera creciente
  con variación aleatoria y límite máximo.
- No se espera ni se vuelve a intentar después del tercer fallo.
- Las credenciales ausentes o inválidas se informan sin reintentar.
  Se reconocen HTTP 401, HTTP 403 y HTTP 400 con
  el motivo `API_KEY_INVALID`.
- Los demás errores HTTP y los errores de validación JSON
  se informan sin reintentar.

La aplicación muestra el tiempo total de la consulta y estima
el costo de la respuesta recibida usando sus datos de consumo.
La estimación no incluye posibles consumos de intentos fallidos
cuyos datos de uso no se recibieron.

### Pruebas locales

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python tests/pruebas_bloque12.py
```

Estas pruebas simulan respuestas del proveedor y las esperas.
No realizan llamadas a la API.

Comprueban la recuperación ante HTTP 429 y 503, el agotamiento
de los tres intentos y el rechazo de credenciales inválidas
sin reintentos para HTTP 401, 403 y 400 con `API_KEY_INVALID`.

## Bloque 13: espera creciente y registro de costos

El cliente modular de `src/cliente.py` reintenta únicamente los errores
temporales, con un máximo predeterminado de tres intentos.

Entre intentos utiliza una espera base de 2 segundos que se duplica,
agrega una variación aleatoria de hasta un 10 % y respeta un máximo
de 30 segundos por espera. No espera después del último intento.

Los errores de credenciales no se reintentan.

### Registro del costo

El cliente calcula el costo estimado de cada respuesta con datos de uso
válidos y lo acumula durante la ejecución del programa.

El cálculo utiliza tarifas de referencia por token e incluye los tokens
de entrada, respuesta y razonamiento. Las tarifas están definidas en
`src/cliente.py`.

Si faltan datos de uso válidos, el costo se considera desconocido y
no se agrega al acumulado. No se contabilizan consumos desconocidos
de intentos fallidos.

`main.py` muestra el costo de la última respuesta y el acumulado conocido.
El acumulado se reinicia al iniciar otra ejecución. Como `main.py`
realiza una sola consulta por ejecución, normalmente ambos valores
coinciden.

La estimación no implica un cobro en el nivel gratuito.

### Comprobación real del límite de uso

El 28 de octubre de 2026 se ejecutaron 10 consultas consecutivas
mediante `tests/prueba_limite_uso.py`.

- Consultas realizadas: 10.
- Intentos de envío: 10.
- Respuestas HTTP 200: 10.
- Respuestas HTTP 429: ninguna.
- Reintentos y esperas: ninguno.
- Costo estimado acumulado conocido: USD 0.00006800.

La ejecución confirmó las consultas exitosas y el registro del costo.
No se alcanzó el límite de uso, por lo que todavía no se ha acreditado
la recuperación ante un HTTP 429 real solicitada en el bloque 13.
Ese comportamiento sí está verificado mediante pruebas simuladas.

El costo utiliza tarifas de referencia y no implica necesariamente
un cobro en el nivel gratuito.

[Ver registro de la ejecución](docs/evidencias_bloque13/prueba_limite_uso.json)

Para ejecutar nuevamente el ensayo, desde la raíz del repositorio
y con el entorno virtual activo:

```bash
python -u tests/prueba_limite_uso.py
```

Este comando realiza consultas reales y consume cuota de la API.
Cada consulta puede efectuar hasta tres intentos. Una nueva ejecución
reemplaza el archivo de registro anterior.

## Bloque 14: pruebas unitarias del cliente modular

Las pruebas se encuentran en `tests/test_cliente.py` y utilizan `pytest`.

Comprueban:

- Respuestas HTTP exitosas y errores de credenciales.
- Clasificación de HTTP 429 y errores del servidor como temporales.
- Recuperación mediante reintentos y agotamiento del límite.
- Esperas crecientes, variación aleatoria y límite de espera.
- Propagación de errores que no deben reintentarse.
- Cálculo del costo, tokens de razonamiento y acumulación por sesión.
- Manejo de datos de uso faltantes.
- Coordinación del cliente sin registrar varias veces una misma respuesta.

Las peticiones HTTP y las esperas se simulan. Estas pruebas no requieren
una credencial real, no realizan consultas a Gemini y no consumen tokens.

### Ejecutar las pruebas unitarias

Desde la raíz del repositorio, con el entorno virtual activo y las
dependencias de `requirements.txt` instaladas:

```bash
python -m pytest tests/test_cliente.py -v
```

Resultado de la ejecución realizada: **17 pruebas aprobadas**.

### Ejecutar las pruebas anteriores

```bash
python tests/pruebas_bloque_7.py
python tests/pruebas_bloque_8.py
python tests/pruebas_bloque12.py
```

Las tres comprobaciones pasaron. La prueba del bloque 12 se adaptó
para comprobar las nuevas esperas crecientes.
## Bloque 15: pipeline de procesamiento de texto

El módulo `src/pipeline_texto.py` contiene tres funciones:

- `limpiar_texto`: normaliza mayúsculas, puntuación y espacios.
- `tokenizar`: separa el texto limpio en palabras.
- `procesar_texto`: combina ambos pasos.

### Pruebas unitarias

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python -m pytest tests/test_pipeline_texto.py -v
```

Las dos pruebas pasaron: normalización de mayúsculas y puntuación,
y entrada de solo puntuación que devuelve una lista vacía.
No realizan llamadas a la API.

### Evaluación con tres respuestas reales

Se utilizó el prompt `resumir_necesidad` mediante `consultar_modelo`.
Se comparó el campo `resumen` con referencias escritas previamente.

La coincidencia se calcula dividiendo las palabras únicas compartidas
por las palabras únicas de la referencia. Se procesan ambos textos.
Si la referencia no contiene palabras, se devuelve 0 para evitar
una división por cero.

| Caso | Sin limpiar | Después de procesar |
|---|---:|---:|
| Reparar la llave del lavaplatos | 85.7 % | 100.0 % |
| Fabricar e instalar un mueble | 88.9 % | 100.0 % |
| Pintar las paredes del living | 60.0 % | 100.0 % |

La limpieza eliminó diferencias de puntuación y mayúsculas.
Esta métrica no evalúa significado, orden ni repeticiones:
una coincidencia del 100 % no garantiza una respuesta correcta.

[Ver respuestas y métricas](docs/evidencias_bloque15/comparacion_textos.json)

Para repetir la evaluación:

```bash
python -u tests/evaluar_pipeline_bloque15.py
```

Este comando realiza tres consultas reales, con posibles reintentos,
consume cuota de la API y reemplaza el registro anterior.

## Bloque 16: precisión, cobertura y F1

El módulo `src/metricas_texto.py` reutiliza el procesamiento del
bloque 15 y calcula coincidencias mediante `Counter`, considerando
las repeticiones de cada palabra.

- Precisión: coincidencias divididas por las palabras de la respuesta.
- Cobertura: coincidencias divididas por las palabras de la referencia.
- F1: media armónica de precisión y cobertura.

Si alguno de los textos queda vacío, las tres métricas devuelven cero
para evitar divisiones por cero.

### Pruebas unitarias

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python -m pytest tests/test_metricas_texto.py -v
```

Resultado: nueve pruebas aprobadas. Comprueban textos equivalentes,
respuestas incompletas, repeticiones adicionales, ausencia de
coincidencias, textos vacíos y cálculo de promedios.

Estas pruebas no realizan llamadas a la API.

### Evaluación de respuestas y ampliación del bloque 17

Desde la raíz del repositorio, con el entorno virtual activo
y `API_KEY` configurada:

```bash
python -u tests/evaluar_metricas_bloque16.py
```

El script reutiliza tres respuestas guardadas del bloque 15 y
realiza 17 consultas nuevas mediante el cliente modular.
Las consultas y referencias nuevas están en `tests/casos_bloque17.py`.

Evalúa el campo `resumen` y guarda los veinte casos ordenados
de menor a mayor F1 en
`docs/evidencias_bloque16/resultados_metricas.json`.

Resultados de la ejecución registrada:

| Métrica | Promedio |
|---|---:|
| Precisión | 100,00 % |
| Cobertura | 81,35 % |
| F1 | 88,38 % |

Cada ejecución realiza nuevamente las 17 consultas, consume cuota
de la API y reemplaza el registro al terminar. No es necesario
ejecutarlo para leer las evidencias guardadas.

[Ver respuestas, referencias y métricas](docs/evidencias_bloque16/resultados_metricas.json)
### Límites de la evaluación

Estas métricas comparan palabras y sus cantidades; no verifican
significado, orden ni veracidad. Los sinónimos pueden reducir el
puntaje y una negación ausente puede mantener un puntaje alto.

Los resultados corresponden únicamente a los veinte resúmenes evaluados.
No garantizan la calidad de otras respuestas ni evalúan el campo `lugar`.

## Bloque 17: revisión cualitativa y límites
Se evaluaron veinte respuestas y se revisaron manualmente diez:
cinco del extremo inferior y cinco del extremo superior de F1.

La revisión considera corrección factual, completitud y
contradicción, con una justificación por caso.

- [Revisión manual](docs/revision_manual.md).
- [Límites de la métrica y recomendación de uso](docs/limites_metrica.md).

La revisión se realizó sobre las respuestas guardadas, sin
generar consultas adicionales.
## Bloque 18: cadena de tres pasos con LangChain

El módulo `src/cadena_tres_pasos.py` conecta tres tareas:

1. Extraer la necesidad, conservando lugares, cantidades y restricciones.
2. Orientar sobre el oficio adecuado o pedir aclaración si faltan datos.
3. Redactar la orientación en lenguaje sencillo.

Cada paso utiliza un `PromptTemplate`, el modelo y `StrOutputParser`.
El operador `|` conecta los pasos y las funciones intermedias preparan
la entrada de la siguiente plantilla.

La función `construir_cadena(modelo)` recibe el modelo como parámetro,
lo que permite probarla con respuestas simuladas.

### Ejecutar la cadena

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y `API_KEY` configurada en `.env`:

```bash
python -m src.cadena_tres_pasos
```

El módulo utiliza la solicitud de ejemplo incluida en el código.
Reutiliza `API_KEY` mediante la variable `GEMINI_API_KEY` durante
la ejecución, sin modificar el archivo `.env`.

La cadena realiza tres llamadas reales a Gemini, además de los
posibles reintentos del conector, y consume cuota de la API.

### Prueba unitaria

```bash
python -m pytest tests/test_cadena_tres_pasos.py -v
```

La prueba verifica las tres llamadas, el paso de las respuestas
entre etapas y la salida final como texto. Utiliza un modelo
simulado: no necesita una credencial real ni consume tokens.

Resultado observado: una prueba aprobada.

### Resultado de la ejecución real

Se probó una solicitud de reparación de una puerta de madera
del baño, conservando la puerta y la cerradura actuales.

La respuesta recomendó un carpintero y conservó las condiciones
de no reemplazarlas ni realizar otros trabajos sin consultar.
Presentó tres viñetas, aunque añadió una introducción.

Esta ejecución demuestra el funcionamiento completo para ese caso;
no garantiza que todas las respuestas conserven siempre los detalles.

## Bloque 19: enrutamiento condicional

El módulo `src/enrutamiento.py` clasifica los mensajes como pregunta,
queja o sugerencia y selecciona una ruta con un prompt diferente.

La clasificación se normaliza con `.strip().lower()`.
`RunnablePassthrough.assign` conserva el mensaje original y agrega
la categoría. `RunnableBranch` selecciona la ruta; pregunta funciona
como ruta por defecto cuando ninguna condición coincide.

### Pruebas automatizadas

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python -m pytest tests/test_enrutamiento.py -v
```

Resultado: cinco pruebas aprobadas. Comprueban las rutas de queja,
sugerencia y pregunta, una categoría desconocida y la normalización.

Estas pruebas utilizan mocks y no realizan llamadas a Gemini.

### Comprobación manual de clasificación

Se realizaron tres consultas reales con estos resultados:

| Mensaje | Categoría esperada | Categoría obtenida |
|---|---|---|
| ¿Cómo cambio mi contraseña? | pregunta | pregunta |
| La app se cierra cada vez que subo una foto. | queja | queja |
| Estaría bueno que la app tuviera modo oscuro. | sugerencia | sugerencia |

Las tres categorías coincidieron con lo esperado.
Esta comprobación evaluó la clasificación; las rutas se verificaron
mediante las pruebas automatizadas.
## Bloque 20: manejo de errores del flujo orquestado

El módulo `src/enrutamiento.py` incorpora dos mecanismos:

- `construir_cadena_queja_segura`: protege la ruta de quejas mediante
  `with_fallbacks` y devuelve una respuesta de respaldo si falla.
- `procesar_mensaje_seguro`: ejecuta la cadena dentro de un
  `try/except`, registra los errores no cubiertos por el respaldo
  y devuelve un mensaje controlado.

### Ejecutar las pruebas

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python -m pytest tests/test_enrutamiento.py tests/test_orquestacion.py -v
```

Resultado: siete pruebas aprobadas.

Las cinco pruebas del bloque 19 verifican las rutas, la categoría
desconocida y la normalización. Las dos del bloque 20 comprueban
el respaldo ante un fallo de la ruta de quejas y la captura de
un fallo en la clasificación, incluido su registro en consola.

Las pruebas utilizan simulaciones, no llaman a Gemini
y no consumen cuota de la API.
## Bloque 21: agente con herramientas

El archivo `src/agente_con_herramientas.py` implementa un agente
con `create_tool_calling_agent` y `AgentExecutor`.

El agente dispone de dos herramientas:

- `consultar_oficio`: consulta un catálogo local de oficios.
- `calcular_superficie`: calcula el área de una pared rectangular
  a partir del ancho y alto en metros, sin descontar aberturas.

Cada herramienta incluye argumentos tipados y una descripción
que indica cuándo utilizarla.

### Ejecutar el agente

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y `API_KEY` configurada en `.env`:

```bash
python -m src.agente_con_herramientas
```

La ejecución realiza consultas reales a Gemini y consume cuota.
Muestra la respuesta final y las herramientas utilizadas mediante
`intermediate_steps`, incluidos sus argumentos y resultados.

### Comprobaciones realizadas

| Consulta | Herramienta utilizada | Resultado |
|---|---|---|
| Según el catálogo, ¿qué trabajos realiza un carpintero? | `consultar_oficio` | Fabrica y repara muebles y elementos de madera. |
| ¿Cuál es la superficie de una pared de 4 metros de ancho y 2,5 metros de alto? | `calcular_superficie` | 10 m². |

En ambas ejecuciones se verificó la herramienta elegida,
sus argumentos y el resultado devuelto.
## Bloque 22: herramientas estructuradas y memoria

Se amplió `src/agente_con_herramientas.py` con:

- `ArgumentosSuperficie`, definido mediante Pydantic y conectado
  a la herramienta con `args_schema`, para describir ancho y alto.
- `chat_history` en el prompt, antes del mensaje del usuario.
- `RunnableWithMessageHistory` para incorporar mensajes anteriores.
- Historiales independientes mediante `session_id`.
- Normalización de la respuesta de Gemini a texto antes de guardarla.

### Comprobaciones realizadas

| Comprobación | Resultado observado |
|---|---|
| Invocación directa de la herramienta con ancho 4 y alto 2,5 | 10 m², sin consultar a Gemini. |
| Primer turno de una sesión: pared de 4 × 2,5 metros | 10 m² y dos mensajes guardados. |
| Segundo turno: duplicar el ancho manteniendo la altura | Utilizó 8 × 2,5 metros; devolvió 20 m² y quedaron cuatro mensajes. |
| Consulta desde otra sesión sobre las medidas anteriores | Indicó que no se habían proporcionado medidas en esa conversación. |

Se verificó que los historiales de las dos sesiones fueran objetos
distintos y contuvieran dos mensajes cada uno.

Las pruebas de conversación se realizaron con llamadas consecutivas
a `construir_agente_con_memoria(modelo)` y su ejecutor, dentro del
mismo proceso, pasando la configuración correspondiente a cada sesión.

### Alcance de la memoria

El historial se conserva únicamente mientras el proceso permanece
abierto. No se guarda en archivos ni en una base de datos.

La ejecución interactiva del módulo sigue solicitando una sola
consulta por ejecución; las comprobaciones de varios turnos se
realizaron desde un script en la terminal.

Reenviar el historial aumenta los tokens de entrada de las consultas.

Durante las pruebas aparecieron avisos de deprecación de
`RunnableWithMessageHistory` e `InMemoryChatMessageHistory`.
Las ejecuciones finalizaron correctamente utilizando el mecanismo
presentado en el curso.
## Bloque 23: trazas y límites de autonomía

El agente guarda cada interacción completada en
`trazas_agente.jsonl`, incluyendo fecha UTC, sesión, entrada,
herramientas utilizadas, argumentos, observaciones y respuesta final.
Los registros nuevos se agregan sin borrar los anteriores.

- [Límites de autonomía del agente](docs/limites_autonomia_agente.md)
- [Trazas registradas](trazas_agente.jsonl)

Se verificaron dos consultas reales: una al catálogo de oficios
y otra al cálculo de superficie. Ambas utilizaron la herramienta
correspondiente y sus respuestas coincidieron con los resultados.

Las dos herramientas son de riesgo bajo: consultan o calculan.
El documento justifica por qué no requieren aprobación humana
y establece cómo revisar las trazas y actuar ante fallos.

Para ejecutar desde la raíz del repositorio, con el entorno
virtual activo y `API_KEY` configurada en `.env`:

```bash
python -m src.agente_con_herramientas
```

Este comando consulta a Gemini, consume cuota y agrega una traza
si la interacción termina correctamente.
## Bloque 24: indexación del corpus y persistencia en Chroma

El archivo `indexar_corpus.py` contiene cinco documentos cortos sobre
el cliente modular, las credenciales, los costos, las herramientas
del agente y las pruebas unitarias.

Utiliza `RecursiveCharacterTextSplitter` con fragmentos de hasta
200 caracteres y un solapamiento de 30 caracteres. Se eligió el
corte recursivo para respetar los límites entre párrafos y palabras.

Los embeddings se generan con `models/gemini-embedding-001`.
Chroma guarda el índice en `vectorstore/`, dentro de la colección
`corpus_proyecto`.

### Generar el índice

Desde la raíz del proyecto, con el entorno virtual activo,
las dependencias instaladas y `API_KEY` configurada en `.env`:

```bash
python -u indexar_corpus.py
```

Este comando realiza llamadas reales a la API y consume cuota.
Debe ejecutarse una vez para crear el índice; repetirlo puede
agregar fragmentos duplicados a la colección existente.

### Comprobar la persistencia

En un nuevo proceso de Python, desde la raíz del proyecto:

```bash
python -c "from langchain_chroma import Chroma; from indexar_corpus import DIRECTORIO_INDICE; indice = Chroma(collection_name='corpus_proyecto', persist_directory=str(DIRECTORIO_INDICE)); print('Fragmentos recuperados del disco:', indice._collection.count())"
```

Resultado verificado: cinco documentos, cinco fragmentos generados
y cinco fragmentos recuperados del disco.

La comprobación no vuelve a generar embeddings ni consume cuota.
La carpeta `vectorstore/` está excluida mediante `.gitignore`;
el índice se reconstruye ejecutando el script.