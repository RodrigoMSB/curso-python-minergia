"""Genera los 50 diagramas de los cuadernos guiados y de sus presentaciones.

Se corre desde la raíz del repositorio.
    python scripts/diagramas/generar.py
Cada imagen queda en la carpeta img del lab que le corresponde.
"""
import os, runpy, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

for script in ["introduccion", "lab00", "lab01", "lab02", "lab03", "lab04",
               "lab01_extra", "lab02_extra", "lab03_extra", "lab04_extra",
               "mejoras_lab01_02"]:
    print("Generando", script)
    runpy.run_path(os.path.join(AQUI, script + ".py"), run_name="__main__")
print("Listo")
