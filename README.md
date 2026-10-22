# Plantilla de repositorio base — Especialización en Desarrollo con IA Generativa (Accenture)

Esta es la estructura base del proyecto, que se amplía bloque a bloque hasta llegar a la aplicación completa del Gate 3.

## Cómo empezar

1. Crea un entorno virtual de Python y actívalo.
2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Copia `.env.example` a un archivo llamado `.env`.
4. Configura tu credencial en la variable `API_KEY` del archivo `.env`.

El archivo `.env` contiene credenciales y no debe subirse al repositorio.

## Estructura de carpetas

- `src/`: código fuente del proyecto.
- `docs/`: documentación técnica y evidencias.
- `docs/evidencias_bloque7/`: capturas de las pruebas del bloque 7.
- `docs/evidencias_bloque8/`: diagrama del bloque 8 y documento de decisión de arquitectura del bloque 9.
- `tests/`: pruebas locales y script de comparación de modelos.
- `requirements.txt`: dependencias de Python.
- `.env.example`: ejemplo de configuración sin credenciales reales.
- `.gitignore`: excluye archivos como `.env`, el entorno virtual y archivos temporales.

## Reglas del proyecto

- No incluir contraseñas, llaves de API ni tokens en los archivos que se suben.
- Mantener un entorno virtual propio para el proyecto.
- Registrar los avances mediante commits y subirlos a GitHub.

## Evidencias de la primera petición autenticada

Estas evidencias están directamente dentro de `docs/`:

- [Registro de la primera petición](docs/evidencia-primera-peticion.md)
- [Captura de la petición](docs/peticion.png)
- [Captura de la respuesta](docs/respuesta.png)

## Bloque 7: validación y manejo de errores

El módulo `src/consumir_gemini.py` valida la pregunta antes de enviarla
y maneja errores de conexión, tiempo de espera, estado HTTP,
JSON inválido y campos o elementos faltantes en la respuesta.

### Ejecutar la consulta real

Con el entorno virtual activo, las dependencias instaladas y
la variable `API_KEY` configurada en `.env`, ejecuta desde la raíz
del repositorio:

```bash
python src/consumir_gemini.py
```

Este comando realiza una petición real a Gemini.

### Ejecutar las pruebas locales

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python tests/pruebas_bloque_7.py
```

Estas pruebas simulan errores de conexión, tiempo de espera,
JSON inválido, campos faltantes y listas vacías.
No realizan llamadas a la API.

### Evidencias del bloque 7

Estas capturas están dentro de `docs/evidencias_bloque7/`:

- [Tiempo de espera controlado](docs/evidencias_bloque7/timeout01.png)
- [Credencial inválida, pregunta vacía y consulta válida](docs/evidencias_bloque7/02_tres_pruebas.png)
- [Pruebas locales de errores controlados](docs/evidencias_bloque7/03_errores_controlados.png)
- [Commit y push del bloque 7](docs/evidencias_bloque7/04_commit_push.png)
- [Pruebas locales con timeout simulado](docs/evidencias_bloque7/05_timeout_simulado.png)

## Bloque 8: arquitectura de la miniaplicación

- [Ver diagrama de arquitectura](docs/evidencias_bloque8/diagrama_arquitectura_bloque8.png)

El cálculo de costo se prueba con datos ficticios mediante:

```bash
python tests/pruebas_bloque_8.py
```

Estas pruebas comprueban el costo del ejemplo, el efecto de duplicar
los precios y el manejo de datos de uso faltantes.
No realizan llamadas a la API.

## Bloque 9: comparación y elección del modelo

- [Ver comparación, resultados y decisión de arquitectura](docs/evidencias_bloque8/decision-arquitectura.md)

Se seleccionó Gemini 3.5 Flash-Lite como modelo predeterminado
para el prototipo. El documento explica los resultados,
las incidencias y las limitaciones de la evaluación.

El documento está junto al diagrama del bloque 8, que se conserva
como referencia de la arquitectura utilizada en la comparación.

### Ejecutar la comparación

El script `tests/comparar_modelos_bloque_9.py` realiza llamadas
reales a la API para los modelos configurados en su lista `modelos`.

Actualmente esa lista contiene Gemini 3.6 Flash, utilizado como
candidato alternativo. Los resultados anteriores de Gemini 3.5
Flash-Lite y Gemini 3.8 Flash se conservan en el documento de decisión.

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y `API_KEY` configurada, ejecuta:

```bash
python -u tests/comparar_modelos_bloque_9.py
```

El script realiza cuatro intentos de la consulta del lavaplatos
y una consulta para cada uno de los otros dos casos: mueble y humedad.
Imprime el promedio de latencia si los cuatro primeros intentos
son exitosos y registra los fallos por separado.

### Repetir únicamente la consulta del mueble

Para consultar el caso del mueble con Gemini 3.6 Flash:

```bash
python -u tests/comparar_modelos_bloque_9.py --solo-mueble
```

Esta opción realiza una sola petición real y no ejecuta
las demás consultas.

## Iniciar la aplicación

Desde la raíz del repositorio, con las dependencias instaladas y
la variable `API_KEY` configurada en `.env`:

En Git Bash de Windows, activa el entorno virtual:

```bash
source venv/Scripts/activate
```

Ejecuta la aplicación:

```bash
python main.py
```

Escribe tu necesidad y presiona Enter. La aplicación realizará
una consulta real a Gemini y mostrará la respuesta.