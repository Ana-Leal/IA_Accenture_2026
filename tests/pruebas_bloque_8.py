# Permite localizar la raíz del repositorio.
import sys
from pathlib import Path

# Permite importar el módulo desde src.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Permite comparar decimales considerando pequeñas diferencias de precisión.
from math import isclose

# Importa únicamente la función que vamos a probar.
from src.consumir_gemini import calcular_costo


# Representa los metadatos ficticios del ejemplo del curso.
datos = {
    "usageMetadata": {
        "promptTokenCount": 850,
        "candidatesTokenCount": 320,
        "totalTokenCount": 1170
    }
}

# Define precios ficticios en dólares por token.
precio_entrada = 0.00000010
precio_salida = 0.00000040

# Calcula el costo del ejemplo.
costo = calcular_costo(datos, precio_entrada, precio_salida)

# Verifica el resultado esperado: 0.000085 + 0.000128.
assert isclose(costo, 0.000213, rel_tol=1e-9)
print(f"CORRECTO: costo del ejemplo = USD {costo:.6f}")

# Duplica ambos precios para comprobar que el costo también se duplica.
costo_doble = calcular_costo(
    datos,
    precio_entrada * 2,
    precio_salida * 2
)

# Verifica que el resultado responde al cambio de precios.
assert isclose(costo_doble, 0.000426, rel_tol=1e-9)
print(f"CORRECTO: precios duplicados = USD {costo_doble:.6f}")

# Comprueba que la ausencia de metadatos produzca un error controlado.
try:
    calcular_costo({}, precio_entrada, precio_salida)
except RuntimeError as error:
    print("CORRECTO: datos de uso faltantes:", error)
else:
    raise AssertionError("No se detectó la ausencia de datos de uso.")

print("\nTodas las pruebas del bloque 8 pasaron.")