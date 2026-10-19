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
- `tests/`: pruebas del código.
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

Desde la raíz del repositorio:

```bash
python tests/pruebas_bloque_7.py
```

Estas pruebas simulan errores de conexión, JSON inválido,
campos faltantes y listas vacías. No realizan llamadas a la API.

### Evidencias del bloque 7

Estas capturas están dentro de `docs/evidencias_bloque7/`:

- [Tiempo de espera controlado](docs/evidencias_bloque7/timeout01.png)
- [Credencial inválida, pregunta vacía y consulta válida](docs/evidencias_bloque7/02_tres_pruebas.png)
- [Pruebas locales de errores controlados](docs/evidencias_bloque7/03_errores_controlados.png)