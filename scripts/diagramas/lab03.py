import sys
from estilo import *
import pandas as pd
D = "datos"

# La misma lectura y limpieza del cuaderno guiado, para sacar las cifras reales
lim = pd.read_csv(f"{D}/demanda_sucia.csv", sep=";", decimal=",", parse_dates=["fecha"], dayfirst=True)
lim["region"] = lim["region"].str.strip().str.title()
sin_rep = lim.drop_duplicates()

# ---------- Paso 2 · read_csv avisando cómo viene escrito ----------
W, H = 16, 5.2
fig, ax = lienzo(W, H)
filas = [
    ("columnas", ["01/01/2024;0;Antofagasta;51,95"], "una sola línea de texto", 'sep=";"',
     "las columnas van separadas\npor punto y coma", ["fecha  hora  region  mwh"], "cuatro columnas", AZUL),
    ("mwh", ["'51,95'"], "texto", 'decimal=","', "la coma separa\nlos decimales", ["51.95"], "número", AMBAR),
    ("fecha", ["'01/01/2024'"], "texto", 'parse_dates=["fecha"],\ndayfirst=True', "es una fecha y\nva primero el día",
     ["2024-01-01"], "fecha", VERDE),
]
ax.text(1, 46, "dato", fontsize=10, color=MUTED, fontweight="bold")
ax.text(14, 46, "cómo viene en el archivo", fontsize=10, color=MUTED, fontweight="bold")
ax.text(53, 46, "qué se le avisa a read_csv", fontsize=10, color=MUTED, fontweight="bold")
ax.text(124, 46, "cómo queda", fontsize=10, color=MUTED, fontweight="bold")
y = 38.5
for col, antes, t1, op, que, despues, t2, c in filas:
    alto = 10.5
    ax.add_patch(Rectangle((0, y - alto + 4), W * 10 - 2, alto, facecolor=c[1], edgecolor="none"))
    ax.add_patch(Rectangle((0, y - alto + 4), 0.9, alto, facecolor=c[0], edgecolor="none"))
    ax.text(2, y, col, fontsize=11, fontweight="bold", family="DejaVu Sans Mono", va="center")
    ax.text(14, y, antes[0], fontsize=10.5, family="DejaVu Sans Mono", va="center", color=ROJO[0])
    ax.text(14, y - 4.6, t1, fontsize=9, color=MUTED, va="center")
    ax.text(53, y - (2.3 if "\n" in op else 0), op, fontsize=10, family="DejaVu Sans Mono", va="center",
            fontweight="bold", linespacing=1.3)
    ax.text(84, y - 2.3, que, fontsize=9.5, color=INK, va="center", linespacing=1.3)
    ax.annotate("", xy=(122, y), xytext=(112, y), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3))
    ax.text(124, y, despues[0], fontsize=10.5, family="DejaVu Sans Mono", va="center", color=VERDE[0] if c != VERDE else INK)
    ax.text(124, y - 4.6, t2, fontsize=9, color=MUTED, va="center")
    y -= alto + 3.5
titulo(ax, "Se le avisa a read_csv cómo viene escrito el archivo",
       "Así el número y la fecha quedan bien desde que se leen, sin convertir nada después", W, H)
save(fig, "lab03_paso4_tipos")

# ---------- Paso 4 · Filas repetidas ----------
W, H = 15, 4.6
fig, ax = lienzo(W, H)
antes = [("2024-01-01", "16", "Antofagasta", "69.17"), ("2024-01-01", "17", "Antofagasta", "71.96"),
         ("2024-01-01", "18", "Antofagasta", "74.81"), ("2024-01-01", "18", "Antofagasta", "74.81"),
         ("2024-01-01", "19", "Antofagasta", "80.71")]
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

# ---------- Paso 5 · Cuatro formas de rellenar ----------
valpo = sin_rep[sin_rep["region"] == "Valparaíso"].copy()
valpo["poner_cero"] = valpo["mwh"].fillna(0)
valpo["repetir_anterior"] = valpo["mwh"].ffill()
valpo["trazar_recta"] = valpo["mwh"].interpolate().round(2)
dia = valpo[valpo["fecha"] == "2024-09-16"].reset_index(drop=True)
horas = list(dia["hora"])
huecos = [h for h, v in zip(horas, dia["mwh"]) if pd.isna(v)]
assert huecos == [1, 2, 8, 9, 15, 16, 22, 23]
estr = {"borrar la fila": ("mwh", valpo["mwh"].mean()), "poner cero": ("poner_cero", valpo["poner_cero"].mean()),
        "repetir el valor anterior": ("repetir_anterior", valpo["repetir_anterior"].mean()),
        "trazar una recta": ("trazar_recta", valpo["trazar_recta"].mean())}
fig, axs = plt.subplots(1, 4, figsize=(15, 3.6), sharey=True, gridspec_kw={"wspace": 0.12})
for a, (nom, (col, prom)) in zip(axs, estr.items()):
    for h in huecos:
        a.axvspan(h - 0.5, h + 0.5, color=AMBAR[1], lw=0)
    serie = list(dia[col])
    a.plot(horas, serie, color=GRIS[0], lw=1.5, zorder=1)
    obs = dia[dia["mwh"].notna()]
    a.scatter(obs["hora"], obs["mwh"], s=16, color=AZUL[0], zorder=3)
    if col != "mwh":
        a.scatter(huecos, [serie[h] for h in huecos], s=34, color=ROJO[0], zorder=4, marker="D")
    else:
        a.text(0.5, 0.05, "no se pone nada, esas horas\nquedan fuera del promedio", transform=a.transAxes,
               ha="center", va="bottom", fontsize=9.5, color=MUTED)
    a.set_title(nom, fontsize=12, fontweight="bold", loc="left")
    a.text(0.0, -0.22, f"promedio del año {es(round(prom, 1))} MWh", transform=a.transAxes, fontsize=10, color=MUTED)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    for s in ("left", "bottom"): a.spines[s].set_color(GRID)
    a.tick_params(colors=MUTED, labelsize=9); a.set_xticks([0, 6, 12, 18, 23])
    a.set_ylim(-10, 300)
axs[0].set_ylabel("MWh", color=MUTED)
fig.text(0.125, 1.08, "Cada forma de rellenar deja distinto el mismo día", fontsize=15, fontweight="bold")
fig.text(0.125, 1.0, "Valparaíso, 16 de septiembre. En ámbar las ocho horas que vinieron vacías y en rojo lo que se puso",
         fontsize=11, color=MUTED)
save(fig, "lab03_paso6_huecos")

# ---------- Paso 6 · Valores imposibles ----------
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
