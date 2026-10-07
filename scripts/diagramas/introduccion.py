import sys
from estilo import *
import pandas as pd
D = "datos"
c = pd.read_csv(f"{D}/centrales.csv")
TEC = {"hidro": AZUL, "solar": AMBAR, "gas": MORADO, "carbon": ("#5F6368", "#E8EAED"), "eolica": VERDE, "diesel": ROJO}

def caja(ax, x, y, etiqueta, valor, col, tachado=None, nota=None):
    ax.add_patch(Rectangle((x, y), 26, 13, facecolor=col[1], edgecolor=col[0], lw=2))
    ax.add_patch(Rectangle((x + 3, y + 11.2), 20, 4.2, facecolor=SURF, edgecolor=col[0], lw=1.5))
    ax.text(x + 13, y + 13.3, etiqueta, ha="center", va="center", fontsize=11, family="DejaVu Sans Mono", fontweight="bold")
    if tachado:
        ax.text(x + 13, y + 7.6, tachado, ha="center", va="center", fontsize=12, color=MUTED, family="DejaVu Sans Mono")
        ax.plot([x + 7, x + 19], [y + 7.6, y + 7.6], color=ROJO[0], lw=2)
        ax.text(x + 13, y + 3.2, valor, ha="center", va="center", fontsize=17, fontweight="bold", family="DejaVu Sans Mono")
    else:
        ax.text(x + 13, y + 5.5, valor, ha="center", va="center", fontsize=17, fontweight="bold", family="DejaVu Sans Mono")
    if nota:
        ax.text(x + 13, y - 2.5, nota, ha="center", va="top", fontsize=10, color=MUTED)

# ---------- Conceptos Paso 4 · La caja que cambia ----------
W, H = 15, 4.4
fig, ax = lienzo(W, H)
caja(ax, 4, 16, "precio_pan", "1700", AZUL, tachado="1500", nota="Paso 4\nse guarda otro valor\ncon la misma etiqueta")
caja(ax, 46, 16, "cantidad", "3", VERDE, nota="Paso 2\nno cambió")
caja(ax, 98, 16, "total", "4500", AMBAR, nota="Paso 3\nse calculó con 1500 × 3\ny se quedó así")
ax.text(80, 22.5, "=", fontsize=26, ha="center", va="center", color=MUTED)
ax.text(38, 22.5, "×", fontsize=22, ha="center", va="center", color=MUTED)
ax.text(128, 28, "Para que el total use\nel precio nuevo,\nhay que volver a\ncorrer el Paso 3.", fontsize=11, va="top",
        fontweight="bold")
titulo(ax, "Cambiar una caja no cambia las cuentas hechas antes",
       "Python guarda el resultado del cálculo, no la fórmula como una planilla", W, H)
save(fig, "conceptos_paso4_caja")

# ---------- Conceptos Paso 8 · Listas que forman una tabla ----------
W, H = 15, 4.4
fig, ax = lienzo(W, H)
prod = ["pan", "leche", "queso"]; prec = [1500, 990, 2300]
cols = [AZUL, VERDE, AMBAR]
def lista(ax, x, y, nombre, vals):
    ax.text(x, y + 2, nombre, fontsize=11, fontweight="bold", family="DejaVu Sans Mono")
    ax.text(x, y - 3, "[", fontsize=24, va="center", color=MUTED)
    for i, (v, col) in enumerate(zip(vals, cols)):
        ax.add_patch(Rectangle((x + 3 + 11 * i, y - 6), 10, 6.4, facecolor=col[1], edgecolor=col[0], lw=1.2))
        ax.text(x + 8 + 11 * i, y - 2.8, str(v), ha="center", va="center", fontsize=11, family="DejaVu Sans Mono")
    ax.text(x + 3 + 11 * 3, y - 3, "]", fontsize=24, va="center", color=MUTED)
lista(ax, 2, 33, "producto", ['"pan"', '"leche"', '"queso"'])
lista(ax, 2, 15, "precios", prec)
flecha(ax, (44, 22), (66, 22), "pd.DataFrame")
tabla(ax, 76, 36, ["", "producto", "precio"], [6, 14, 12], [(str(i), p, str(v)) for i, (p, v) in enumerate(zip(prod, prec))],
      cols, alin=["right", "left", "right"], rotulo="almacen")
ax.text(76, 11, "Cada lista pasa a ser una columna.\nLo que estaba en la misma posición queda en la misma fila.\n"
        "Python numera las filas desde 0.", fontsize=10, va="top")
titulo(ax, "Una tabla junta varias listas una al lado de la otra", "Como una planilla con una columna por dato", W, H)
save(fig, "conceptos_paso8_tabla")

# ---------- Bienvenida Paso 6 · El filtro ----------
cs = c.sort_values(["region", "central"]).reset_index(drop=True)
W, H = 15, 7.6
fig, ax = lienzo(W, H)
filas = [(r.central, r.region, str(r.potencia_mw)) for r in cs.itertuples()]
col = [AZUL if r.region == "Biobío" else None for r in cs.itertuples()]
tabla(ax, 1, 70, ["central", "region", "potencia_mw"], [31, 16, 14], filas, col, rh=3.2, alin=["left", "left", "right"],
      rotulo="centrales  (las 20)")
flecha(ax, (66, 40), (77, 40), None)
ax.text(71.5, 44, 'region ==\n"Biobío"', ha="center", fontsize=10, family="DejaVu Sans Mono", color=MUTED)
bb = cs[cs.region == "Biobío"].sort_values("potencia_mw", ascending=False)
f2 = [(r.central, r.tecnologia, str(r.potencia_mw)) for r in bb.itertuples()]
tabla(ax, 81, 52, ["central", "tecnologia", "potencia_mw"], [31, 13, 14], f2, [AZUL] * len(f2), rh=4.2,
      alin=["left", "left", "right"], rotulo="en_la_region  (de la más grande a la más chica)")
ax.text(81, 22, "Pasan solo las filas que cumplen la condición.\nLas otras 15 siguen en la tabla original, no se borran.",
        fontsize=10.5, va="top")
titulo(ax, "Un filtro deja pasar solo las filas que cumplen una condición",
       "Las 5 centrales de Biobío, en azul en la tabla de la izquierda", W, H)
save(fig, "bienvenida_paso6_filtro")

# ---------- Bienvenida Paso 7 · La suma por tecnología ----------
orden = c.groupby("tecnologia")["potencia_mw"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 4.6))
for i, t in enumerate(orden.index):
    x0 = 0
    for r in c[c.tecnologia == t].sort_values("potencia_mw", ascending=False).itertuples():
        ax.barh(i, r.potencia_mw, left=x0, color=TEC[t][1], edgecolor=TEC[t][0], lw=1.2, height=0.62)
        if r.potencia_mw >= 120:
            ax.text(x0 + r.potencia_mw / 2, i, str(r.potencia_mw), ha="center", va="center", fontsize=9, color=INK)
        x0 += r.potencia_mw
    n = (c.tecnologia == t).sum()
    ax.text(x0 + 20, i, f"{orden[t]} MW", va="center", fontsize=12, fontweight="bold")
    ax.text(x0 + 20, i + 0.32, f"{n} central" + ("es" if n > 1 else ""), va="center", fontsize=9, color=MUTED)
ax.set_yticks(range(len(orden))); ax.set_yticklabels(orden.index, fontsize=11, family="DejaVu Sans Mono")
ax.invert_yaxis(); ax.set_xlim(0, 1500); ax.set_xticks([])
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(GRID)
ax.text(0, 1.15, "Agrupar es juntar las filas iguales y sumarlas", transform=ax.transAxes, fontsize=15, fontweight="bold")
ax.text(0, 1.06, "Cada bloque es una central con su potencia en MW. groupby las junta por tecnología y sum las suma",
        transform=ax.transAxes, fontsize=11, color=MUTED)
save(fig, "bienvenida_paso7_suma")
print("ok")
