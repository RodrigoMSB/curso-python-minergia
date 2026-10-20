"""Diagramas nuevos del Lab 03 de la ruta guiada. Cifras sacadas de datos/."""
from estilo import *

D = "datos/"

def caja(ax, x, y, w, h, fill="#F8F9FA", edge=GRID, lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw))

def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)

def miles(n):
    return f"{n:,}".replace(",", ".")

# La misma lectura y limpieza del cuaderno guiado, para sacar las cifras reales
sucia = pd.read_csv(D + "demanda_sucia.csv", sep=";")
esperadas = 366 * 24 * 7
limpia = pd.read_csv(D + "demanda_sucia.csv", sep=";", decimal=",", parse_dates=["fecha"], dayfirst=True)
limpia["region"] = limpia["region"].str.strip().str.title()
sin_rep = limpia.drop_duplicates()
verdad = pd.read_csv(D + "demanda.csv", parse_dates=["fecha"])

# ---------- Paso 1 · Cómo llegó el archivo ----------
W, H = 15.5, 5.0
fig, ax = lienzo(W, H)
lineas = open(D + "demanda_sucia.csv", encoding="utf-8").read().splitlines()[:5]
caja(ax, 0, 14, 40, 30)
ax.text(1.5, 42, "demanda_sucia.csv, tal como viene", fontsize=10, color=MUTED, va="top")
for i, l in enumerate(lineas):
    ax.text(1.5, 36 - i * 4.6, l, fontsize=10, family="DejaVu Sans Mono", va="center",
            color=AZUL[0] if i == 0 else INK, fontweight="bold" if i == 0 else "normal")
nota(ax, 0, 12, "Separado por punto y coma y con coma decimal,\ncomo guarda Excel en Chile.")
flecha(ax, (42, 30), (56, 30), None)
ax.text(49, 33, 'read_csv\nsep=";"', ha="center", va="bottom", fontsize=9.5, family="DejaVu Sans Mono", color=MUTED)
r = sucia.head(3)
tabla(ax, 59, 42, ["", "fecha", "hora", "region", "mwh"], [3, 14, 6, 14, 9],
      [(str(i), x.fecha, str(x.hora), x.region, x.mwh) for i, x in r.iterrows()], [AZUL] * 3, rh=4.4,
      alin=["right", "left", "right", "left", "right"], rotulo="sucia")
nota(ax, 59, 22, "Sin sep=\";\" todo quedaría en una sola columna.", color=INK, size=10.5)
xs = 110
for i, (n, t, k) in enumerate([("366", "días", AZUL), ("24", "horas", AMBAR), ("7", "regiones", MORADO)]):
    ax.add_patch(Rectangle((xs + i * 14, 30), 11, 12, facecolor=k[1], edgecolor=k[0], lw=1.3))
    ax.text(xs + i * 14 + 5.5, 37.5, n, ha="center", va="center", fontsize=15, fontweight="bold", color=k[0])
    ax.text(xs + i * 14 + 5.5, 32.5, t, ha="center", va="center", fontsize=9)
    if i < 2: ax.text(xs + i * 14 + 12.5, 36, "×", ha="center", va="center", fontsize=14, color=MUTED)
ax.text(xs, 26, f"= {miles(esperadas)} filas esperadas", fontsize=11, fontweight="bold", va="top")
ax.text(xs, 21, f"llegaron {miles(len(sucia))}", fontsize=11, va="top")
ax.text(xs, 16, f"sobran {len(sucia) - esperadas}", fontsize=12, fontweight="bold", color=ROJO[0], va="top")
titulo(ax, "Antes de arreglar nada, se mira cómo llegó el archivo y se cuentan las filas",
       "Si sobran o faltan filas, algo viene mal aunque nada dé error", W, H)
save(fig, "lab03_paso1_archivo")

# ---------- Estudio 1 · Contra la demanda real ----------
valpo = sin_rep[sin_rep["region"] == "Valparaíso"].copy()
valpo["poner_cero"] = valpo["mwh"].fillna(0)
valpo["repetir_anterior"] = valpo["mwh"].ffill()
valpo["trazar_recta"] = valpo["mwh"].interpolate().round(2)
dia = valpo[valpo["fecha"] == "2024-09-16"].reset_index(drop=True)
real = verdad[(verdad["region"] == "Valparaíso") & (verdad["fecha"] == "2024-09-16")]
dia["real"] = list(real["mwh"])
vac = dia[dia["mwh"].isna()]
formas = [("poner_cero", "poner cero", ROJO), ("repetir_anterior", "repetir el anterior", AMBAR),
          ("trazar_recta", "trazar una recta", VERDE)]
W, H = 16, 5.4
fig, ax = lienzo(W, H)
a = fig.add_axes([0.08, 0.12, 0.54, 0.62])
for h in vac["hora"]:
    a.axvspan(h - 0.5, h + 0.5, color=AMBAR[1], lw=0)
a.plot(dia["hora"], dia["real"], color=INK, lw=1.8, zorder=2, label="demanda real")
for col, nom, k in formas:
    a.scatter(vac["hora"], vac[col], s=46, color=k[0], zorder=4, marker="D", label=nom)
a.set_ylim(-10, 300); a.set_xticks([0, 3, 6, 9, 12, 15, 18, 21, 23])
a.set_xlabel("hora del 16 de septiembre", color=MUTED); a.set_ylabel("MWh", color=MUTED)
for s_ in ("top", "right"): a.spines[s_].set_visible(False)
a.legend(frameon=False, loc="lower center", ncol=4, fontsize=9.5, bbox_to_anchor=(0.5, -0.33))
err = [(nom, es((vac[col] - vac["real"]).abs().mean()), es((vac[col] - vac["real"]).abs().max())) for col, nom, k in formas]
tabla(ax, 103, 46, ["forma", "promedio", "máximo"], [25, 13, 12], err, [k for _, _, k in formas], rh=4.6,
      alin=["left", "right", "right"], rotulo="error en las 8 horas vacías, en MWh")
nota(ax, 103, 22, "La recta es la que más se acerca.\nPoner cero es lo más lejano, el\nconsumo no se fue a cero.", color=INK, size=10.5)
nota(ax, 103, 8, "En el trabajo real no existe el archivo\noriginal. Por eso la forma de rellenar se\nelige con criterio y se deja escrita.", color=MUTED, size=10)
titulo(ax, "Con el archivo original se ve qué forma de rellenar se acercó más",
       "Valparaíso, 16 de septiembre. La línea es la demanda real y los rombos lo que puso cada forma en las horas vacías", W, H)
save(fig, "lab03_paso6_auditoria")

# ---------- Estudio 1 anterior · Lo que ve Python ----------
W, H = 15, 4.6
fig, ax = lienzo(W, H)
cards = [
    ("region", f"{sucia['region'].nunique()} formas distintas", "deberían ser 7", ROJO),
    ("mwh vacías", f"{miles(int(sucia['mwh'].isna().sum()))} horas", "sin dato", AMBAR),
    ("mwh", repr(sucia["mwh"].iloc[0]), "con comillas, es texto", MORADO),
    ("fecha", repr(sucia["fecha"].iloc[0]), "con comillas, es texto", AZUL),
]
for i, (t, v, s, k) in enumerate(cards):
    x = 1 + i * 37
    ax.add_patch(Rectangle((x, 12), 34, 26, facecolor=k[1], edgecolor=k[0], lw=1.5))
    ax.text(x + 17, 33.5, t, ha="center", va="center", fontsize=11, fontweight="bold", family="DejaVu Sans Mono")
    ax.text(x + 17, 25, v, ha="center", va="center", fontsize=14, fontweight="bold", color=k[0], family="DejaVu Sans Mono")
    ax.text(x + 17, 17, s, ha="center", va="center", fontsize=10, color=INK)
nota(ax, 1, 9, "Con el número como texto no se puede sumar. Python pegaría los textos uno detrás del otro, '51,95' + '49,02' da '51,9549,02'.\nrepr muestra las comillas, y así se nota que no es número.", color=INK, size=10.5)
titulo(ax, "Cuatro problemas que no se ven a simple vista",
       "Una persona lee 51,95 como número. Python lo lee como texto", W, H)
save(fig, "lab03_estudio1_problemas")

# ---------- Estudio 2 · Siete formas de escribir Biobío ----------
W, H = 15, 5.2
fig, ax = lienzo(W, H)
v = sucia["region"].value_counts()
bio = [(k, n) for k, n in v.items() if k.strip().lower() == "biobío"]
yb = tabla(ax, 1, 46, ["como viene escrita", "filas"], [26, 9], [(repr(k), miles(int(n))) for k, n in bio],
           [AZUL] + [AMBAR] * (len(bio) - 1), rh=4.6, alin=["left", "right"], rotulo="value_counts, solo las de Biobío")
caja(ax, 60, 20, 30, 18)
ax.text(75, 33, ".str.strip()", ha="center", fontsize=11, family="DejaVu Sans Mono", fontweight="bold", va="center")
ax.text(75, 29.5, "quita espacios de los extremos", ha="center", fontsize=9, color=MUTED, va="center")
ax.text(75, 25, ".str.title()", ha="center", fontsize=11, family="DejaVu Sans Mono", fontweight="bold", va="center")
ax.text(75, 21.5, "mayúscula solo al comienzo", ha="center", fontsize=9, color=MUTED, va="center")
for y in yb:
    ax.annotate("", xy=(59.5, 29), xytext=(37, y), arrowprops=dict(arrowstyle="-|>", color=GRIS[0], lw=0.9))
ax.add_patch(Rectangle((104, 25), 30, 8, facecolor=AZUL[1], edgecolor=AZUL[0], lw=1.5))
ax.text(119, 29, "'Biobío'", ha="center", va="center", fontsize=13, fontweight="bold", family="DejaVu Sans Mono")
flecha(ax, (91, 29), (103, 29), None, color=AZUL[0])
nota(ax, 96, 19, "Las siete formas quedan como una sola.\nEso lo hace el Paso 3 con todas las regiones,\ny por eso después quedan 7.", color=INK, size=10.5)
nota(ax, 1, 8, "Las comillas muestran los espacios. ' Biobío' y 'Biobío ' se ven iguales en una planilla, pero para Python son distintas.", color=INK, size=10.5)
titulo(ax, "value_counts muestra cuántas formas distintas tiene una misma región",
       f"El archivo trae {sucia['region'].nunique()} formas de escribir 7 regiones", W, H)
save(fig, "lab03_estudio2_formas")

# ---------- Estudio 3 · Promedio contra mediana ----------
W, H = 15.5, 5.4
fig, ax = lienzo(W, H)
res = sin_rep.groupby("region")["mwh"].agg(promedio="mean", mediana="median").sort_values("promedio", ascending=False)
pm, md = sin_rep["mwh"].mean(), sin_rep["mwh"].median()
axb = fig.add_axes([0.06, 0.1, 0.6, 0.66])
labels = ["Todo el país"] + list(res.index)
pr = [pm] + list(res.promedio); me = [md] + list(res.mediana)
yy = range(len(labels))
axb.barh([y + 0.2 for y in yy], pr, height=0.38, color=AZUL[0], label="promedio")
axb.barh([y - 0.2 for y in yy], me, height=0.38, color=AMBAR[0], label="mediana")
axb.set_yticks(list(yy)); axb.set_yticklabels(labels); axb.invert_yaxis()
for y, a_, b_ in zip(yy, pr, me):
    axb.text(a_ + 8, y + 0.2, es(float(pd.Series([a_]).round(1)[0])), va="center", fontsize=8.5, color=AZUL[0])
    axb.text(b_ + 8, y - 0.2, es(float(pd.Series([b_]).round(1)[0])), va="center", fontsize=8.5, color=AMBAR[0])
axb.get_yticklabels()[0].set_fontweight("bold")
axb.set_xlabel("MWh por hora", color=MUTED); axb.legend(frameon=False, loc="lower right")
for s_ in ["top", "right"]: axb.spines[s_].set_visible(False)
nota(ax, 109, 44, "Todo el país junto el promedio\nes el doble de la mediana.", color=INK, size=11, fontweight="bold")
nota(ax, 109, 33, "Dentro de cada región, las dos\nbarras quedan casi iguales.", color=INK, size=10.5)
nota(ax, 109, 23, "No es por los valores imposibles,\nque son pocos y casi no lo mueven.\nEs porque la Metropolitana consume\nvarias veces más que las demás y\nempuja el promedio hacia arriba.", color=MUTED, size=10)
titulo(ax, "El promedio de todo junto no describe a ninguna región",
       "La mediana es el valor del medio. La mitad de las horas está por debajo y la mitad por encima", W, H)
save(fig, "lab03_estudio3_mediana")
print("ok")
