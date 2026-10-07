"""Genera los 24 diagramas de los cuadernos guiados.

Se corre desde la raíz del repositorio.
    python scripts/diagramas/generar.py
Cada imagen queda en la carpeta img del lab que le corresponde.
"""
import os, runpy, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

for script in ["introduccion", "lab00", "lab01", "lab02", "lab03", "lab04"]:
    print("Generando", script)
    runpy.run_path(os.path.join(AQUI, script + ".py"), run_name="__main__")
print("Listo")
