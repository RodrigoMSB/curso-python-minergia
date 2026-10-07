import sys
from estilo import *
import pandas as pd
D = "datos"

# ---------- Paso 4 · De texto a su forma correcta ----------
W, H = 15, 5.2
fig, ax = lienzo(W, H)
filas = [
    ("mwh", ["'51,95'"], "texto", '.str.replace(",", ".").astype(float)', ["51.95"], "número", AZUL),
    ("fecha", ["'01/01/2024'"], "texto", 'pd.to_datetime(..., format="%d/%m/%Y")', ["2024-01-01"], "fecha", VERDE),
    ("region", ["'  BIOBÍO'", "'los lagos '", "' Metropolitana'"], "49 formas",
     ".str.strip().str.title()", ["'Biobío'", "'Los Lagos'", "'Metropolitana'"], "7 formas", MORADO),
]
ax.text(1, 45, "columna", fontsize=10, color=MUTED, fontweight="bold")
ax.text(14, 45, "cómo llega", fontsize=10, color=MUTED, fontweight="bold")
ax.text(46, 45, "qué se le aplica", fontsize=10, color=MUTED, fontweight="bold")
ax.text(112, 45, "cómo queda", fontsize=10, color=MUTED, fontweight="bold")
y = 38
for col, antes, t1, op, despues, t2, c in filas:
    alto = 4.6 * len(antes) + 2
    ax.add_patch(Rectangle((0, y - alto + 3), W * 10 - 2, alto, facecolor=c[1], edgecolor="none"))
    ax.add_patch(Rectangle((0, y - alto + 3), 0.9, alto, facecolor=c[0], edgecolor="none"))
    ax.text(2, y, col, fontsize=11, fontweight="bold", family="DejaVu Sans Mono", va="center")
    for k, a in enumerate(antes):
        ax.text(14, y - 4.6 * k, a, fontsize=11, family="DejaVu Sans Mono", va="center", color=ROJO[0])
    ax.text(14, y - 4.6 * len(antes) + 1.2, t1, fontsize=9, color=MUTED, va="center")
    ax.text(46, y, op, fontsize=10, family="DejaVu Sans Mono", va="center")
    ax.annotate("", xy=(110, y), xytext=(100, y), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    for k, dd in enumerate(despues):
        ax.text(112, y - 4.6 * k, dd, fontsize=11, family="DejaVu Sans Mono", va="center", color=VERDE[0] if c != VERDE else INK)
    ax.text(112, y - 4.6 * len(despues) + 1.2, t2, fontsize=9, color=MUTED, va="center")
    y -= alto + 3
titulo(ax, "El archivo trae números, fechas y regiones escritos como texto",
       "Cada columna se convierte con su propia instrucción, sobre una copia del archivo", W, H)
save(fig, "lab03_paso4_tipos")

# ---------- Paso 5 · Filas repetidas ----------
W, H = 15, 4.6
fig, ax = lienzo(W, H)
antes = [("01/01/2024", "16", "Antofagasta", "69,17"), ("01/01/2024", "17", "Antofagasta", "71,96"),
         ("01/01/2024", "18", "Antofagasta", "74,81"), ("01/01/2024", "18", "Antofagasta", "74,81"),
         ("01/01/2024", "19", "Antofagasta", "80,71")]
ca = tabla(ax, 1, 38, ["fecha", "hora", "region", "mwh"], [13, 6, 13, 8], antes, [AZUL, AZUL, AZUL, ROJO, AZUL],
           alin=["left", "right", "left", "right"], rotulo="limpia  (cinco filas seguidas)")
ax.text(42, ca[3], "   ← idéntica a la anterior", fontsize=10, color=ROJO[0], va="center")
flecha(ax, (68, 25), (82, 25), "drop_duplicates()")
tabla(ax, 86, 38, ["fecha", "hora", "region", "mwh"], [13, 6, 13, 8], antes[:3] + antes[4:], [AZUL] * 4,
      alin=["left", "right", "left", "right"], rotulo="sin_repetidas")
ax.text(86, 9, "Se queda la primera y se va la copia.\nEn todo el archivo son 20 filas, y quedan las 61.488 esperadas.",
        fontsize=10, va="top")
titulo(ax, "Una fila repetida suma dos veces la misma hora",
       "duplicated marca las filas idénticas a una anterior y drop_duplicates las quita", W, H)
save(fig, "lab03_paso5_repetidas")

# ---------- Paso 6 · Cuatro formas de rellenar ----------
horas = list(range(12))
venia = [177.0, None, None, 166.0, 164.7, 179.2, 191.4, 222.5, None, None, 247.4, 259.6]
estr = {
    "borrar la fila": [v for v in venia],
    "poner cero": [0 if v is None else v for v in venia],
    "repetir el valor anterior": [177.0, 177.0, 177.0, 166.0, 164.7, 179.2, 191.4, 222.5, 222.5, 222.5, 247.4, 259.6],
    "trazar una recta": [177.0, 173.3, 169.7, 166.0, 164.7, 179.2, 191.4, 222.5, 230.8, 239.1, 247.4, 259.6],
}
prom = {"borrar la fila": "227,3", "poner cero": "220,5", "repetir el valor anterior": "227,6", "trazar una recta": "227,5"}
fig, axs = plt.subplots(1, 4, figsize=(15, 3.6), sharey=True, gridspec_kw={"wspace": 0.12})
huecos = [1, 2, 8, 9]
for a, (nom, serie) in zip(axs, estr.items()):
    for h in huecos:
        a.axvspan(h - 0.5, h + 0.5, color=AMBAR[1], lw=0)
    xs = [h for h, v in zip(horas, venia) if v is not None]; ys = [v for v in venia if v is not None]
    a.plot(horas, [v if v is not None else float("nan") for v in serie], color=GRIS[0], lw=1.5, zorder=1)
    a.scatter(xs, ys, s=22, color=AZUL[0], zorder=3)
    hv = [h for h in huecos if serie[h] is not None]
    a.scatter(hv, [serie[h] for h in hv], s=40, color=ROJO[0], zorder=4, marker="D")
    if nom == "borrar la fila":
        for h in huecos:
            a.text(h, 100, "×", ha="center", fontsize=13, color=ROJO[0])
    a.set_title(nom, fontsize=12, fontweight="bold", loc="left")
    a.text(0.0, -0.22, f"promedio del año {prom[nom]} MWh", transform=a.transAxes, fontsize=10, color=MUTED)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    for s in ("left", "bottom"): a.spines[s].set_color(GRID)
    a.tick_params(colors=MUTED, labelsize=9); a.set_xticks([0, 3, 6, 9, 11])
    a.set_ylim(-10, 280)
axs[0].set_ylabel("MWh", color=MUTED)
fig.text(0.125, 1.08, "Cada estrategia deja distinto el mismo día", fontsize=15, fontweight="bold")
fig.text(0.125, 1.0, "Valparaíso, 16 de septiembre, horas 0 a 11. En ámbar las horas que venían vacías y en rojo lo que se puso",
         fontsize=11, color=MUTED)
save(fig, "lab03_paso6_huecos")

# ---------- Paso 7 · Valores imposibles ----------
s = pd.read_csv(f"{D}/demanda_sucia.csv", sep=";")
s["mwh"] = s["mwh"].str.replace(",", ".").astype(float)
s["region"] = s["region"].str.strip().str.title()
s = s.drop_duplicates()
v = s[s.region == "Atacama"].reset_index(drop=True)
prom = s.groupby("region")["mwh"].mean()["Atacama"]
fig, ax = plt.subplots(figsize=(13, 4.4))
normal = v[(v.mwh >= 0) & (v.mwh <= 3 * prom)]
pico = v[v.mwh > 3 * prom]; neg = v[v.mwh < 0]
ax.scatter(normal.index, normal.mwh, s=2, color="#BDC1C6", lw=0)
ax.scatter(pico.index, pico.mwh, s=28, color=ROJO[0], zorder=3)
ax.scatter(neg.index, neg.mwh, s=28, color=ROJO[0], zorder=3, marker="v")
ax.axhline(3 * prom, color=INK, lw=1.2, ls="--")
ax.axhline(0, color=INK, lw=0.8)
ax.text(len(v) + 60, 3 * prom, "3 veces el promedio\n" + f"{3 * prom:.0f}" + " MWh", va="center", fontsize=10)
ax.text(len(v) + 60, 8, "cero", va="center", fontsize=10)
ax.text(len(v) + 60, pico.mwh.mean(), f"{len(pico)} picos", va="center", fontsize=10, color=ROJO[0], fontweight="bold")
ax.text(len(v) + 60, neg.mwh.mean() - 22, f"{len(neg)} negativos", va="center", fontsize=10, color=ROJO[0], fontweight="bold")
ax.set_xlim(0, len(v) + 900); ax.set_xticks([])
for sp in ("top", "right", "bottom"): ax.spines[sp].set_visible(False)
ax.spines["left"].set_color(GRID); ax.tick_params(colors=MUTED, labelsize=9)
ax.set_ylabel("MWh por hora", color=MUTED); ax.set_xlabel("las 8.784 horas del año, de enero a diciembre", color=MUTED)
ax.text(0, 1.16, "Una regla de negocio separa lo normal de lo imposible", transform=ax.transAxes, fontsize=15, fontweight="bold")
ax.text(0, 1.07, "Atacama, cada punto es una hora. Su promedio es " + f"{prom:.1f}".replace(".", ",") + " MWh",
        transform=ax.transAxes, fontsize=11, color=MUTED)
save(fig, "lab03_paso7_imposibles")
print("ok", len(pico), len(neg))
