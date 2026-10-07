import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

INK, MUTED, GRID, SURF = "#202124", "#5F6368", "#E3E3E3", "#FFFFFF"
# Rampa ordinal azul (chica, mediana, grande)
CHICA, MEDIANA, GRANDE = "#9ec5f4", "#3987e5", "#104281"
GRIS = "#E8EAED"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "text.color": INK,
                     "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED})

from estilo import save

def titulo(ax, t, sub):
    ax.text(0, 1.18, t, transform=ax.transAxes, fontsize=15, fontweight="bold", color=INK)
    ax.text(0, 1.07, sub, transform=ax.transAxes, fontsize=11, color=MUTED)

# ---------- Paso 2 · Potencia por horas ----------
fig, ax = plt.subplots(figsize=(9, 4))
ax.add_patch(Rectangle((0, 0), 24, 300, facecolor="#cde2fb", edgecolor=MEDIANA, linewidth=2))
ax.text(12, 150, "7.200 MWh", ha="center", va="center", fontsize=22, fontweight="bold", color="#0d366b")
ax.text(12, 105, "la energía es el área", ha="center", va="center", fontsize=11, color=MUTED)
ax.annotate("", xy=(-1.2, 300), xytext=(-1.2, 0), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
ax.text(-1.8, 150, "potencia\n300 MW", ha="right", va="center", fontsize=11)
ax.annotate("", xy=(24, -28), xytext=(0, -28), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
ax.text(12, -52, "tiempo  24 horas", ha="center", va="top", fontsize=11)
ax.set_xlim(-9, 27); ax.set_ylim(-95, 360); ax.axis("off")
titulo(ax, "Potencia por tiempo da energía", "300 MW funcionando 24 horas producen 300 × 24 = 7.200 MWh")
save(fig, "lab00_paso2_energia")

# ---------- Recta de cortes ----------
def recta(ax, cortes, puntos=None, marcador=None, nota100=False):
    c1, c2 = cortes
    zonas = [(0, c1, CHICA, "chica"), (c1, c2, MEDIANA, "mediana"), (c2, 500, GRANDE, "grande")]
    for a, b, col, lab in zonas:
        ax.add_patch(Rectangle((a, 0), b - a, 1, facecolor=col, edgecolor=SURF, linewidth=2))
        ax.text((a + b) / 2, 0.5, lab, ha="center", va="center", fontsize=13, fontweight="bold",
                color=INK if col == CHICA else "white")
    for c in cortes:
        ax.plot([c, c], [-0.15, 1.15], color=INK, lw=1.5)
        ax.text(c, -0.32, f"{c} MW", ha="center", va="top", fontsize=11, fontweight="bold")
    for v in (0, 500):
        ax.text(v, -0.32, f"{v}", ha="center", va="top", fontsize=10, color=MUTED)
    if marcador:
        v, lab = marcador
        ax.annotate(lab, xy=(v, 1.0), xytext=(v, 1.75), ha="center", fontsize=12, fontweight="bold",
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    if nota100:
        ax.annotate("100 justo ya es mediana", xy=(100, 0.05), xytext=(165, -0.95), fontsize=10, color=MUTED,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
    if puntos:
        for v, nom in puntos:
            ax.plot(v, 1.45, "o", ms=11, color=INK, mec=SURF, mew=2, zorder=5)
            ax.text(v, 1.68, f"{v}", ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_xlim(-15, 515); ax.set_ylim(-1.2, 2.3); ax.axis("off")

fig, ax = plt.subplots(figsize=(9, 3.4))
recta(ax, (100, 300), marcador=(230, "230 MW"), nota100=True)
titulo(ax, "Dos cortes separan las tres categorías", "Una central de 230 MW cae en mediana")
save(fig, "lab00_paso5_cortes")

# ---------- Paso 6 · Cinco centrales, dos criterios ----------
pot = [420, 230, 160, 375, 45]
def cuenta(c1, c2):
    ch = sum(p < c1 for p in pot); gr = sum(p >= c2 for p in pot); return ch, len(pot) - ch - gr, gr
fig, axs = plt.subplots(2, 1, figsize=(9, 6.2))
for ax, cortes, tit in [(axs[0], (100, 300), "Con cortes en 100 y 300 MW"), (axs[1], (100, 400), "Con el corte de grande en 400 MW")]:
    recta(ax, cortes, puntos=[(p, "") for p in pot])
    ch, me, gr = cuenta(*cortes)
    ax.text(0, 2.45, tit, fontsize=13, fontweight="bold")
    ax.text(515, 2.45, f"chica {ch}   ·   mediana {me}   ·   grande {gr}", ha="right", fontsize=12, color=INK)
axs[1].annotate("375 pasa a mediana", xy=(375, 1.45), xytext=(250, 2.05), fontsize=10, color=MUTED, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
fig.subplots_adjust(hspace=0.55)
fig.text(0.125, 0.99, "El corte lo elige quien analiza", fontsize=15, fontweight="bold")
fig.text(0.125, 0.955, "Los mismos cinco datos dan otro conteo si cambia el corte", fontsize=11, color=MUTED)
save(fig, "lab00_paso6_criterio")

# ---------- Paso 7 · Factor de planta ----------
nom = ["Río Manso Alto", "Bahía Norte", "Pampa Alta", "Cerro Negro", "Respaldo Cordillera"]
p = [420, 375, 230, 160, 45]; f = [0.56, 0.50, 0.25, 0.34, 0.03]
mx = [x * 24 for x in p]; real = [x * 24 * y for x, y in zip(p, f)]
fig, ax = plt.subplots(figsize=(9, 4.2))
y = list(range(len(nom)))[::-1]
ax.barh(y, mx, height=0.55, color=GRIS, edgecolor=SURF, linewidth=2)
ax.barh(y, real, height=0.55, color=MEDIANA, edgecolor=SURF, linewidth=2)
for yi, m, r, fi in zip(y, mx, real, f):
    rr = (f"{r:,.1f}" if round(r, 1) != int(r) else f"{int(r):,}").replace(",", "X").replace(".", ",").replace("X", ".")
    ax.text(m + 150, yi, "produce " + rr + " de " + f"{m:,.0f}".replace(",", ".") + f" MWh  ({int(fi*100)} %)",
            va="center", fontsize=10, color=INK)
ax.set_yticks(y); ax.set_yticklabels(nom, fontsize=11, color=INK)
ax.set_xlim(0, 16500); ax.set_xticks([])
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(GRID)
ax.add_patch(Rectangle((0, -1.12), 380, 0.28, color=GRIS)); ax.text(560, -0.98, "lo máximo en un día", fontsize=10, color=MUTED, va="center")
ax.add_patch(Rectangle((4600, -1.12), 380, 0.28, color=MEDIANA)); ax.text(5160, -0.98, "lo que produce de verdad", fontsize=10, color=MUTED, va="center")
ax.set_ylim(-1.3, 4.6)
titulo(ax, "El factor de planta es la parte que se llena", "Energía de un día, comparada con lo máximo que podría producir cada central")
save(fig, "lab00_paso7_factor")

# ---------- Paso 8 · La conclusión ----------
partes = [(10144.8, GRANDE, "grandes", "2 centrales"), (2685.6, MEDIANA, "medianas", "2 centrales"), (32.4, CHICA, "chica", "1 central")]
tot = sum(x for x, *_ in partes)
fig, ax = plt.subplots(figsize=(9, 2.8))
x0 = 0
for v, col, lab, n in partes:
    ax.barh(0, v, left=x0, height=0.6, color=col, edgecolor=SURF, linewidth=2)
    x0 += v
ax.text(10144.8 / 2, 0, "grandes  79 %", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
ax.text(10144.8 + 2685.6 / 2, 0, "medianas\n21 %", ha="center", va="center", color="white", fontsize=11, fontweight="bold")
ax.annotate("chica  0,3 %", xy=(tot - 10, 0.3), xytext=(tot - 600, 0.7), fontsize=10, color=MUTED, ha="right",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
ax.text(10144.8 / 2, -0.55, "Río Manso Alto y Bahía Norte\n10.144,8 MWh", ha="center", va="top", fontsize=10, color=INK)
ax.text(10144.8 + 2685.6 / 2, -0.55, "Pampa Alta y Cerro Negro\n2.685,6 MWh", ha="center", va="top", fontsize=10, color=INK)
ax.set_xlim(0, tot); ax.set_ylim(-1.3, 1.0); ax.axis("off")
titulo(ax, "Dos centrales de cinco producen casi el 80 % de la energía", "Energía de un día por categoría, 12.862,8 MWh en total")
save(fig, "lab00_paso8_conclusion")
print("ok")
