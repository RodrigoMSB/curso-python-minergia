import sys
from estilo import *
import pandas as pd, numpy as np
D = "datos"
m = pd.read_csv(f"{D}/mantenimiento.csv", parse_dates=["fecha"])
m["mes"] = m["fecha"].dt.month
TIPOS = ["correctivo", "evento_climatico", "falla_electrica", "falla_mecanica", "inspeccion", "preventivo"]
CORTOS = ["correctivo", "climático", "f. eléctrica", "f. mecánica", "inspección", "preventivo"]
MES = {1: AZUL, 2: VERDE, 3: MORADO, 4: AMBAR, 5: AZUL, 6: VERDE, 7: MORADO, 8: AMBAR}
conteo = m.pivot_table(index=["central", "mes"], columns="tipo_evento", aggfunc="size", fill_value=0)
CB = "Carboeléctrica Costa Brava"


def tabla_tipos(ax, x0, y0, filas, rh, texto_de, tinte_de, rotulo, ancho=12):
    """Tabla con la columna mes y una columna por tipo de evento. Devuelve el centro de cada celda."""
    ax.text(x0, y0 + 1.6, rotulo, fontsize=11, fontweight="bold", va="bottom")
    ax.add_patch(Rectangle((x0, y0 - rh), 6, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
    ax.text(x0 + 5, y0 - rh / 2, "mes", fontsize=10, fontweight="bold", color=MUTED, va="center", ha="right",
            family="DejaVu Sans Mono")
    for k, t in enumerate(CORTOS):
        ax.add_patch(Rectangle((x0 + 6 + ancho * k, y0 - rh), ancho, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
        ax.text(x0 + 6 + ancho * k + ancho / 2, y0 - rh / 2, t, fontsize=9 if ancho >= 12 else 8.2, fontweight="bold", color=MUTED, va="center",
                ha="center")
    centros = {}
    for i, (mes, fila) in enumerate(filas):
        yy = y0 - rh * (i + 2)
        fuerte, tinte = MES[mes]
        ax.add_patch(Rectangle((x0 - 0.9, yy), 0.9, rh, facecolor=fuerte, edgecolor=SURF, lw=1.5))
        ax.add_patch(Rectangle((x0, yy), 6, rh, facecolor=tinte, edgecolor=SURF, lw=1.5))
        ax.text(x0 + 5, yy + rh / 2, str(mes), fontsize=10, va="center", ha="right", family="DejaVu Sans Mono")
        for k, t in enumerate(TIPOS):
            v = fila[t]
            ax.add_patch(Rectangle((x0 + 6 + ancho * k, yy), ancho, rh, facecolor=tinte_de(v, tinte), edgecolor=SURF, lw=1.5))
            txt, col = texto_de(v, fuerte)
            ax.text(x0 + 6 + ancho * k + ancho / 2, yy + rh / 2, txt, fontsize=10, va="center", ha="center",
                    family="DejaVu Sans Mono", color=col)
            centros[(mes, t)] = (x0 + 6 + ancho * k + ancho / 2, yy + rh / 2)
    return centros


# ---------- Paso 2 · De la bitácora a canastas ----------
cb = m[(m.central == CB) & (m.mes <= 3)]
W, H = 15, 4.8
fig, ax = lienzo(W, H)
filas = [(r.fecha.strftime("%Y-%m-%d"), r.tipo_evento) for r in cb.itertuples()]
cols = [MES[r.mes] for r in cb.itertuples()]
ce = tabla(ax, 1, 38, ["fecha", "tipo_evento"], [13, 17], filas, cols, alin=["left", "left"],
           rotulo="mant  (Costa Brava, enero a marzo)")
filas_c = [(mes, conteo.loc[(CB, mes)]) for mes in [1, 2, 3]]
cc = tabla_tipos(ax, 64, 38, filas_c, 5, lambda v, f: (str(v), INK if v else "#BDC1C6"),
                 lambda v, t: t if v else "#F8F9FA", "conteo  (las mismas tres canastas)", ancho=13)
for i, r in enumerate(cb.itertuples()):
    x_, y_ = cc[(r.mes, r.tipo_evento)]
    flecha(ax, (33, ce[i]), (62.5, y_), color=MES[r.mes][0], lw=1.0)
ax.text(64, 13, "Cinco eventos quedan en tres canastas, una por mes. Cada casilla cuenta\ncuántas veces pasó ese tipo de evento. "
        "En todo el año son 600 eventos y 215 canastas.", fontsize=10, va="top")
titulo(ax, "La tabla dinámica cuenta lo que le pasó a cada central en cada mes",
       "Cada fila es una canasta, como una boleta de supermercado que junta lo que se compró en una visita", W, H)
save(fig, "lab04_paso4_canastas")

# ---------- Paso 3 · Más de cero veces es sí ----------
W, H = 16, 5.6
fig, ax = lienzo(W, H)
filas_c = [(mes, conteo.loc[(CB, mes)]) for mes in range(1, 9)]
assert conteo.loc[(CB, 7), "correctivo"] == 2
tabla_tipos(ax, 1, 48, filas_c, 4.4, lambda v, f: (str(v), INK if v else "#BDC1C6"),
            lambda v, t: t if v else "#F8F9FA", "conteo  (Costa Brava, enero a agosto)", ancho=10.5)
flecha(ax, (73, 30), (83, 30), "> 0")
tabla_tipos(ax, 87, 48, filas_c, 4.4, lambda v, f: ("True" if v else "False", VERDE[0] if v else "#9AA0A6"),
            lambda v, t: VERDE[1] if v else "#F8F9FA", "tabla", ancho=10.5)
ax.text(1, 4, "En julio hubo dos correctivos. La casilla dice 2 y pasa a True igual que las que dicen 1. "
        "Desde aquí importa si pasó, no cuántas veces.", fontsize=10.5, va="center")
titulo(ax, "Más de cero veces es sí",
       "conteo > 0 deja cada casilla en True o False, la pregunta de un filtro hecha a toda la tabla", W, H)
save(fig, "lab04_paso5_tabla")

# ---------- Paso 4 · Confianza contra lift ----------
t = pd.crosstab([m["central"], m["mes"]], m["tipo_evento"]) > 0
def waffle(ax, n, marcados, color, titulo_, sub):
    lado = int(np.ceil(np.sqrt(n * 1.6)))
    for i in range(n):
        r, c = divmod(i, lado)
        ax.add_patch(Rectangle((c, -r), 0.82, 0.82, facecolor=color if i < marcados else "#E8EAED", edgecolor="none"))
    filas = int(np.ceil(n / lado))
    ax.set_xlim(-0.3, 26); ax.set_ylim(-11, 3.4); ax.set_aspect("equal"); ax.axis("off")
    ax.text(0, 2.6, titulo_, fontsize=12, fontweight="bold", va="center")
    ax.text(0, 1.5, sub, fontsize=10, color=MUTED, va="center")
fig, axs = plt.subplots(2, 2, figsize=(13, 7.6), gridspec_kw={"hspace": 0.12, "wspace": 0.05})
for fila, (ent, col) in enumerate([("correctivo", AZUL[0]), ("preventivo", MORADO[0])]):
    tot = t[ent].sum(); n_si = t["falla_electrica"].sum(); ambos = (t["falla_electrica"] & t[ent]).sum()
    p_all = 100 * tot / len(t); p_si = 100 * ambos / n_si
    waffle(axs[fila, 0], len(t), tot, col, f"Todas las canastas, {ent} en el {p_all:.1f} %".replace(".", ","),
           f"{tot} de {len(t)}. Esto es lo normal")
    waffle(axs[fila, 1], n_si, ambos, col, f"Canastas con falla eléctrica, {ent} en el {p_si:.1f} %".replace(".", ","),
           f"{ambos} de {n_si}. Esta es la confianza")
    lift = p_si / p_all
    axs[fila, 1].text(0, -5.2, f"lift {lift:.2f}".replace(".", ","), fontsize=20, fontweight="bold", color=col)
    axs[fila, 1].text(0, -7.3, "aparece el doble de lo normal" if lift > 1.5 else "aparece igual que siempre,\nla regla no dice nada",
                      fontsize=11, color=INK, va="top")
fig.text(0.125, 0.97, "La confianza se compara con lo normal, y eso es el lift", fontsize=15, fontweight="bold")
fig.text(0.125, 0.935, "Cada cuadrito es una canasta. Arriba la regla falla eléctrica con correctivo y abajo con preventivo",
         fontsize=11, color=MUTED)
save(fig, "lab04_paso6_lift")

# ---------- Paso 5 · Días hasta el correctivo ----------
e = m[m.tipo_evento == "falla_electrica"]; co = m[m.tipo_evento == "correctivo"]
p = e[["central", "fecha"]].merge(co[["central", "fecha"]], on="central", suffixes=("_f", "_c"))
p["d"] = (p.fecha_c - p.fecha_f).dt.days
primero = p[p.d >= 0].groupby(["central", "fecha_f"]).d.min()
cuenta = [int((primero == d).sum()) for d in range(8)]
despues = int((primero > 7).sum()); nunca = len(e) - len(primero)
etiquetas = [str(d) for d in range(8)] + ["más de 7", "ninguno"]
valores = cuenta + [despues, nunca]
fig, ax = plt.subplots(figsize=(12, 4.4))
colores = [AZUL[0] if i <= 3 else "#BDC1C6" for i in range(len(valores))]
ax.bar(range(len(valores)), valores, color=colores, width=0.7)
acum = 0
for i, v in enumerate(valores):
    if v: ax.text(i, v + 0.3, str(v), ha="center", fontsize=11, fontweight="bold")
for d in range(4):
    acum += cuenta[d]
    ax.text(d, -2.6, f"{100 * acum / len(e):.1f} %".replace(".", ","), ha="center", fontsize=10, color=AZUL[0])
ax.text(-0.9, -2.6, "acumulado", ha="right", fontsize=10, color=MUTED)
ax.set_xticks(range(len(valores))); ax.set_xticklabels(etiquetas)
ax.set_ylim(-3.6, 14); ax.set_yticks([]); ax.axhline(0, color=GRID, lw=1)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(colors=MUTED, labelsize=10)
ax.set_xlabel("días entre la falla eléctrica y el primer correctivo en la misma central", color=MUTED, labelpad=22)
ax.annotate("desde el día 4 ya no suma nada\nhasta pasada una semana", xy=(5.5, 0.5), xytext=(5.5, 6), ha="center",
            fontsize=10, color=MUTED, arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
ax.text(0, 1.17, "La mayoría de los correctivos llega en los tres días siguientes", transform=ax.transAxes,
        fontsize=15, fontweight="bold")
ax.text(0, 1.08, f"Las {len(e)} fallas eléctricas del año, según cuánto tardó el correctivo", transform=ax.transAxes,
        fontsize=11, color=MUTED)
save(fig, "lab04_paso9_dias")
print("ok", valores)
