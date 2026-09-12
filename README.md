# Análisis Avanzado de Datos con Python

Material del curso dictado por **Xpertis** para la **Subsecretaría de Energía de Chile**, construido sobre el caso conductor del **Observatorio de Datos Energéticos (ODE)**.

## Laboratorios

Los laboratorios se ejecutan en Google Colab.

| # | Laboratorio | Notebook | Colab |
|---|-------------|----------|-------|
| 00 | Nivelación en Python | [`labs/lab00_nivelacion.ipynb`](labs/lab00_nivelacion.ipynb) | |
| 01 | Importar y unir datos | [`labs/lab01_importar_unir.ipynb`](labs/lab01_importar_unir.ipynb) | |
| 02 | Manipulación de datos | [`labs/lab02_manipulacion.ipynb`](labs/lab02_manipulacion.ipynb) | |
| 03 | Limpieza y análisis exploratorio | [`labs/lab03_limpieza_eda.ipynb`](labs/lab03_limpieza_eda.ipynb) | |
| 04 | Data mining | [`labs/lab04_data_mining.ipynb`](labs/lab04_data_mining.ipynb) | |
| 05 | Aprendizaje no supervisado | [`labs/lab05_no_supervisado.ipynb`](labs/lab05_no_supervisado.ipynb) | |
| 06 | Visualización de datos | [`labs/lab06_visualizacion.ipynb`](labs/lab06_visualizacion.ipynb) | |
| 07 | Caso integrador | [`labs/lab07_integrador.ipynb`](labs/lab07_integrador.ipynb) | |

## Datos

Todos los datos son **sintéticos**. Las cifras son verosímiles para el Sistema Eléctrico Nacional, pero ninguna central corresponde a una instalación real.

| Archivo | Contenido |
|---------|-----------|
| `datos/centrales.csv` · `.xlsx` | Tabla maestra de 20 centrales (el `.xlsx` incluye una hoja `notas`) |
| `datos/generacion.csv` | Generación horaria por central, año 2024 |
| `datos/demanda.csv` | Demanda horaria por región, año 2024 |
| `datos/demanda_sucia.csv` | `demanda.csv` con defectos plantados (separador `;`) |
| `datos/demanda.db` | SQLite con las tablas `demanda` y `regiones` |
| `datos/mantenimiento.csv` | Bitácora de 600 eventos de mantenimiento, año 2024 |
| `datos/api/precios_nudo.json` | Respuesta simulada de una API REST, enero 2024 |
| `datos/generacion_2025.csv` · `demanda_2025.csv` | Datos del caso integrador, año 2025 |
| `datos/grande/` | Dataset grande, **no versionado** (ver más abajo) |

Convenciones: separador coma, codificación UTF-8, fechas ISO `YYYY-MM-DD` y decimales con punto. La única excepción es `demanda_sucia.csv`, cuyos defectos son deliberados.

## Regenerar los datos

El proyecto usa **Python 3.13** gestionado con [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                      # crea el entorno e instala dependencias
uv run python scripts/generar_datos.py       # regenera todo datos/
```

El generador es **determinista**: la semilla está fija en `2026` y dos ejecuciones producen archivos idénticos byte a byte. Para regenerar después de cambiar el script, basta con volver a ejecutarlo.

### Verificar un laboratorio

Los notebooks se verifican con el arnés `scripts/probar_lab.py`, que revisa el formato y los ejecuta de arriba a abajo contra los datos locales, sin tocar el archivo del repo.

```bash
uv sync --group dev                                              # una sola vez
uv run --group dev python scripts/probar_lab.py labs/lab01_importar_unir.ipynb
```

El grupo `dev` fija **pandas 2.x**, que es la versión que trae Google Colab, de modo que el arnés verifique los notebooks contra lo mismo que va a ejecutar el participante.

### Dataset grande

`datos/grande/generacion_grande.csv` tiene ~8,8 millones de filas (200 centrales × 5 años) y **no se versiona**. Se genera en local:

```bash
uv run python scripts/generar_datos.py --grande        # todo, incluido el grande
uv run python scripts/generar_datos.py --solo-grande   # únicamente el grande
```

La función que lo produce está aislada y se puede importar sin efectos secundarios, de modo que el lab 01 la reutiliza para generar el archivo directamente en Colab:

```python
from generar_datos import generar_dataset_grande
generar_dataset_grande("generacion_grande.csv")
```

---

Material propietario de Xpertis. Uso restringido a los participantes del curso.
