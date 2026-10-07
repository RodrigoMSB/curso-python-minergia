from estilo import *
from matplotlib.patches import Ellipse

# ---------- Paso 8 · La base hace el cálculo ----------
W, H = 15, 5.0
fig, ax = lienzo(W, H)
# cilindro de la base
cx, cy, ancho, alto = 13, 22, 21, 20
ax.add_patch(Rectangle((cx - ancho / 2, cy - alto / 2), ancho, alto, facecolor=AZUL[1], edgecolor="none"))
ax.add_patch(Ellipse((cx, cy - alto / 2), ancho, 5, facecolor=AZUL[1], edgecolor=AZUL[0], lw=1.5))
ax.add_patch(Rectangle((cx - ancho / 2, cy - alto / 2), ancho, alto, facecolor=AZUL[1], edgecolor="none"))
ax.plot([cx - ancho / 2] * 2, [cy - alto / 2, cy + alto / 2], color=AZUL[0], lw=1.5)
ax.plot([cx + ancho / 2] * 2, [cy - alto / 2, cy + alto / 2], color=AZUL[0], lw=1.5)
ax.add_patch(Ellipse((cx, cy + alto / 2), ancho, 5, facecolor="#c4dbf7", edgecolor=AZUL[0], lw=1.5))
ax.text(cx, cy + 1, "demanda.db", ha="center", fontsize=12, fontweight="bold", family="DejaVu Sans Mono")
ax.text(cx, cy - 4, "61.488 filas\nuna por región y hora", ha="center", va="top", fontsize=10, color=MUTED)
# consulta
ax.add_patch(Rectangle((30, 12), 44, 21, facecolor="#F8F9FA", edgecolor=GRID, lw=1.2))
ax.text(32, 30.5, "consulta", fontsize=10, color=MUTED, va="top")
ax.text(32, 26.5, "SELECT region, SUM(mwh) AS demanda_total\nFROM demanda\nGROUP BY region\nORDER BY demanda_total DESC",
        fontsize=10, family="DejaVu Sans Mono", va="top", linespacing=1.6)
ax.annotate("", xy=(22, 22.5), xytext=(29.5, 22.5), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
ax.text(52, 9, "1. la pregunta viaja a la base", ha="center", fontsize=10, color=MUTED)
# resultado
res = [("Metropolitana", "7779657.53"), ("Valparaíso", "1825770.20"), ("Biobío", "1632753.33"),
       ("Los Lagos", "864564.87"), ("Coquimbo", "816624.13"), ("Antofagasta", "672440.52"), ("Atacama", "307486.00")]
c = tabla(ax, 92, 42, ["region", "demanda_total"], [16, 17], res, [AZUL] * 7, rh=3.9, alin=["left", "right"],
          rotulo="lo que llega a Colab")
flecha(ax, (cx, cy - alto / 2 - 3), (90, 15), None, rad=0.25)
ax.set_ylim(-8, H * 10); ax.text(56, -6, "2. la base suma y devuelve 7 filas, no 61.488", ha="center", fontsize=10.5, fontweight="bold")
titulo(ax, "La base de datos hace el cálculo y entrega solo el resumen",
       "Demanda total del año por región, calculada dentro de la base", W, H)
save(fig, "lab01_paso8_sql")

# ---------- Paso 9 · inner contra left ----------
gen = [("Río Manso Alto", "6671.4"), ("Bahía Norte", "6005.6"), ("Pampa Alta", "331.4"),
       ("Loma Fría", "613.0"), ("Vega Azul", "1529.7"), ("Respaldo Cordillera", "111.4")]
fich = [("Río Manso Alto", "hidro"), ("Bahía Norte", "gas"), ("Pampa Alta", "solar")]
cols = [AZUL, MORADO, AMBAR, ROJO, ROJO, ROJO]
W, H = 15, 7.4
fig, ax = lienzo(W, H)
cg = tabla(ax, 1, 62, ["central", "mwh_del_dia"], [23, 14], gen, cols, alin=["left", "right"],
           rotulo="un_dia  (6 de las 20 centrales)")
cf = tabla(ax, 1, 25, ["central", "tecnologia"], [23, 13], fich, cols[:3], alin=["left", "left"],
           rotulo="fichas  (faltan 3 centrales)")
ax.text(1, 3, "Loma Fría, Vega Azul y Respaldo Cordillera\nno tienen ficha", fontsize=10, color=ROJO[0])
# inner
ci = tabla(ax, 74, 62, ["central", "mwh", "tecnologia"], [23, 10, 13], [(g[0], g[1], f[1]) for g, f in zip(gen, fich)],
           cols[:3], alin=["left", "right", "left"], rotulo='how="inner"')
ax.text(74, 40.5, "Las 3 sin ficha desaparecen sin aviso.\nTotal del día 50395.9 de 52650.0 MWh", fontsize=10, va="top",
        color=ROJO[0])
cl = tabla(ax, 74, 30, ["central", "mwh", "tecnologia"], [23, 10, 13],
           [(g[0], g[1], f[1]) for g, f in zip(gen, fich)] + [(g[0], g[1], "NaN") for g in gen[3:]],
           cols, alin=["left", "right", "left"], rotulo='how="left"')
ax.text(74, 0, "Se quedan todas, con la ficha vacía. Total 52650.0 MWh", fontsize=10, va="top", color=VERDE[0])
for i in range(3):
    flecha(ax, (40, cg[i]), (71.5, ci[i]), color=cols[i][0], lw=1.1)
for i in range(3, 6):
    flecha(ax, (40, cg[i]), (71.5, cl[i]), color=ROJO[0], lw=1.1)
titulo(ax, "Unir con inner pierde las filas que no encuentran pareja",
       "Generación del 15 de junio unida con una tabla de fichas incompleta", W, H)
save(fig, "lab01_paso9_join")

# ---------- Paso 10 · Una ficha repetida duplica sus horas ----------
W, H = 15, 5.4
fig, ax = lienzo(W, H)
g3 = [("Río Manso Alto", "0", "279.46"), ("Río Manso Alto", "1", "265.05"), ("Río Manso Alto", "2", "266.85")]
cg = tabla(ax, 1, 44, ["central", "hora", "mwh"], [17, 6, 9], g3, [AZUL] * 3, alin=["left", "right", "right"],
           rotulo="un_dia  (3 de sus 24 horas)")
cf = tabla(ax, 1, 20, ["central", "tecnologia"], [17, 13], [("Río Manso Alto", "hidro"), ("Río Manso Alto", "hidro")],
           [AZUL, ROJO], alin=["left", "left"], rotulo="fichas_repetidas  (la ficha aparece dos veces)")
filas = []
for c_, h, m in g3:
    filas += [(c_, h, m, "hidro"), (c_, h, m, "hidro")]
cr = tabla(ax, 84, 50, ["central", "hora", "mwh", "tecnologia"], [17, 6, 9, 13], filas,
           [AZUL, ROJO] * 3, rh=3.9, alin=["left", "right", "right", "left"], rotulo="unido")
for i in range(3):
    flecha(ax, (42, cg[i]), (81.5, cr[2 * i]), color=AZUL[0], lw=1.1)
    flecha(ax, (42, cg[i]), (81.5, cr[2 * i + 1]), color=ROJO[0], lw=1.1)
ax.text(84, 17, "Cada hora calza con las dos fichas y queda dos veces.", fontsize=10.5, va="top")
ax.text(84, 11, "Con dos centrales repetidas, 480 filas pasan a 528\ny el día suma 64298.7 MWh en vez de 52650.0.",
        fontsize=10, va="top", color=ROJO[0])
titulo(ax, "Una ficha repetida duplica todas las horas de su central",
       "Nada da error. Solo se nota contando filas y comparando el total", W, H)
save(fig, "lab01_paso10_repetidas")
print("ok")
