import sys
from estilo import *
import pandas as pd, numpy as np
D = "datos"
m = pd.read_csv(f"{D}/mantenimiento.csv", parse_dates=["fecha"])
m["mes"] = m["fecha"].dt.month
TIPOS = ["correctivo", "evento_climatico", "falla_electrica", "falla_mecanica", "inspeccion", "preventivo"]
MES = {1: AZUL, 2: VERDE, 3: MORADO, 4: AMBAR, 5: AZUL, 6: VERDE}

# ---------- Paso 4 · De la bitácora a canastas ----------
cb = m[(m.central == "Carboeléctrica Costa Brava") & (m.mes <= 3)]
W, H = 15, 4.6
fig, ax = lienzo(W, H)
filas = [(r.fecha.strftime("%Y-%m-%d"), r.tipo_evento) for r in cb.itertuples()]
cols = [MES[r.mes] for r in cb.itertuples()]
ce = tabla(ax, 1, 38, ["fecha", "tipo_evento"], [13, 17], filas, cols, alin=["left", "left"],
           rotulo="mant  (Costa Brava, enero a marzo)")
can = cb.groupby("mes")["tipo_evento"].apply(lambda s: sorted(set(s)))
fil2 = [(str(k), ", ".join(v)) for k, v in can.items()]
cc = tabla(ax, 78, 34, ["mes", "lo_que_pasó"], [6, 32], fil2, [MES[k] for k in can.index], rh=5,
           alin=["right", "left"], rotulo="canastas")
for i, r in enumerate(cb.itertuples()):
    j = list(can.index).index(r.mes)
    flecha(ax, (33, ce[i]), (75.5, cc[j]), color=MES[r.mes][0], lw=1.1)
ax.text(78, 9, "Cinco eventos quedan en tres canastas, una por mes.\nEn todo el año son 600 eventos y 215 canastas.", fontsize=10, va="top")
titulo(ax, "Una canasta junta todo lo que le pasó a una central en un mes",
       "Como una boleta de supermercado, que junta lo que se compró en una visita", W, H)
save(fig, "lab04_paso4_canastas")

# ---------- Paso 5 · Canastas en una tabla de sí o no ----------
mm = m[(m.central == "Carboeléctrica Costa Brava") & (m.mes <= 6)]
can = mm.groupby("mes")["tipo_evento"].apply(lambda s: sorted(set(s)))
W, H = 15, 5.0
fig, ax = lienzo(W, H)
fil2 = [(str(k), ", ".join(v)) for k, v in can.items()]
cc = tabla(ax, 1, 42, ["mes", "lo_que_pasó"], [6, 31], fil2, [MES[k] for k in can.index], rh=4.4,
           alin=["right", "left"], rotulo="canastas  (Costa Brava, enero a junio)")
flecha(ax, (41, 27), (52, 27), "crosstab")
x0, y0, rh = 56, 42, 4.4
cortos = ["correctivo", "climático", "f. eléctrica", "f. mecánica", "inspección", "preventivo"]
ax.text(x0, y0 + 1.6, "tabla  (una columna por tipo de evento)", fontsize=11, fontweight="bold", va="bottom")
ax.add_patch(Rectangle((x0, y0 - rh), 6, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
ax.text(x0 + 5, y0 - rh / 2, "mes", fontsize=10, fontweight="bold", color=MUTED, va="center", ha="right", family="DejaVu Sans Mono")
for k, t in enumerate(cortos):
    ax.add_patch(Rectangle((x0 + 6 + 13 * k, y0 - rh), 13, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
    ax.text(x0 + 6 + 13 * k + 6.5, y0 - rh / 2, t, fontsize=9.5, fontweight="bold", color=MUTED, va="center", ha="center")
for i, (mes, lista) in enumerate(can.items()):
    yy = y0 - rh * (i + 2)
    fuerte, tinte = MES[mes]
    ax.add_patch(Rectangle((x0 - 0.9, yy), 0.9, rh, facecolor=fuerte, edgecolor=SURF, lw=1.5))
    ax.add_patch(Rectangle((x0, yy), 6, rh, facecolor=tinte, edgecolor=SURF, lw=1.5))
    ax.text(x0 + 5, yy + rh / 2, str(mes), fontsize=10, va="center", ha="right", family="DejaVu Sans Mono")
    for k, t in enumerate(TIPOS):
        si = t in lista
        ax.add_patch(Rectangle((x0 + 6 + 13 * k, yy), 13, rh, facecolor=tinte if si else "#F8F9FA", edgecolor=SURF, lw=1.5))
        if si:
            ax.text(x0 + 6 + 13 * k + 6.5, yy + rh / 2, "✓", fontsize=12, va="center", ha="center", color=fuerte)
ax.text(x0, y0 - rh * 8 - 1, "Promediando una columna se obtiene en qué porcentaje de las canastas aparece.\n"
        "El preventivo aparece en el 56,3 por ciento de las 215 canastas del año.", fontsize=10, color=MUTED, va="top")
titulo(ax, "Cada canasta pasa a ser una fila de sí o no",
       "Las listas se convierten en una tabla con una columna por tipo de evento", W, H)
save(fig, "lab04_paso5_tabla")

# ---------- Paso 6 · Confianza contra lift ----------
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

# ---------- Paso 9 · Días hasta el correctivo ----------
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
