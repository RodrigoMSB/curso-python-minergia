# Análisis Avanzado de Datos con Python

Material del curso que **Xpertis** dicta para la **Subsecretaría de Energía de Chile**.

Son 24 horas cronológicas en ocho sesiones de tres horas, online por Zoom. Los laboratorios se
ejecutan en Google Colab, así que **no tienes que instalar nada**. Basta el navegador y una
cuenta de Google.

Todo el curso trabaja sobre un mismo caso, el **Observatorio de Datos Energéticos**, con datos
del Sistema Eléctrico Nacional.

> **Los datos son sintéticos.** Están hechos para el curso, son verosímiles y se parecen en
> orden de magnitud al sistema real, pero ninguna central corresponde a una instalación
> existente y ninguna cifra debe citarse como dato del sector.

## Los módulos

| Módulo | Horas | Laboratorio | Guía | De qué trata |
|---|---|---|---|---|
| **00** · Python básico | 1 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo00/lab.ipynb) | [Guía](modulos/modulo00/guia_alumno.pdf) | Variables, listas, diccionarios, decisiones y funciones. Opcional, para quien nunca programó |
| **01** · Importar y unir datos | 2 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo01/lab.ipynb) | [Guía](modulos/modulo01/guia_alumno.pdf) | Traer datos desde CSV, Excel, una API y una base SQL, y unir dos tablas |
| **02** · Manipulación de datos | 4 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo02/lab.ipynb) | [Guía](modulos/modulo02/guia_alumno.pdf) | Filtrar, agrupar, pivotar y responder preguntas con una tabla |
| **03** · Limpieza y análisis exploratorio | 4 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo03/lab.ipynb) | [Guía](modulos/modulo03/guia_alumno.pdf) | Diagnosticar un archivo nuevo antes de calcularle nada |
| **04** · Minería de datos | 4 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo04/lab.ipynb) | [Guía](modulos/modulo04/guia_alumno.pdf) | Distancias, reglas de asociación y patrones en secuencias |
| **05** · Aprendizaje no supervisado | 4 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo05/lab.ipynb) | [Guía](modulos/modulo05/guia_alumno.pdf) | Agrupar sin respuesta correcta, con K-Means, PCA, DBSCAN y LDA |
| **06** · Visualización de datos | 4 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo06/lab.ipynb) | [Guía](modulos/modulo06/guia_alumno.pdf) | Matplotlib, Seaborn y Plotly, y cómo se revisa un gráfico antes de mandarlo |
| **07** · Caso integrador | 2 h | [Abrir en Colab](https://colab.research.google.com/github/RodrigoMSB/curso-python-minergia/blob/main/modulos/modulo07/lab.ipynb) | [Guía](modulos/modulo07/guia_alumno.pdf) | Un informe de cierre de año, de principio a fin |

## Cómo se abre un laboratorio

1. Haz clic en **Abrir en Colab** del módulo que corresponda. El notebook se abre en tu
   navegador.
2. Colab avisa que **el cuaderno no lo creó Google**, porque viene de este repositorio y no de
   ellos. Es lo esperable. Pulsa **Ejecutar de todos modos**.
3. Ejecuta las celdas **en orden**, de arriba hacia abajo. Una celda se ejecuta con el botón de
   play de la izquierda, o poniéndote encima y apretando **Shift + Enter**.
4. La primera celda de cada laboratorio deja listos los datos. Si te la saltas, las demás dan
   error.
5. Para conservar lo que escribas, usa **Archivo, Guardar una copia en Drive**. La copia queda
   en tu Drive y el original no se toca.

Si algo sale mal y quieres empezar de nuevo, **Entorno de ejecución, Reiniciar y ejecutar
todo**. No se rompe nada, y un error en rojo tampoco rompe nada.

## Las guías

Cada módulo tiene una guía en PDF pensada para leer **después** de la clase. Trae la
explicación escrita de cada tema, el mismo código y las mismas salidas que viste en pantalla,
los ejercicios con su solución, una tabla de referencia rápida, y los errores más comunes con
el mensaje tal como aparece.

Durante la clase conviene mirar la pantalla y ejecutar, que es donde se aprende. La guía está
para después.

## Los datos

Los laboratorios generan sus propios datos dentro del notebook, así que funcionan sin descargar
nada. Esta carpeta trae los mismos archivos por si quieres trabajarlos aparte.

| Archivo | Contenido |
|---|---|
| `datos/centrales.csv` · `.xlsx` | Tabla maestra de 20 centrales. El `.xlsx` trae una hoja `notas` |
| `datos/generacion.csv` | Generación horaria por central, 2024 |
| `datos/demanda.csv` | Demanda horaria por región, 2024 |
| `datos/demanda_sucia.csv` | El anterior con defectos deliberados, separador `;` |
| `datos/demanda.db` | SQLite con las tablas `demanda` y `regiones` |
| `datos/mantenimiento.csv` | Bitácora de 600 eventos de mantenimiento, 2024 |
| `datos/api/precios_nudo.json` | Respuesta simulada de una API REST, enero de 2024 |
| `datos/generacion_2025.csv` · `demanda_2025.csv` | Los datos del caso integrador |

Separador coma, codificación UTF-8, fechas ISO y decimales con punto. La única excepción es
`demanda_sucia.csv`, cuyos defectos son a propósito.

Los archivos se regeneran con `python scripts/generar_datos.py`, que necesita `pandas`, `numpy`
y `openpyxl`. El generador es determinista, la semilla está fija, y dos corridas producen
archivos idénticos.

## Convenciones del material

- Los nombres de columnas, de centrales y de archivos van **sin tilde**, para que una tilde de
  diferencia no se convierta en un error difícil de encontrar.
- Los decimales van con **punto** en el código, que es como los escribe Python, y con coma en
  el texto de las guías, que es como se escriben en Chile.
- Cada laboratorio es independiente. No hace falta haber terminado el anterior para abrir el
  siguiente.
