"""Diagramas del Paso 4 del Lab 01 y del Estudio 4 del Lab 02, iguales a los de las presentaciones."""
import json
from estilo import *
from matplotlib.patches import Circle

D = "datos/"


def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)


# ---------- Lab 01 Paso 4 · inner y left como conjuntos ----------
c = pd.read_csv(D + "centrales.csv")
sin_ficha = ["Eólica Loma Fría", "Central Vega Azul", "Diésel Respaldo Cordillera"]
izq = set(c["central"])
der = set(c["central"]) - set(sin_ficha)
solo_izq, ambas, solo_der = len(izq - der), len(izq & der), len(der - izq)
assert (solo_izq, ambas, solo_der) == (3, 17, 0)
fig, axs = plt.subplots(1, 2, figsize=(10, 5.0))
casos = [("inner", "solo lo que está en las dos", "ambas"), ("left", "toda la izquierda", "izq")]
n = {"ambas": ambas, "izq": solo_izq + ambas}
for a, (how, que, k) in zip(axs, casos):
    a.set_xlim(-1.95, 1.95); a.set_ylim(-2.15, 1.7); a.set_aspect("equal"); a.axis("off")
    A = Circle((-0.6, 0), 1.25, facecolor="none", edgecolor=AZUL[0], lw=2)
    B = Circle((0.6, 0), 1.25, facecolor="none", edgecolor=AMBAR[0], lw=2)
    if k == "izq":
        a.add_patch(Circle((-0.6, 0), 1.25, facecolor=VERDE[1], edgecolor="none"))
    if k == "ambas":
        f = Circle((-0.6, 0), 1.25, facecolor=VERDE[1], edgecolor="none")
        a.add_patch(f); f.set_clip_path(Circle((0.6, 0), 1.25, transform=a.transData))
    a.add_patch(A); a.add_patch(B)
    a.text(-1.25, 0, str(solo_izq), ha="center", va="center", fontsize=15, fontweight="bold", color=ROJO[0])
    a.text(0, 0, str(ambas), ha="center", va="center", fontsize=15, fontweight="bold")
    a.text(1.25, 0, str(solo_der), ha="center", va="center", fontsize=15, fontweight="bold", color=MUTED)
    a.text(-0.6, 1.45, "un_dia", ha="center", fontsize=10, color=AZUL[0], family="DejaVu Sans Mono")
    a.text(0.6, 1.45, "fichas", ha="center", fontsize=10, color=AMBAR[0], family="DejaVu Sans Mono")
    a.text(0, -1.55, f'how="{how}"', ha="center", fontsize=12, fontweight="bold", family="DejaVu Sans Mono")
    a.text(0, -1.95, f"{que}, {n[k]} centrales", ha="center", fontsize=11, color=INK)
fig.suptitle("Qué centrales conserva cada forma de unir", x=0.02, ha="left", fontsize=15, fontweight="bold", y=1.0)
fig.text(0.02, 0.9, f"En rojo las {solo_izq} centrales que tienen generación y no tienen ficha. "
         f"A la derecha hay {solo_der}, porque todas las fichas tienen generación.",
         fontsize=11.5, color=MUTED)
fig.text(0.02, 0.01, "El dibujo cuenta centrales, no filas. Cada central del día son 24 filas, una por hora.",
         fontsize=11, color=MUTED, style="italic")
fig.subplots_adjust(top=0.86, bottom=0.07, left=0.01, right=0.99, wspace=0.04)
save(fig, "lab01_paso4_conjuntos")

# ---------- Lab 02 Estudio 4 · tres láminas ----------
d = pd.read_csv(D + "demanda.csv", parse_dates=["fecha"])
p = pd.json_normalize(json.load(open(D + "precios_nudo.json", encoding="utf-8"))["datos"])
p["fecha"] = pd.to_datetime(p["fecha"])
m = pd.merge(p, d, on=["fecha", "hora", "region"], how="inner")
glob = round(m["precio_usd_mwh"].corr(m["mwh"]), 3)
assert len(m) == 5208 and glob == 0.979


def base(ax):
    ax.set_xlabel("demanda en MWh por hora", color=MUTED, fontsize=11)
    ax.set_ylabel("precio en USD por MWh", color=MUTED, fontsize=11)
    ax.set_xlim(0, 1000); ax.set_ylim(30, 175)
    for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)


# a. todas en gris
fig, ax = plt.subplots(figsize=(13, 5.6))
ax.scatter(m["mwh"], m["precio_usd_mwh"], s=5, color="#80868B", alpha=0.45)
base(ax)
ax.text(30, 165, f"Todas las regiones juntas, correlación {es(glob, 3)}", fontsize=17, fontweight="bold", va="top")
ax.text(30, 154, f"{len(m):,}".replace(",", ".") + " filas de enero, una por hora y región. Parece una línea casi perfecta.", fontsize=12, color=MUTED, va="top")
save(fig, "lab02_paso5_a_todas")

# b. pintadas por región
orden = m.groupby("region")["mwh"].mean().sort_values().index
pal = {"Atacama": AMBAR[0], "Antofagasta": "#9334E6", "Coquimbo": VERDE[0], "Los Lagos": "#12B5CB",
       "Biobío": ROJO[0], "Valparaíso": "#E8710A", "Metropolitana": AZUL[0]}
fig, ax = plt.subplots(figsize=(13, 5.6))
for r in orden:
    g = m[m.region == r]
    ax.scatter(g["mwh"], g["precio_usd_mwh"], s=5, color=pal[r], alpha=0.5, label=r)
base(ax)
ax.legend(loc="lower right", frameon=False, markerscale=3, fontsize=10.5, title="región", title_fontsize=10.5)
ax.text(30, 165, "Los mismos puntos, pintados por región", fontsize=17, fontweight="bold", va="top")
ax.text(30, 154, "La línea la forman dos grupos, la Metropolitana arriba a la derecha\ny las otras seis regiones amontonadas abajo a la izquierda.", fontsize=12, color=MUTED, va="top")
cm = m[m.region == "Metropolitana"]
ax.annotate("Metropolitana, consume y paga\nmucho más que las demás", xy=(560, 108), xytext=(300, 118),
            fontsize=10.5, color=AZUL[0], arrowprops=dict(arrowstyle="-|>", color=AZUL[0]))
ax.annotate("las otras seis regiones", xy=(150, 55), xytext=(260, 80), fontsize=10.5, color=INK,
            arrowprops=dict(arrowstyle="-|>", color=INK))
save(fig, "lab02_paso5_b_regiones")

# ---------- Correlación por región ----------
d = pd.read_csv(D + "demanda.csv", parse_dates=["fecha"])
p = pd.json_normalize(json.load(open(D + "precios_nudo.json", encoding="utf-8"))["datos"])
p["fecha"] = pd.to_datetime(p["fecha"])
m = pd.merge(p, d, on=["fecha", "hora", "region"], how="inner")
glob = round(m["precio_usd_mwh"].corr(m["mwh"]), 3)
reg = m.groupby("region")[["precio_usd_mwh", "mwh"]].apply(lambda g: round(g["precio_usd_mwh"].corr(g["mwh"]), 3)).sort_values()
prom = m.groupby("region")["mwh"].mean()
W, H = 15, 5.0
fig, ax = lienzo(W, H)
a = fig.add_axes([0.16, 0.12, 0.5, 0.62])
cols = [AMBAR[0] if r == "Atacama" else (AZUL[0] if r == "Metropolitana" else GRIS[0]) for r in reg.index]
a.barh(list(reg.index), list(reg.values), color=cols)
a.axvline(glob, color=ROJO[0], lw=2, ls="--")
a.text(glob - 0.01, len(reg) - 0.35, f"todas juntas {es(glob, 3)}", color=ROJO[0], ha="right", fontsize=10, fontweight="bold")
for y_, v_ in enumerate(reg.values):
    if v_ > 0.85: a.text(v_ - 0.012, y_, es(v_, 3), va="center", ha="right", fontsize=9.5, color="white", fontweight="bold")
    else: a.text(v_ + 0.012, y_, es(v_, 3), va="center", fontsize=9.5)
a.set_xlim(0, 1.05); a.set_xlabel("correlación entre precio y demanda, enero de 2024", color=MUTED)
for s_ in ["top", "right"]: a.spines[s_].set_visible(False)
nota(ax, 104, 44, "Ninguna región llega al 0,979\nde todas juntas.", color=INK, size=11, fontweight="bold")
nota(ax, 104, 33, f"En enero la Metropolitana consume en\npromedio {es(prom['Metropolitana'], 0)} MWh por hora y Atacama {es(prom['Atacama'], 0)}.\nEsa diferencia de tamaño, más que la\nrelación dentro de cada región, es la\nque dibuja la línea casi recta.", color=INK, size=10.5)
nota(ax, 104, 12, "Cerca de 1 suben juntos. Cerca de 0\nno hay relación. Cerca de -1, cuando\nuno sube el otro baja.", color=MUTED, size=10)
titulo(ax, "La correlación de cada región, comparada con la de todas juntas",
       "Las siete regiones que se pueden elegir en el Estudio 4 del Lab 02", W, H)
save(fig, "lab02_paso5_c_correlaciones")
print("ok")
