"""Diagramas nuevos del Lab 02 de la ruta guiada. Cifras sacadas de datos/."""
from estilo import *

D = "datos/"
c = pd.read_csv(D + "centrales.csv")
g = pd.read_csv(D + "generacion.csv", parse_dates=["fecha"])
dem = pd.read_csv(D + "demanda.csv", parse_dates=["fecha"])
gen = pd.merge(g, c, on="central", how="left")

def caja(ax, x, y, w, h, fill="#F8F9FA", edge=GRID, lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw))

def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)

def miles(n):
    return f"{n:,}".replace(",", ".")

# ---------- Paso 1 · La generación con su ficha ----------
W, H = 16, 6.4
fig, ax = lienzo(W, H)
r0 = g.iloc[0]
tabla(ax, 1, 58, ["fecha", "hora", "central", "mwh"], [12, 6, 27, 9],
      [(str(r0.fecha.date()), str(r0.hora), r0.central, f"{r0.mwh:.2f}")], [AZUL], rh=4.4,
      alin=["left", "right", "left", "right"], rotulo=f"generacion  ({miles(len(g))} × 4)")
c0 = c.iloc[0]
tabla(ax, 70, 58, ["central", "tecnologia", "region", "potencia_mw", "anio_inicio"], [27, 12.5, 10, 13.5, 13.5],
      [(c0.central, c0.tecnologia, c0.region, str(c0.potencia_mw), str(c0.anio_inicio))], [AMBAR], rh=4.4,
      alin=["left", "left", "left", "right", "right"], rotulo=f"centrales  ({len(c)} × 5)")
flecha(ax, (28, 46), (60, 33), None, color=AZUL[0])
flecha(ax, (108, 46), (76, 33), None, color=AMBAR[0])
ax.text(68, 41, 'merge on="central"', ha="center", va="center", fontsize=10, family="DejaVu Sans Mono", color=MUTED)
gr = gen.iloc[0]
cols = ["fecha", "hora", "central", "mwh", "tecnologia", "region", "potencia_mw", "anio_inicio"]
an = [12, 6, 27, 9, 12.5, 10, 13.5, 13.5]
x = 18
ax.text(x, 31, f"gen  ({miles(len(gen))} × 8)", fontsize=11, fontweight="bold", va="bottom")
vals = [str(gr.fecha.date()), str(gr.hora), gr.central, f"{gr.mwh:.2f}", gr.tecnologia, gr.region, str(gr.potencia_mw), str(gr.anio_inicio)]
for i, (cn, w, v) in enumerate(zip(cols, an, vals)):
    k = AZUL if i < 4 else AMBAR
    ax.add_patch(Rectangle((x, 26), w, 4.4, facecolor=k[1], edgecolor=SURF, lw=1.5))
    ax.text(x + 0.8, 28.2, cn, fontsize=9.5, fontweight="bold", color=k[0], va="center", family="DejaVu Sans Mono")
    ax.add_patch(Rectangle((x, 21.6), w, 4.4, facecolor="#F8F9FA", edgecolor=SURF, lw=1.5))
    ax.text(x + 0.8, 23.8, v, fontsize=9.5, va="center", family="DejaVu Sans Mono")
    x += w
nota(ax, 18, 18, "Las 4 columnas de generacion, en azul, más las 4 de la ficha, en amarillo. central aparece una sola vez\nporque es la columna con que se une. Las filas no cambian, siguen siendo una por central y por hora.", color=INK, size=10.5)
caja(ax, 18, 1, 104, 7, fill=VERDE[1], edge=VERDE[0])
ax.text(20, 4.5, f"demanda  ({miles(len(dem))} × 4)  queda aparte. Se usa en los Pasos 4 y 5 y en el Estudio 1.", fontsize=10.5, va="center")
titulo(ax, "El Paso 1 deja la generación de cada hora con la ficha de su central al lado",
       "Es la misma unión del Lab 01, ahora con todo el año", W, H)
save(fig, "lab02_paso1_tablas")

# ---------- Paso 2 · Dos condiciones con & ----------
W, H = 16, 5.4
fig, ax = lienzo(W, H)
quien = ["Parque Solar Pampa Alta", "Parque Solar Llano Seco", "Parque Solar Sol Naciente", "Carboeléctrica Roca Gris",
         "Parque Solar Altiplano", "Central Río Manso Alto"]
sub = c.set_index("central").loc[quien].reset_index()
s1 = sub.tecnologia == "solar"
s2 = sub.region == "Antofagasta"
amb = s1 & s2
rows = [(r.central, r.tecnologia, r.region) for r in sub.itertuples()]
yc = tabla(ax, 1, 46, ["central", "tecnologia", "region"], [28, 12, 13], rows,
           [AZUL if a else GRIS for a in amb], rh=4.6, alin=["left", "left", "left"], rotulo="algunas filas de gen")
k = lambda b: VERDE if b else ROJO
tabla(ax, 60, 46, ['tecnologia == "solar"'], [22], [(str(b),) for b in s1], [k(b) for b in s1], rh=4.6, alin=["left"])
ax.text(86, 46 - 2.3, "&", fontsize=18, fontweight="bold", ha="center", va="center", color=INK)
tabla(ax, 90, 46, ['region == "Antofagasta"'], [24], [(str(b),) for b in s2], [k(b) for b in s2], rh=4.6, alin=["left"])
ax.text(118, 46 - 2.3, "=", fontsize=18, fontweight="bold", ha="center", va="center", color=INK)
tabla(ax, 122, 46, ["pasa"], [12], [(str(b),) for b in amb], [k(b) for b in amb], rh=4.6, alin=["left"])
nota(ax, 60, 12, "& se lee como \"y\". La fila pasa solo si las dos condiciones dan True.\nCada condición va entre paréntesis.", color=INK, size=10.5)
ns = int(((c.tecnologia == "solar") & (c.region == "Antofagasta")).sum())
assert ns * 366 * 24 == 26352
nota(ax, 60, 4, f"En el año hay {ns} centrales solares en Antofagasta, {ns} × 8.784 horas = 26.352 filas.", color=AZUL[0], size=10.5)
titulo(ax, "Con & la fila tiene que cumplir las dos condiciones a la vez",
       '(gen["tecnologia"] == tecnologia) & (gen["region"] == region)', W, H)
save(fig, "lab02_paso2_dos_condiciones")

# ---------- Estudio 1 · Fin de semana ----------
W, H = 16, 4.8
fig, ax = lienzo(W, H)
dem["dow"] = dem.fecha.dt.dayofweek
pm = dem.groupby("dow").mwh.mean()
dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
for i, dname in enumerate(dias):
    fin = i >= 5
    col = AMBAR if fin else AZUL
    x = 1 + i * 13
    ax.add_patch(Rectangle((x, 24), 12, 16, facecolor=col[1], edgecolor=col[0], lw=1.4))
    ax.text(x + 6, 37, dname, ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(x + 6, 32.5, str(i), ha="center", va="center", fontsize=16, fontweight="bold", color=col[0], family="DejaVu Sans Mono")
    ax.text(x + 6, 27.5, str(fin), ha="center", va="center", fontsize=10, family="DejaVu Sans Mono", color=col[0])
ax.text(1, 43, "dayofweek numera los días desde 0, lunes, hasta 6, domingo.   >= 5 da True solo el sábado y el domingo.",
        fontsize=10.5, va="bottom")
prom = dem.assign(es_finde=dem.dow >= 5).groupby("es_finde").mwh.mean()
f, t = prom[False], prom[True]
caida = 100 * (1 - t / f)
tabla(ax, 1, 18, ["es_finde", "promedio mwh"], [14, 16], [("False", es(f)), ("True", es(t))], [AZUL, AMBAR], rh=4.4,
      alin=["left", "right"])
caja(ax, 46, 2, 70, 15)
ax.text(48, 13.5, "caida = 100 * (1 - promedio[True] / promedio[False])", fontsize=10, family="DejaVu Sans Mono", va="center")
ax.text(48, 7, f"100 × (1 − {es(t)} / {es(f)}) = {es(caida)} por ciento", fontsize=12, fontweight="bold", color=AMBAR[0], va="center")
nota(ax, 120, 15, "La caída se calcula sobre el\npromedio de los días de semana,\npor eso se divide por False.", color=INK, size=10)
titulo(ax, "Una columna de True y False separa los días de semana del fin de semana",
       "Después se agrupa por esa columna y se comparan los dos promedios", W, H)
save(fig, "lab02_estudio1_finde")

# ---------- Estudio 2 · Potencia contra energía ----------
W, H = 15, 5.4
fig, ax = lienzo(W, H)
pot = c.groupby("tecnologia").potencia_mw.sum().sort_values(ascending=False)
ene = gen.groupby("tecnologia").mwh.sum().sort_values(ascending=False)
pal = dict(zip(["hidro", "solar", "eolica", "gas", "carbon", "diesel"], [AZUL, AMBAR, VERDE, MORADO, ROJO, GRIS]))
yp = tabla(ax, 4, 46, ["", "tecnologia", "potencia_mw"], [4, 14, 14],
           [(str(i + 1), t, miles(int(v))) for i, (t, v) in enumerate(pot.items())], [pal[t] for t in pot.index], rh=5,
           alin=["right", "left", "right"], rotulo="Lab 01 · potencia instalada")
ye = tabla(ax, 96, 46, ["", "tecnologia", "mwh en 2024"], [4, 14, 18],
           [(str(i + 1), t, miles(round(v))) for i, (t, v) in enumerate(ene.items())], [pal[t] for t in ene.index], rh=5,
           alin=["right", "left", "right"], rotulo="Estudio 2 · energía generada")
for t in pot.index:
    a, b = yp[list(pot.index).index(t)], ye[list(ene.index).index(t)]
    flecha(ax, (37, a), (94.5, b), color=pal[t][0], lw=2.2 if t == "solar" else 1.0)
nota(ax, 40, 9, "La solar es segunda en potencia y quinta en energía, porque de noche no genera.\nGas y carbón suben porque generan casi todas las horas.", color=INK, size=10.5)
titulo(ax, "Potencia instalada y energía generada no ordenan igual a las tecnologías",
       "Potencia es lo máximo que puede dar una central. Energía es lo que de verdad generó en el año", W, H)
save(fig, "lab02_estudio2_potencia_energia")

# ---------- Estudio 4 · Factor de planta ----------
W, H = 15, 5.2
fig, ax = lienzo(W, H)
caja(ax, 0, 22, 50, 22)
ax.text(2, 41, "factor_planta = mwh / potencia_mw", fontsize=11, family="DejaVu Sans Mono", fontweight="bold", va="top")
sol = gen[(gen.central == "Parque Solar Pampa Alta") & (gen.fecha == "2024-06-15")].set_index("hora")
gas = gen[(gen.central == "Termoeléctrica Bahía Norte") & (gen.fecha == "2024-06-15")].set_index("hora")
ax.text(2, 34, f"Solar Pampa Alta, 15 de junio a las 12\n{es(sol.mwh[12], 2)} / {sol.potencia_mw[12]} = {es(sol.mwh[12] / sol.potencia_mw[12], 3)}",
        fontsize=10, va="top", color=AMBAR[0])
ax.text(2, 27, f"Solar Pampa Alta, 15 de junio a las 0\n{es(sol.mwh[0], 2)} / {sol.potencia_mw[0]} = {es(0, 3)}",
        fontsize=10, va="top", color=AMBAR[0])
fp = gen.assign(f=gen.mwh / gen.potencia_mw).groupby("tecnologia").f.mean()
nota(ax, 0, 18, f"Promedio de todas las horas del año\nsolar {es(fp['solar'], 3)}   gas {es(fp['gas'], 3)}", color=INK, size=11, fontweight="bold")
nota(ax, 0, 8, "1 sería generar a plena potencia todas las horas.", color=MUTED, size=10)
axb = fig.add_axes([0.45, 0.12, 0.53, 0.62])
hrs = list(range(24))
axb.bar([h - 0.2 for h in hrs], [sol.mwh[h] / sol.potencia_mw[h] for h in hrs], width=0.4, color=AMBAR[0], label="Solar Pampa Alta")
axb.bar([h + 0.2 for h in hrs], [gas.mwh[h] / gas.potencia_mw[h] for h in hrs], width=0.4, color=MORADO[0], label="Gas Bahía Norte")
axb.set_xticks(range(0, 24, 2)); axb.set_xlabel("hora del 15 de junio", color=MUTED); axb.set_ylabel("factor de planta", color=MUTED)
axb.set_ylim(0, 1); axb.legend(frameon=False, loc="upper right")
for s_ in ["top", "right"]: axb.spines[s_].set_visible(False)
titulo(ax, "El factor de planta dice qué parte de su potencia usó cada central",
       "Se calcula para cada hora y después se promedia por tecnología", W, H)
save(fig, "lab02_estudio4_factor")
print("ok")
