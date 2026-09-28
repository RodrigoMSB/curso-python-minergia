#!/usr/bin/env python3
"""Comprueba que datos/ sea idéntico a lo que generan los notebooks.

    python scripts/verificar_datos.py

Ejecuta la celda Datos del curso de cada notebook en un directorio temporal y
compara cada archivo que escribe contra el de datos/. La comparación es por hash,
salvo centrales.xlsx, que se compara por contenido, hoja por hoja, porque el
archivo guarda la hora en que se escribió y esa hora cambia en cada corrida.

Termina con código 1 si algún archivo difiere o falta.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
MODULOS = ["01", "02", "03", "04", "05", "06", "07"]


def celda_de_datos(modulo):
    nb = json.loads((RAIZ / f"modulos/modulo{modulo}/lab.ipynb").read_text(encoding="utf-8"))
    for c in nb["cells"]:
        fuente = "".join(c["source"])
        # Desde el SPEC-20 la celda de los labs 01 a 06 lleva el rótulo Inicio.
        if re.match(r"#@title (Inicio · )?Datos del curso", fuente):
            return fuente
    raise SystemExit(f"El Lab {modulo} no tiene celda de datos")


def huella(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def mismo_excel(a, b):
    hojas_a = pd.read_excel(a, sheet_name=None)
    hojas_b = pd.read_excel(b, sheet_name=None)
    return (list(hojas_a) == list(hojas_b)
            and all(hojas_a[h].equals(hojas_b[h]) for h in hojas_a))


def main():
    fallas = 0
    for modulo in MODULOS:
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-c", celda_de_datos(modulo)], cwd=tmp,
                               capture_output=True, text=True)
            if r.returncode != 0:
                print(f"Lab {modulo}  la celda de datos falló")
                print(r.stderr[-800:])
                fallas += 1
                continue
            for archivo in sorted(Path(tmp).iterdir()):
                destino = DATOS / archivo.name
                if not destino.exists():
                    estado = "FALTA en datos/"
                elif archivo.suffix == ".xlsx":
                    estado = "igual" if mismo_excel(archivo, destino) else "DISTINTO"
                else:
                    estado = "igual" if huella(archivo) == huella(destino) else "DISTINTO"
                if estado != "igual":
                    fallas += 1
                print(f"Lab {modulo}  {archivo.name:24} {estado}")
    print("RESULTADO", "todo igual" if fallas == 0 else f"{fallas} diferencias")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
