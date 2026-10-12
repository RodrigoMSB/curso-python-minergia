"""Diagramas nuevos del Lab 03 de la ruta guiada. Cifras sacadas de datos/."""
from estilo import *

D = "datos/"

def caja(ax, x, y, w, h, fill="#F8F9FA", edge=GRID, lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw))

def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)

def miles(n):
    return f"{n:,}".replace(",", ".")

# Misma limpieza del cuaderno, para sacar las cifras reales
sucia = pd.read_csv(D + "demanda_sucia.csv", sep=";")
esperadas = 366 * 24 * 7
limpia = sucia.copy()
limpia["mwh"] = limpia["mwh"].str.replace(",", ".").astype(float)
limpia["fecha"] = pd.to_datetime(limpia["fecha"], format="%d/%m/%Y")
limpia["region"] = limpia["region"].str.strip().str.title()
sin_rep = limpia.drop_duplicates()
tabla_ = sin_rep.sort_values(["region", "fecha", "hora"]).reset_index(drop=True)
prom_reg = tabla_.groupby("region")["mwh"].transform("mean")
final = tabla_.copy()
final["fue_nulo"] = final["mwh"].isna()
final["fue_corregido"] = (tabla_["mwh"] < 0) | (tabla_["mwh"] > 3 * prom_reg)
final.loc[final["fue_corregido"], "mwh"] = None
final["mwh"] = final.groupby("region")["mwh"].transform(lambda s: s.interpolate())
verdad = pd.read_csv(D + "demanda.csv", parse_dates=["fecha"])
aud = pd.merge(final, verdad, on=["fecha", "hora", "region"], suffixes=("_limpia", "_real"))
aud["error"] = (aud["mwh_limpia"] - aud["mwh_real"]).abs()
aud["grupo"] = "no se tocó"
aud.loc[aud["fue_nulo"], "grupo"] = "se rellenó"
aud.loc[aud["fue_corregido"], "grupo"] = "se corrigió"

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

# ---------- Paso 6 · La auditoría ----------
W, H = 16, 5.4
fig, ax = lienzo(W, H)
ej = []
for gname, col in [("no se tocó", VERDE), ("se rellenó", AMBAR), ("se corrigió", ROJO)]:
    x = aud[aud.grupo == gname].iloc[0]
    ej.append(((str(x.fecha.date()), str(x.hora), x.region, es(x.mwh_limpia, 1), es(x.mwh_real, 1), es(x.error, 1), gname), col))
tabla(ax, 1, 46, ["fecha", "hora", "region", "mwh_limpia", "mwh_real", "error", "grupo"], [12, 6, 14, 13, 11, 8, 13],
      [e[0] for e in ej], [e[1] for e in ej], rh=4.6, alin=["left", "right", "left", "right", "right", "right", "left"],
      rotulo="auditoria, una fila de cada grupo")
nota(ax, 1, 24, "merge pone lado a lado lo limpio y lo real de la misma hora. suffixes les pone\napellido a las dos columnas mwh. error es la diferencia sin signo.", color=INK, size=10.5)
res = aud.groupby("grupo")["error"].agg(horas="count", error_promedio="mean", error_maximo="max")
cols = {"no se tocó": VERDE, "se rellenó": AMBAR, "se corrigió": ROJO}
tabla(ax, 92, 46, ["grupo", "horas", "error_promedio", "error_maximo"], [13, 10, 16.5, 15],
      [(gname, miles(int(r.horas)), es(float(pd.Series([r.error_promedio]).round(1)[0])), es(float(pd.Series([r.error_maximo]).round(1)[0]))) for gname, r in res.iterrows()],
      [cols[g_] for g_ in res.index], rh=4.6, alin=["left", "right", "right", "right"], rotulo="lo que muestra la celda")
nota(ax, 92, 24, "Las horas que no se tocaron tienen error cero.\nEl error está solo donde se rellenó o se corrigió.", color=INK, size=10.5)
caja(ax, 1, 2, 150, 8, fill=AMBAR[1], edge=AMBAR[0])
ax.text(3, 6, "En el trabajo real no existe el archivo original. Lo que sí se puede hacer siempre es marcar qué se tocó, con fue_nulo y fue_corregido.",
        fontsize=10, va="center")
titulo(ax, "Como aquí existe el archivo original, se puede medir qué tan bien quedó la limpieza",
       "Cada hora limpia se compara con la real y se agrupa según lo que se le hizo", W, H)
save(fig, "lab03_paso6_auditoria")

# ---------- Estudio 1 · Lo que ve Python ----------
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
nota(ax, 96, 19, "Las siete formas quedan como una sola.\nEso lo hace el Paso 2 con todas las regiones,\ny por eso después quedan 7.", color=INK, size=10.5)
nota(ax, 1, 8, "Las comillas muestran los espacios. ' Biobío' y 'Biobío ' se ven iguales en una planilla, pero para Python son distintas.", color=INK, size=10.5)
titulo(ax, "value_counts muestra cuántas formas distintas tiene una misma región",
       f"El archivo trae {sucia['region'].nunique()} formas de escribir 7 regiones", W, H)
save(fig, "lab03_estudio2_formas")

# ---------- Estudio 3 · Promedio contra mediana ----------
W, H = 15.5, 5.4
fig, ax = lienzo(W, H)
res = final.groupby("region")["mwh"].agg(promedio="mean", mediana="median").sort_values("promedio", ascending=False)
pm, md = final["mwh"].mean(), final["mwh"].median()
axb = fig.add_axes([0.06, 0.1, 0.6, 0.66])
labels = ["Todo el país"] + list(res.index)
pr = [pm] + list(res.promedio); me = [md] + list(res.mediana)
yy = range(len(labels))
axb.barh([y + 0.2 for y in yy], pr, height=0.38, color=AZUL[0], label="promedio")
axb.barh([y - 0.2 for y in yy], me, height=0.38, color=AMBAR[0], label="mediana")
axb.set_yticks(list(yy)); axb.set_yticklabels(labels); axb.invert_yaxis()
for y, a, b in zip(yy, pr, me):
    axb.text(a + 8, y + 0.2, es(float(pd.Series([a]).round(1)[0])), va="center", fontsize=8.5, color=AZUL[0])
    axb.text(b + 8, y - 0.2, es(float(pd.Series([b]).round(1)[0])), va="center", fontsize=8.5, color=AMBAR[0])
axb.get_yticklabels()[0].set_fontweight("bold")
axb.set_xlabel("MWh por hora", color=MUTED); axb.legend(frameon=False, loc="lower right")
for s_ in ["top", "right"]: axb.spines[s_].set_visible(False)
nota(ax, 109, 44, "Todo el país junto el promedio\nes el doble de la mediana.", color=INK, size=11, fontweight="bold")
nota(ax, 109, 33, "Dentro de cada región, las dos\nbarras quedan casi iguales.", color=INK, size=10.5)
nota(ax, 109, 23, "No es por valores extremos, que ya\nse corrigieron en el Paso 5. Es\nporque la Metropolitana consume\nvarias veces más que las demás y\nempuja el promedio hacia arriba.", color=MUTED, size=10)
titulo(ax, "El promedio de todo junto no describe a ninguna región",
       "La mediana es el valor del medio. La mitad de las horas está por debajo y la mitad por encima", W, H)
save(fig, "lab03_estudio3_mediana")
print("ok")
