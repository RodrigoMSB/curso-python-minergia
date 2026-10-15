#!/usr/bin/env python3
"""Genera las dos planillas de fichas que usan los Pasos 4 y 5 del Lab 01 guiado.

    python scripts/generar_fichas.py

Las dos salen de datos/centrales.csv y quedan en datos/.

fichas.csv es la planilla de fichas que mantiene otra área. Tiene las mismas columnas
que centrales.csv y le faltan tres centrales, Eólica Loma Fría, Central Vega Azul y
Diésel Respaldo Cordillera. Queda con 17 filas.

fichas_repetidas.csv es la misma planilla con sus dos primeras centrales anotadas dos
veces, Central Río Manso Alto y Central Salto Verde. Queda con 19 filas.

Necesita pandas.
"""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "datos"
SIN_FICHA = ["Eólica Loma Fría", "Central Vega Azul", "Diésel Respaldo Cordillera"]


def main():
    centrales = pd.read_csv(DATOS / "centrales.csv")
    fichas = centrales[~centrales["central"].isin(SIN_FICHA)].reset_index(drop=True)
    repetidas = pd.concat([fichas, fichas.head(2)], ignore_index=True)
    assert len(fichas) == 17 and len(repetidas) == 19
    fichas.to_csv(DATOS / "fichas.csv", index=False)
    repetidas.to_csv(DATOS / "fichas_repetidas.csv", index=False)
    print("fichas.csv          ", len(fichas), "filas")
    print("fichas_repetidas.csv", len(repetidas), "filas")


if __name__ == "__main__":
    main()
