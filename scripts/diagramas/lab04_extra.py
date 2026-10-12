"""Diagramas nuevos del Lab 04 de la ruta guiada. Cifras sacadas de datos/."""
from estilo import *

D = "datos/"
mant = pd.read_csv(D + "mantenimiento.csv", parse_dates=["fecha"])
cen = pd.read_csv(D + "centrales.csv")
TIPOS = ["preventivo", "correctivo", "inspeccion", "falla_mecanica", "falla_electrica", "evento_climatico"]
PAL = dict(zip(TIPOS, [VERDE, AZUL, GRIS, MORADO, ROJO, AMBAR]))

def caja(ax, x, y, w, h, fill="#F8F9FA", edge=GRID, lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw))

def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)

def r1(v):
    return float(pd.Series([v]).round(1)[0])

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

# ---------- Paso 1 · La bitácora de una central ----------
W, H = 15.5, 5.0
fig, ax = lienzo(W, H)
CEN = "Termoeléctrica Bahía Norte"
x = mant[mant.central == CEN].sort_values("fecha", kind="stable")
x0, x1 = 6, 150
dx = (x1 - x0) / 366
for i in range(12):
    a = pd.Timestamp(2024, i + 1, 1).dayofyear - 1
    ax.add_patch(Rectangle((x0 + a * dx, 8), 0.12, 30, facecolor=GRID, edgecolor="none"))
    ax.text(x0 + a * dx + 1, 39, MESES[i], fontsize=9, color=MUTED)
ax.plot([x0, x1], [20, 20], color=INK, lw=1)
nivel = {}
for _, r in x.iterrows():
    d = r.fecha.dayofyear - 1
    k = nivel.get(d, 0); nivel[d] = k + 1
    ax.plot(x0 + d * dx, 23 + k * 4.2, "o", ms=9, color=PAL[r.tipo_evento][0])
for i, t in enumerate(TIPOS):
    ax.plot(x0 + 3 + i * 24, 4, "o", ms=8, color=PAL[t][0])
    ax.text(x0 + 5 + i * 24, 4, t, fontsize=9.5, va="center", family="DejaVu Sans Mono")
ax.text(x0, 14, f"{CEN}, {len(x)} eventos en el año. Cada punto es una fila de la bitácora.", fontsize=10.5, va="center")
nota(ax, x0, 52, f"La bitácora completa tiene {len(mant)} filas, una por evento, de {mant.central.nunique()} centrales. Las líneas grises separan los meses,\ny en el Paso 2 cada central en cada mes se convierte en una canasta.", color=INK, size=10.5)
titulo(ax, "La bitácora anota un evento por fila, en el orden en que pasan",
       "Así se ve el año de una sola central", W, H + 0.5)
ax.set_ylim(0, (H + 0.5) * 10)
save(fig, "lab04_paso1_bitacora")

# ---------- Estudio 1 · Duración por tipo ----------
W, H = 16.6, 5.4
fig, ax = lienzo(W, H)
res = mant.groupby("tipo_evento")["duracion_horas"].agg(eventos="count", horas_promedio="mean", horas_maximo="max")
res = res.round(1).sort_values("eventos", ascending=False)
axb = fig.add_axes([0.12, 0.12, 0.47, 0.64])

for i, t in enumerate(res.index):
    v = mant.loc[mant.tipo_evento == t, "duracion_horas"].to_numpy()
    jit = (pd.Series(range(len(v))) % 7 - 3).to_numpy() * 0.05
    axb.scatter(v, [i + j for j in jit], s=10, color=PAL[t][0], alpha=0.45)
    axb.plot([res.loc[t, "horas_promedio"]] * 2, [i - 0.35, i + 0.35], color=INK, lw=2.2)
    axb.plot(res.loc[t, "horas_maximo"], i, marker="|", ms=16, color=ROJO[0], mew=2)
axb.set_yticks(range(len(res))); axb.set_yticklabels(res.index, family="DejaVu Sans Mono"); axb.invert_yaxis()
axb.set_xlabel("duración en horas", color=MUTED)
for s_ in ["top", "right"]: axb.spines[s_].set_visible(False)
tabla(ax, 104, 44, ["tipo_evento", "eventos", "horas_promedio", "horas_maximo"], [18, 9.5, 16, 15],
      [(t, str(int(r.eventos)), es(r.horas_promedio), str(int(r.horas_maximo))) for t, r in res.iterrows()],
      [PAL[t] for t in res.index], rh=4.4, alin=["left", "right", "right", "right"], rotulo="lo que muestra la celda")
nota(ax, 104, 10, "Cada punto es un evento. La raya negra es el\npromedio y la roja el máximo de cada tipo.", color=INK, size=10.5)
titulo(ax, "agg calcula varias cifras por tipo de evento de una sola vez",
       "Cuántos hubo, cuánto duraron en promedio y cuánto duró el más largo", W, H)
save(fig, "lab04_estudio1_duracion")

# ---------- Estudio 2 · Eventos por tecnología ----------
W, H = 15, 5.0
fig, ax = lienzo(W, H)
con = pd.merge(mant, cen, on="central", how="left")
tecs = ["eolica", "hidro", "solar", "gas", "carbon", "diesel"]
ncen = cen.tecnologia.value_counts()
for j, (t, k) in enumerate([("evento_climatico", AMBAR), ("falla_electrica", ROJO)]):
    vc = con[con.tipo_evento == t].tecnologia.value_counts().reindex(tecs).fillna(0).astype(int)
    a = fig.add_axes([0.05 + j * 0.34, 0.12, 0.27, 0.6])
    a.barh(tecs, vc.values, color=k[0]); a.invert_yaxis()
    for y_, v_ in enumerate(vc.values): a.text(v_ + 0.8, y_, str(v_), va="center", fontsize=9)
    a.set_title(f"{t}, {vc.sum()} eventos", fontsize=11, family="DejaVu Sans Mono", loc="left")
    for s_ in ["top", "right"]: a.spines[s_].set_visible(False)
    a.set_xlim(0, 62)
nota(ax, 104, 44, "Los eventos climáticos se concentran\nen las eólicas. Las fallas eléctricas\nestán más repartidas.", color=INK, size=10.5)
nota(ax, 104, 26, f"Ojo al comparar. Hay {ncen['eolica']} centrales eólicas, {ncen['hidro']} hidro\ny {ncen['solar']} solares. Un conteo alto puede venir\nde tener más centrales de esa tecnología.", color=MUTED, size=10)
titulo(ax, "Con la ficha pegada se puede contar cada tipo de evento por tecnología",
       "El merge del Lab 01 y un filtro, después value_counts", W, H)
save(fig, "lab04_estudio2_tecnologia")

# ---------- Estudio 3 · Las 30 parejas ----------
W, H = 15, 6.0
fig, ax = lienzo(W, H)
tabla_ = pd.crosstab([mant["central"], mant["mes"] if "mes" in mant else mant["fecha"].dt.month], mant["tipo_evento"]) > 0
cols = list(tabla_.columns)
L = pd.DataFrame(index=cols, columns=cols, dtype=float); Cf = L.copy()
for si in cols:
    for en in cols:
        if si != en:
            j_ = (tabla_[si] & tabla_[en]).sum()
            conf = j_ / tabla_[si].sum()
            Cf.loc[si, en] = round(100 * conf, 1); L.loc[si, en] = round(conf / tabla_[en].mean(), 2)
a = fig.add_axes([0.2, 0.08, 0.45, 0.66])
import matplotlib.colors as mc
cmap = mc.LinearSegmentedColormap.from_list("l", ["#F1F3F4", "#F1F3F4", AZUL[1], AZUL[0]])
a.imshow(L.fillna(1).to_numpy(dtype=float), cmap=cmap, vmin=0.8, vmax=2.2)
for i, si in enumerate(cols):
    for j, en in enumerate(cols):
        if si == en:
            a.text(j, i, "·", ha="center", va="center", color=MUTED)
        else:
            v = L.loc[si, en]
            a.text(j, i, es(v, 2), ha="center", va="center", fontsize=9, fontweight="bold" if v >= 1.5 else "normal",
                   color="white" if v >= 1.8 else INK)
a.set_xticks(range(6)); a.set_xticklabels(cols, rotation=35, ha="right", family="DejaVu Sans Mono", fontsize=9)
a.set_yticks(range(6)); a.set_yticklabels(cols, family="DejaVu Sans Mono", fontsize=9)
a.set_ylabel("si", fontsize=11, fontweight="bold"); a.xaxis.set_label_position("top"); a.set_xlabel("entonces", fontsize=11, fontweight="bold")
i0, j0 = cols.index("falla_electrica"), cols.index("preventivo")
a.add_patch(Rectangle((j0 - 0.5, i0 - 0.5), 1, 1, fill=False, edgecolor=ROJO[0], lw=2.2))
nota(ax, 104, 52, "Cada casilla es el lift de una pareja.\n6 por 6 menos la diagonal da 30.", color=INK, size=10.5)
nota(ax, 104, 40, f"Las dos azules llegan a 1,9 o más.\nfalla_electrica con correctivo y\nevento_climatico con falla_mecanica.", color=AZUL[0], size=10.5)
nota(ax, 104, 25, f"En rojo, falla_electrica con preventivo.\nConfianza {es(Cf.loc['falla_electrica', 'preventivo'])} por ciento, pero lift\n{es(L.loc['falla_electrica', 'preventivo'], 2)}. El preventivo aparece en todas\npartes, no más de lo normal.", color=ROJO[0], size=10.5)
titulo(ax, "El for del Estudio 3 calcula el Paso 4 para todas las parejas",
       "Lift sobre 1 es que van juntas más de lo normal. Cerca de 1 es que no hay relación", W, H)
save(fig, "lab04_estudio3_parejas")

# ---------- Estudio 4 · shift trae el evento siguiente ----------
W, H = 15, 5.4
fig, ax = lienzo(W, H)
ordn = mant.sort_values(["central", "fecha"]).copy()
ordn["siguiente"] = ordn.groupby("central")["tipo_evento"].shift(-1)
x = ordn[ordn.central == CEN].head(7)
rows = [(str(r.fecha.date()), r.tipo_evento, r.siguiente) for r in x.itertuples()]

yc = tabla(ax, 1, 46, ["fecha", "tipo_evento", "siguiente"], [13, 19, 19], rows, [PAL[r[1]] for r in rows], rh=4.6,
           alin=["left", "left", "left"], rotulo=f"ordenados, primeras filas de {CEN}")
nota(ax, 55, yc[0] + 1.5, "← siguiente de esta fila es\n    el tipo_evento de la de abajo", color=AZUL[0], size=10)
nota(ax, 1, 8, "shift(-1) sube la columna una fila. Cada evento queda al lado del que vino después en la misma central.\ngroupby(\"central\") evita que el último evento de una central se junte con el primero de la siguiente.", color=INK, size=10.5)
tr = pd.crosstab(ordn["tipo_evento"], ordn["siguiente"], normalize="index")
fe = (100 * tr.loc["falla_electrica"]).round(1).sort_values(ascending=False)
tabla(ax, 92, 50, ["siguiente", "por ciento"], [19, 12], [(k, es(v)) for k, v in fe.items()], [PAL[k] for k in fe.index],
      rh=4.6, alin=["left", "right"], rotulo="después de falla_electrica")
nota(ax, 92, 15, "crosstab con normalize=\"index\" cuenta\nlas parejas y deja cada fila en porcentaje.", color=INK, size=10.5)
titulo(ax, "shift(-1) pone al lado de cada evento el que vino después",
       "Con eso se cuenta qué suele seguir a cada tipo de evento", W, H)
save(fig, "lab04_estudio4_siguiente")
print("ok")
