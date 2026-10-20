"""Diagramas de apoyo de los Labs 03 y 04 guiados, iguales a los de las presentaciones. Cifras sacadas de datos/."""
from estilo import *

D = "datos/"


def caja(ax, x, y, w, h, fill="#F8F9FA", edge=GRID, lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw))


def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)


def miles(n):
    return f"{n:,}".replace(",", ".")


sucia = pd.read_csv(D + "demanda_sucia.csv", sep=";")
limpia = pd.read_csv(D + "demanda_sucia.csv", sep=";", decimal=",", parse_dates=["fecha"], dayfirst=True)
limpia["region"] = limpia["region"].str.strip().str.title()
sin_rep = limpia.drop_duplicates()

# ---------- Lab 03 Paso 2 · El día va primero ----------
W, H = 15, 4.6
fig, ax = lienzo(W, H)
caja(ax, 56, 28, 38, 13, fill="#FFFFFF", edge=INK, lw=1.4)
ax.text(75, 34.5, "01/02/2024", ha="center", va="center", fontsize=20, fontweight="bold", family="DejaVu Sans Mono")
for x, k, orden, lee, quien in [(2, VERDE, "día / mes / año", "1 de febrero de 2024", "Así se escribe en Chile.\nEs lo que se le avisa con dayfirst=True."),
                                (104, ROJO, "mes / día / año", "2 de enero de 2024", "Así se escribe en Estados Unidos.\nEs lo que supone pandas si no se le avisa.")]:
    caja(ax, x, 6, 44, 30, fill=k[1], edge=k[0], lw=1.5)
    ax.text(x + 22, 31, orden, ha="center", va="center", fontsize=11, family="DejaVu Sans Mono", color=MUTED)
    ax.text(x + 22, 24, lee, ha="center", va="center", fontsize=14, fontweight="bold", color=k[0])
    ax.text(x + 22, 14, quien, ha="center", va="center", fontsize=10, color=INK, linespacing=1.4)
flecha(ax, (55, 30), (47, 24), None, color=VERDE[0])
flecha(ax, (95, 30), (103, 24), None, color=ROJO[0])
nota(ax, 50, 18, "Con 13/01/2024 no hay duda,\nporque no existe el mes 13.\nCon 01/02/2024 sí la hay.", color=INK, size=10)
titulo(ax, "En Chile la fecha empieza por el día",
       "Una misma fecha escrita con números se puede leer de dos formas. dayfirst=True dice cuál", W, H)
save(fig, "lab03_paso2_dayfirst")

# ---------- Lab 03 Paso 3 · De 49 formas a 7 ----------
W, H = 15, 5.4
fig, ax = lienzo(W, H)
vc = sucia["region"].value_counts()
bio = [k for k in vc.index if k.strip().lower() == "biobío"]
tras_strip = sorted({k.strip() for k in bio}, key=lambda s: (s != "Biobío", s))
tras_title = sorted({k.strip().title() for k in bio})
n0, n1, n2 = sucia["region"].nunique(), sucia["region"].str.strip().nunique(), sucia["region"].str.strip().str.title().nunique()
assert (n0, n1, n2) == (49, 21, 7) and len(bio) == 7 and len(tras_strip) == 3 and tras_title == ["Biobío"]
columnas = [(4, n0, "en el archivo", [repr(k) for k in bio], ROJO),
            (60, n1, "sin espacios", [repr(k) for k in tras_strip], AMBAR),
            (116, n2, "con mayúscula al inicio", [repr(k) for k in tras_title], VERDE)]
for x, n, que, ej, k in columnas:
    ax.text(x, 47, f"{n} formas", fontsize=17, fontweight="bold", color=k[0], va="center")
    ax.text(x, 42.5, que, fontsize=10, color=MUTED, va="center")
    for i, e in enumerate(ej):
        ax.add_patch(Rectangle((x, 35 - i * 4.4 - 3.6), 26, 3.8, facecolor=k[1], edgecolor="none"))
        ax.text(x + 1, 35 - i * 4.4 - 1.7, e, fontsize=9.5, family="DejaVu Sans Mono", va="center")
flecha(ax, (34, 22), (57, 22), ".str.strip()", color=INK)
flecha(ax, (90, 22), (113, 22), ".str.title()", color=INK)
nota(ax, 34, 18.5, "quita los espacios del\ncomienzo y del final", color=MUTED, size=9.5)
nota(ax, 90, 18.5, "primera letra mayúscula,\nel resto minúscula", color=MUTED, size=9.5)
nota(ax, 60, 6, "Aquí se ven solo las formas de Biobío. Cada región viene escrita de 7 formas,\n"
     "7 por 7 da 49. Sin espacios quedan 3 por región, 21, y al final 1 por región, 7.", color=INK, size=10.5)
titulo(ax, "De 49 formas de escribir las regiones a 7",
       "Cada arreglo junta formas que para Python eran distintas", W, H)
save(fig, "lab03_paso3_regiones")

# ---------- Lab 03 Paso 6 · describe en ocho números ----------
ata = sin_rep[sin_rep["region"] == "Atacama"]["mwh"]
d = ata.describe()
W, H = 15, 5.6
fig, ax = lienzo(W, H)
significado = {"count": "horas que tienen dato", "mean": "el promedio", "std": "cuánto se alejan del promedio, en general",
               "min": "el valor más bajo", "25%": "un cuarto de las horas queda por debajo",
               "50%": "la mediana, el valor del medio", "75%": "tres cuartos de las horas quedan por debajo",
               "max": "el valor más alto"}
filas = [(k, es(v, 1), significado[k]) for k, v in d.items()]
colores = [ROJO if k in ("min", "max") else GRIS for k in d.index]
yc = tabla(ax, 2, 50, ["", "Atacama", "qué es"], [8, 12, 52], filas, colores, rh=4.8, alin=["left", "right", "left"],
           rotulo='una["mwh"].describe().round(1)')
ax.text(80, yc[3], "← una demanda negativa no puede ser", fontsize=10.5, color=ROJO[0], va="center")
ax.text(80, yc[5], f"← la mitad de las horas está entre {es(d['25%'])} y {es(d['75%'])} MWh,\n    eso es lo normal en Atacama", fontsize=10.5, color=INK, va="center")
ax.text(80, yc[7], f"← {es(d['max'] / d['mean'], 0)} veces el promedio, muy raro para una hora", fontsize=10.5, color=ROJO[0], va="center")
nota(ax, 80, 50, "Mirar el mínimo y el máximo es la forma más rápida\nde notar que algo no calza, sin revisar las 8.784 horas\nuna por una.", color=MUTED, size=10.5)
titulo(ax, "describe resume una columna en ocho números",
       "La demanda de Atacama por hora. El mínimo y el máximo delatan los valores imposibles", W, H)
save(fig, "lab03_paso6_describe")

# ---------- Lab 03 Paso 6 · El umbral ----------
v = sin_rep[sin_rep["region"] == "Atacama"].reset_index(drop=True)
prom = v["mwh"].mean()
fig, axs = plt.subplots(1, 3, figsize=(15, 4.0), sharey=True, gridspec_kw={"wspace": 0.08})
casos = [(1, "casi la mitad de las horas,\ny son horas normales", ROJO), (3, "los picos que se plantaron\nal crear los datos", VERDE),
         (10, "se escapan 4 picos, en gris", AMBAR)]
for a, (veces, que, k) in zip(axs, casos):
    arriba = v[v["mwh"] > veces * prom]
    abajo = v[~(v["mwh"] > veces * prom)]
    a.scatter(abajo.index, abajo["mwh"], s=1.5, color="#BDC1C6", lw=0)
    a.scatter(arriba.index, arriba["mwh"], s=10 if veces == 1 else 26, color=ROJO[0], lw=0, zorder=3)
    if veces == 10:
        # Los picos que se marcan con 3 y ya no con 10, en gris y del mismo tamaño que los rojos
        escapan = v[(v["mwh"] > 3 * prom) & ~(v["mwh"] > veces * prom)]
        assert len(escapan) == 4
        a.scatter(escapan.index, escapan["mwh"], s=26, color="#9AA0A6", lw=0, zorder=3)
    a.axhline(veces * prom, color=INK, lw=1.2, ls="--")
    a.set_title(f"veces = {veces}, umbral {es(veces * prom, 0)} MWh", fontsize=12, fontweight="bold", loc="left")
    a.text(0.02, 0.98, f"{miles(len(arriba))} horas marcadas", transform=a.transAxes, fontsize=11.5, fontweight="bold", color=k[0], va="top")
    a.text(0.02, 0.89, que, transform=a.transAxes, fontsize=10, color=INK, va="top")
    a.set_xticks([]); a.set_ylim(-60, 640)
    for s_ in ("top", "right", "bottom"): a.spines[s_].set_visible(False)
    a.spines["left"].set_color(GRID); a.tick_params(colors=MUTED, labelsize=9)
axs[0].set_ylabel("MWh por hora", color=MUTED)
fig.text(0.125, 1.07, "El umbral decide cuántas horas se marcan como picos", fontsize=15, fontweight="bold")
fig.text(0.125, 0.99, f"Atacama, las mismas horas con tres umbrales distintos. Su promedio es {es(prom)} MWh",
         fontsize=11, color=MUTED)
save(fig, "lab03_paso6_umbral")

# ---------- Lab 04 Paso 3 · El promedio de True y False ----------
m = pd.read_csv(D + "mantenimiento.csv", parse_dates=["fecha"])
m["mes"] = m["fecha"].dt.month
tabla_ = m.pivot_table(index=["central", "mes"], columns="tipo_evento", aggfunc="size", fill_value=0) > 0
cb = tabla_.loc["Carboeléctrica Costa Brava"]["preventivo"].head(6)
W, H = 15, 5.0
fig, ax = lienzo(W, H)
yc = tabla(ax, 2, 42, ["mes", "preventivo"], [6, 14], [(str(k), str(bool(x))) for k, x in cb.items()],
           [VERDE if x else GRIS for x in cb], rh=4.6, alin=["right", "left"], rotulo="Costa Brava, enero a junio")
for y, x in zip(yc, cb):
    ax.text(26, y, "→", fontsize=13, va="center", color=MUTED)
    ax.text(31, y, "1" if x else "0", fontsize=13, fontweight="bold", va="center", family="DejaVu Sans Mono",
            color=VERDE[0] if x else "#9AA0A6")
n_si, n = int(cb.sum()), len(cb)
caja(ax, 42, 14, 46, 22)
ax.text(44, 31, f"suma {n_si}, de {n} canastas", fontsize=11, va="center")
ax.text(44, 25, f"promedio {n_si} / {n} = {es(n_si / n, 2)}", fontsize=12, fontweight="bold", va="center", family="DejaVu Sans Mono")
ax.text(44, 19, f"por 100, {es(100 * n_si / n, 0)} por ciento", fontsize=12, fontweight="bold", va="center", color=VERDE[0])
tot, nn = int(tabla_["preventivo"].sum()), len(tabla_)
assert (tot, nn) == (121, 215)
caja(ax, 98, 14, 50, 22, fill=VERDE[1], edge=VERDE[0])
ax.text(100, 31, f"En las {nn} canastas del año", fontsize=11, va="center")
ax.text(100, 25, f"preventivo es True en {tot}", fontsize=11, va="center")
ax.text(100, 19, f"{tot} / {nn} = {es(tot / nn, 3)}, el {es(100 * tot / nn)} por ciento", fontsize=11.5, fontweight="bold",
        va="center", color=VERDE[0])
nota(ax, 42, 9, "Por eso mean sobre la tabla de True y False entrega directo en qué parte de las canastas aparece cada evento.",
     color=INK, size=10.5)
titulo(ax, "El promedio de una columna de True y False es un porcentaje",
       "Para sumar y promediar, Python cuenta True como 1 y False como 0", W, H)
save(fig, "lab04_paso5_promedio")

# ---------- Lab 04 Paso 5 · Cómo se cuentan los días ----------
CEN = "Central Vega Azul"
x = m[(m.central == CEN) & (m.fecha >= "2024-02-01") & (m.fecha <= "2024-02-12")]
f = pd.read_csv(D + "fallas_electricas.csv")
fila = f[(f.central == CEN) & (f.fecha == "2024-02-05")].iloc[0]
assert int(fila.dias_hasta_correctivo) == 3
W, H = 15, 4.8
fig, ax = lienzo(W, H)
dias = pd.date_range("2024-02-01", "2024-02-12")
x0, dx = 6, 12
for i, dd in enumerate(dias):
    ax.plot([x0 + i * dx] * 2, [24, 26], color=GRID, lw=1)
    ax.text(x0 + i * dx, 21.5, dd.strftime("%d/%m"), ha="center", fontsize=9, color=MUTED)
ax.plot([x0, x0 + (len(dias) - 1) * dx], [25, 25], color=INK, lw=1)
col = {"falla_electrica": ROJO, "correctivo": AZUL, "inspeccion": GRIS}
niv = {}
for r in x.itertuples():
    i = (r.fecha - dias[0]).days
    k = niv.get(i, 0); niv[i] = k + 1
    ax.plot(x0 + i * dx, 30 + k * 6, "o", ms=11, color=col.get(r.tipo_evento, GRIS)[0])
    ax.text(x0 + i * dx + 2.2, 30 + k * 6, r.tipo_evento, fontsize=9.5, va="center", family="DejaVu Sans Mono")
i_f, i_c = (pd.Timestamp("2024-02-05") - dias[0]).days, (pd.Timestamp("2024-02-08") - dias[0]).days
ax.annotate("", xy=(x0 + i_c * dx, 43), xytext=(x0 + i_f * dx, 43), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.4))
ax.text(x0 + (i_f + i_c) / 2 * dx, 45, "3 días", ha="center", fontsize=12, fontweight="bold")
tabla(ax, 6, 13, ["central", "fecha", "dias_hasta_correctivo"], [24, 13, 27],
      [(fila.central, fila.fecha, str(int(fila.dias_hasta_correctivo)))], [ROJO], rh=4.6, alin=["left", "left", "right"])
nota(ax, 78, 14, "Esa falla queda así en fallas_electricas.csv. La inspección\ndel mismo día no cuenta, solo el correctivo. Un correctivo\n"
     "el mismo día de la falla cuenta como 0 días, y si nunca llegó,\nla casilla queda vacía.", color=INK, size=10)
titulo(ax, "Cada falla eléctrica se cuenta hasta el primer correctivo de su central",
       f"{CEN}, primeros días de febrero. Así se armó la planilla del Paso 5", W, H + 0.4)
ax.set_ylim(0, (H + 0.4) * 10)
save(fig, "lab04_paso9_linea")
print("ok")
