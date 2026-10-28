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