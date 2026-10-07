"""Estilo común de los diagramas de los cuadernos guiados. Se corre desde la raíz del repo."""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import pandas as pd

INK, MUTED, GRID, SURF = "#202124", "#5F6368", "#DADCE0", "#FFFFFF"
HEAD = "#F1F3F4"
# Pares (fuerte, tinte) para seguir a cada fila con su color
AZUL = ("#1a6fd4", "#dbe9fb"); AMBAR = ("#d99a00", "#fdf0c8"); MORADO = ("#7b4fc9", "#ece2fa")
VERDE = ("#1e8e3e", "#dcefe0")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK})

def es(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

CARPETAS = {"conceptos": "modulos/conceptos/img", "bienvenida": "modulos/bienvenida/img",
            "lab00": "modulos/modulo00/img", "lab01": "modulos/modulo01/img", "lab02": "modulos/modulo02/img",
            "lab03": "modulos/modulo03/img", "lab04": "modulos/modulo04/img"}

def save(fig, name):
    """Guarda el diagrama en la carpeta img del lab que indica el prefijo del nombre."""
    carpeta = CARPETAS[name.split("_")[0]]
    os.makedirs(carpeta, exist_ok=True)
    fig.savefig(os.path.join(carpeta, f"{name}.png"), dpi=160, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)

def lienzo(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w * 10); ax.set_ylim(0, h * 10); ax.axis("off")
    return fig, ax

def titulo(ax, t, sub, w, h):
    ax.text(0, h * 10 + 6, t, fontsize=15, fontweight="bold")
    ax.text(0, h * 10 + 1.5, sub, fontsize=11, color=MUTED)

def tabla(ax, x, y, cols, anchos, filas, colores, rh=4.2, rotulo=None, alin=None):
    """Dibuja una tabla con la esquina superior izquierda en (x, y). Devuelve el centro vertical de cada fila."""
    alin = alin or ["left"] * len(cols)
    if rotulo:
        ax.text(x, y + 1.6, rotulo, fontsize=11, fontweight="bold", va="bottom")
    cx = x
    for c, w, a in zip(cols, anchos, alin):
        ax.add_patch(Rectangle((cx, y - rh), w, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
        ax.text(cx + (w - 1 if a == "right" else 1), y - rh / 2, c, fontsize=10, fontweight="bold",
                color=MUTED, va="center", ha=a, family="DejaVu Sans Mono")
        cx += w
    centros = []
    for i, (fila, col) in enumerate(zip(filas, colores)):
        yy = y - rh * (i + 2)
        cx = x
        fuerte, tinte = col if col else (GRID, "#F8F9FA")
        for v, w, a in zip(fila, anchos, alin):
            ax.add_patch(Rectangle((cx, yy), w, rh, facecolor=tinte, edgecolor=SURF, lw=1.5))
            ax.text(cx + (w - 1 if a == "right" else 1), yy + rh / 2, v, fontsize=10, va="center", ha=a,
                    family="DejaVu Sans Mono", color=INK if col else "#9AA0A6")
            cx += w
        ax.add_patch(Rectangle((x - 0.9, yy), 0.9, rh, facecolor=fuerte, edgecolor=SURF, lw=1.5))
        centros.append(yy + rh / 2)
    return centros

def flecha(ax, a, b, texto=None, color=INK, rad=0.0, lw=1.4):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}"))
    if texto:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 2, texto, ha="center", va="bottom", fontsize=10,
                color=MUTED, family="DejaVu Sans Mono")


ROJO = ("#c5221f", "#fce8e6")
GRIS = ("#9AA0A6", "#F1F3F4")
