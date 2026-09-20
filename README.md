# Análisis Avanzado de Datos con Python

Material del curso que **Xpertis** dicta para la **Subsecretaría de Energía de Chile**.

Son 24 horas cronológicas en seis sesiones de cuatro horas, online por Zoom, para 25
funcionarios y prestadores de servicios de la institución. Los laboratorios se ejecutan en
Google Colab, así que el participante no instala nada.

Todo el curso trabaja sobre un caso conductor único, el **Observatorio de Datos Energéticos**,
con datos sintéticos pero verosímiles del Sistema Eléctrico Nacional. Ninguna central
corresponde a una instalación real.

**El estado del material está en [ESTADO.md](ESTADO.md).** Acá solo está cómo se organiza el
repositorio y cómo se regeneran las cosas.

## Cómo se organiza

```
curso-python-minergia/
  ESTADO.md            qué está listo, qué falta y qué ya se decidió
  datos/               los datos del caso conductor
  scripts/             generar datos, ejecutar notebooks y armar las guías
  modulos/
    modulo01/
      guia_relator.pdf     la pieza principal, se escribe primero
      guia_alumno.pdf      la explicación escrita, para leer después de la clase
      lab.ipynb            el notebook que recibe el participante, sin salidas
      lab_resuelto.ipynb   la copia del relator, con salidas
      fuentes/             las fuentes LaTeX, los diagramas y las fichas de contexto
  _archivo/            material del modelo antiguo, ver _archivo/LEEME.md
```

Un módulo, una carpeta, con sus cuatro entregables a la vista.

## Los datos

| Archivo | Contenido |
|---------|-----------|
| `datos/centrales.csv` · `.xlsx` | Tabla maestra de 20 centrales, el `.xlsx` trae una hoja `notas` |
| `datos/generacion.csv` | Generación horaria por central, 2024 |
| `datos/demanda.csv` | Demanda horaria por región, 2024 |
| `datos/demanda_sucia.csv` | `demanda.csv` con defectos plantados, separador `;` |
| `datos/demanda.db` | SQLite con las tablas `demanda` y `regiones` |
| `datos/mantenimiento.csv` | Bitácora de 600 eventos de mantenimiento, 2024 |
| `datos/api/precios_nudo.json` | Respuesta simulada de una API REST, enero de 2024 |
| `datos/generacion_2025.csv` · `demanda_2025.csv` | Datos del caso integrador |

Convenciones, separador coma, codificación UTF-8, fechas ISO y decimales con punto. La única
excepción es `demanda_sucia.csv`, cuyos defectos son deliberados.

El proyecto usa **Python 3.13** gestionado con [uv](https://docs.astral.sh/uv/). El generador
es determinista, la semilla está fija en `2026` y dos corridas producen archivos idénticos.

```bash
uv sync
uv run python scripts/generar_datos.py
```

## Regenerar el material de un módulo

El notebook se entrega sin salidas y la versión resuelta sale de ejecutarlo. Los recuadros de
código y de salida de las guías **no se escriben a mano**, se generan desde el notebook
resuelto, de modo que las cifras de las guías sean siempre las de una corrida real.

```bash
uv sync --group dev                                      # una sola vez

# 1. ejecutar el notebook y dejar la versión resuelta
uv run --group dev python scripts/ejecutar_notebook.py \
    modulos/modulo01/lab.ipynb modulos/modulo01/lab_resuelto.ipynb

# 2. volcar código y salidas a fragmentos LaTeX
python3 scripts/generar_celdas.py \
    modulos/modulo01/lab_resuelto.ipynb modulos/modulo01/fuentes/celdas

# 3. compilar las guías, dos pasadas porque la portada usa posiciones absolutas
cd modulos/modulo01/fuentes
xelatex guia_relator.tex && xelatex guia_relator.tex
xelatex guia_alumno.tex  && xelatex guia_alumno.tex
mv guia_relator.pdf guia_alumno.pdf ..
```

El grupo `dev` fija **pandas 2.x**, que es la serie que trae Google Colab, para que lo que se
verifica sea lo mismo que va a ejecutar el participante.

Para las guías hace falta una instalación de TeX con **XeLaTeX**, más las tipografías Charter,
Avenir Next y Menlo, que vienen con macOS.

`scripts/verificar_tildes.py` sirve cuando hay que corregir la ortografía de una guía entera y
se quiere comprobar que no se cambió nada más que las tildes.

## Dataset grande

El Módulo 1 genera dentro del notebook un CSV de 4.380.000 filas y 141 MB para comparar pandas
con Polars. No se versiona y se crea solo si no existe.
