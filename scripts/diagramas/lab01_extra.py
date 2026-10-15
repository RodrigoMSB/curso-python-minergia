"""Diagramas nuevos del Lab 01 de la ruta guiada. Cifras sacadas de datos/."""
import json
from estilo import *

D = "datos/"
c = pd.read_csv(D + "centrales.csv")

def caja(ax, x, y, w, h, fill="#F8F9FA", edge=GRID, lw=1.2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw))

def nota(ax, x, y, t, color=MUTED, size=10, **k):
    ax.text(x, y, t, fontsize=size, color=color, va="top", **k)

# ---------- Paso 1 · Del archivo de texto a la tabla ----------
W, H = 15, 5.2
fig, ax = lienzo(W, H)
lineas = open(D + "centrales.csv", encoding="utf-8").read().splitlines()[:6]
caja(ax, 0, 6, 56, 40)
ax.text(1.5, 44, "centrales.csv, tal como viene", fontsize=10, color=MUTED, va="top")
for i, l in enumerate(lineas):
    ax.text(1.5, 38 - i * 5, l, fontsize=9.5, family="DejaVu Sans Mono", va="center",
            color=AZUL[0] if i == 0 else INK, fontweight="bold" if i == 0 else "normal")
nota(ax, 1.5, 4, "Es solo texto. Cada coma separa una columna.")
flecha(ax, (57.5, 26), (66.5, 26), "pd.read_csv")
filas = [(str(i), r.central.replace("Central ", ""), r.tecnologia, r.region, str(r.potencia_mw), str(r.anio_inicio))
         for i, r in c.head(5).iterrows()]
tabla(ax, 69, 44, ["", "central", "tecnologia", "region", "potencia_mw", "anio_inicio"], [3, 16, 12.5, 11, 13.5, 13.5],
      filas, [AZUL] * 5, rh=4.2, alin=["right", "left", "left", "left", "right", "right"], rotulo="centrales, ya como tabla")
ax.annotate("", xy=(69.5, 15), xytext=(69.5, 8), arrowprops=dict(arrowstyle="-|>", color=MORADO[0], lw=1.3))
nota(ax, 71, 9, "pandas agrega a la izquierda el número de fila,\nque se llama índice. No viene en el archivo.", color=MORADO[0])
nota(ax, 69, 51.5, "la primera línea del archivo pasa a ser el nombre de cada columna", color=AZUL[0])
titulo(ax, "read_csv convierte un archivo de texto en una tabla",
       "Las primeras líneas de centrales.csv, antes y después de leerlo", W, H + 0.5)
ax.set_ylim(0, (H + 0.5) * 10)
save(fig, "lab01_paso1_csv")

# ---------- Paso 2 · Cómo funciona el filtro ----------
W, H = 16, 5.8
fig, ax = lienzo(W, H)
sub = c.iloc[:8]
col = [AZUL if t == "hidro" else GRIS for t in sub.tecnologia]
ci = tabla(ax, 1, 52, ["", "central", "tecnologia"], [3, 28, 12],
           [(str(i), r.central, r.tecnologia) for i, r in sub.iterrows()], col, rh=4.2,
           alin=["right", "left", "left"], rotulo="centrales  (8 de las 20 filas)")
mask = tabla(ax, 53, 52, ['== "hidro"'], [12], [(str(t == "hidro"),) for t in sub.tecnologia],
             [VERDE if t == "hidro" else ROJO for t in sub.tecnologia], rh=4.2, alin=["left"], rotulo="la pregunta")
for y in ci:
    ax.annotate("", xy=(50, y), xytext=(45, y), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.9))
hid = sub[sub.tecnologia == "hidro"]
co = tabla(ax, 88, 52, ["", "central", "tecnologia"], [3, 28, 12],
           [(str(i), r.central, r.tecnologia) for i, r in hid.iterrows()], [AZUL] * len(hid), rh=4.2,
           alin=["right", "left", "left"], rotulo="filtradas")
for i, k in enumerate(hid.index):
    flecha(ax, (66, mask[k]), (86.5, co[i]), color=AZUL[0], lw=1.0)
nota(ax, 53, 12.5, "True deja pasar la fila.\nFalse la deja afuera.", color=INK, size=10.5)
nota(ax, 88, 23, "Pasan las 5 hidro, con su número de fila\noriginal. Si eligen solar, la tabla empieza\nen 5, porque el número no se renumera.", color=AZUL[0])
titulo(ax, "Un filtro pregunta fila por fila y deja pasar las que responden True",
       'centrales[centrales["tecnologia"] == "hidro"]', W, H)
save(fig, "lab01_paso2_filtro")

# ---------- Paso 3 · De dónde salen 175.680 filas ----------
W, H = 15, 4.6
fig, ax = lienzo(W, H)
fact = [("20", "centrales", AZUL), ("24", "horas al día", AMBAR), ("366", "días de 2024,\nque fue bisiesto", MORADO)]
x = 0
for i, (n, t, k) in enumerate(fact):
    ax.add_patch(Rectangle((x, 24), 22, 16, facecolor=k[1], edgecolor=k[0], lw=1.5))
    ax.text(x + 11, 34, n, ha="center", va="center", fontsize=22, fontweight="bold", color=k[0])
    ax.text(x + 11, 28.5, t, ha="center", va="center", fontsize=10, color=INK)
    x += 22
    ax.text(x + 3, 32, "×" if i < 2 else "=", ha="center", va="center", fontsize=22, color=MUTED)
    x += 6
ax.add_patch(Rectangle((x, 24), 30, 16, facecolor=VERDE[1], edgecolor=VERDE[0], lw=1.5))
ax.text(x + 15, 34, "175.680", ha="center", va="center", fontsize=22, fontweight="bold", color=VERDE[0])
ax.text(x + 15, 28.5, "filas en generacion", ha="center", va="center", fontsize=10)
assert 20 * 24 * 366 == 175680
g = pd.read_csv(D + "generacion.csv", nrows=3)
tabla(ax, 0, 16, ["fecha", "hora", "central", "mwh"], [22, 7, 28, 10],
      [(str(r.fecha) + " 00:00:00", str(r.hora), r.central, f"{r.mwh:.2f}") for r in g.itertuples()],
      [AZUL] * 3, rh=3.6, alin=["left", "right", "left", "right"])
nota(ax, 72, 14, 'Sin parse_dates la fecha llega como texto, "2024-01-01".\nCon parse_dates=["fecha"] pandas la convierte en fecha,\ny recién así se le puede pedir el mínimo y el máximo.', color=INK, size=10.5)
titulo(ax, "Una fila por central y por hora de todo el año",
       "Por eso el archivo es grande y la celda demora unos segundos", W, H)
ax.set_ylim(0, H * 10)
save(fig, "lab01_paso3_filas")

# ---------- Estudio 1 · Las tres preguntas a una tabla ----------
W, H = 15.5, 5.0
fig, ax = lienzo(W, H)
filas = [(str(i), r.central, r.tecnologia, r.region, str(r.potencia_mw), str(r.anio_inicio)) for i, r in c.head(4).iterrows()]
x0, y0 = 6, 40
anchos = [3, 27, 12.5, 11, 13.5, 13.5]
tabla(ax, x0, y0, ["", "central", "tecnologia", "region", "potencia_mw", "anio_inicio"], anchos, filas, [AZUL] * 4,
      rh=4.2, alin=["right", "left", "left", "left", "right", "right"])
ax.text(x0 + 1, y0 - 4.2 * 5 - 2.5, "…  16 filas más", fontsize=10, color=MUTED, va="center")
xp = x0 + sum(anchos[:4])
ax.add_patch(Rectangle((xp, y0 - 4.2 * 6), anchos[4], 4.2 * 6, facecolor="none", edgecolor=AMBAR[0], lw=2.2))
# filas
ax.annotate("", xy=(2, y0 - 4.2 * 6), xytext=(2, y0 - 4.2), arrowprops=dict(arrowstyle="<|-|>", color=MORADO[0], lw=1.5))
ax.text(0.5, y0 - 15, "20\nfilas", ha="right", va="center", fontsize=11, fontweight="bold", color=MORADO[0])
# columnas
xe = x0 + sum(anchos)
ax.annotate("", xy=(x0 + 3, y0 + 3), xytext=(xe, y0 + 3), arrowprops=dict(arrowstyle="<|-|>", color=VERDE[0], lw=1.5))
ax.text((x0 + 3 + xe) / 2, y0 + 4, "5 columnas", ha="center", va="bottom", fontsize=11, fontweight="bold", color=VERDE[0])
# panel derecho
px = 96
caja(ax, px, 6, 56, 38)
lines = [("centrales.shape", "(20, 5)", MORADO[0], "filas y columnas, en ese orden"),
         ("list(centrales.columns)", "5 nombres", VERDE[0], "los nombres de las columnas"),
         ('centrales["potencia_mw"].sum()', "4540", AMBAR[0], "suma la columna marcada, en MW")]
for i, (code, val, k, exp) in enumerate(lines):
    y = 39 - i * 11
    ax.text(px + 2, y, code, fontsize=10, family="DejaVu Sans Mono", va="top")
    ax.text(px + 2, y - 4, "→ " + val, fontsize=11, fontweight="bold", color=k, va="top", family="DejaVu Sans Mono")
    ax.text(px + 22, y - 4.3, exp, fontsize=10, color=MUTED, va="top")
nota(ax, 0, 5, "El índice de la izquierda no cuenta como columna.")
titulo(ax, "Tres preguntas que se le hacen a cualquier tabla apenas se abre",
       "Cuánto mide, qué columnas trae y cuánto suma lo que importa", W, H + 0.3)
ax.set_ylim(0, (H + 0.3) * 10)
save(fig, "lab01_estudio1_tamano")

# ---------- Estudio 2 · Agrupar y sumar ----------
W, H = 16, 8.6
fig, ax = lienzo(W, H)
paleta = dict(zip(["hidro", "solar", "eolica", "gas", "carbon", "diesel"], [AZUL, AMBAR, VERDE, MORADO, ROJO, GRIS]))
orden = list(c.groupby("tecnologia")["potencia_mw"].sum().sort_values().index)
cs = c.copy()
cs["k"] = cs.tecnologia.map(orden.index)
cs = cs.sort_values(["k"], kind="stable")
yi = tabla(ax, 1, 82, ["central", "tecnologia", "potencia_mw"], [33, 12.5, 13.5],
           [(r.central, r.tecnologia, str(r.potencia_mw)) for r in cs.itertuples()],
           [paleta[t] for t in cs.tecnologia], rh=3.6, alin=["left", "left", "right"],
           rotulo="1. separa las 20 centrales según su tecnología")
XB = 1 + 33 + 12.5 + 13.5 + 1
res = c.groupby("tecnologia")["potencia_mw"].agg(["sum", "count"]).sort_values("sum")
yo = tabla(ax, 108, 64, ["tecnologia", "potencia_mw"], [14, 15],
           [(t, str(int(r["sum"]))) for t, r in res.iterrows()], [paleta[t] for t in res.index], rh=4.4,
           alin=["left", "right"], rotulo="resumen")
pos = {t: i for i, t in enumerate(res.index)}
ys = dict(zip(range(len(cs)), yi))
for t in orden:
    idx = [i for i, tt in enumerate(cs.tecnologia) if tt == t]
    mid = (yi[idx[0]] + yi[idx[-1]]) / 2
    ax.plot([XB, XB + 1, XB + 1, XB], [yi[idx[0]] + 1.5, yi[idx[0]] + 1.5, yi[idx[-1]] - 1.5, yi[idx[-1]] - 1.5], color=paleta[t][0], lw=1.3)
    n = int(res.loc[t, "count"])
    detalle = " + ".join(str(v) for v in c[c.tecnologia == t].potencia_mw) if n > 1 else "sola"
    ax.text(XB + 3, mid + 1.2, f"{detalle}", fontsize=8.5, color=MUTED, va="bottom", family="DejaVu Sans Mono")
    flecha(ax, (XB + 28, mid), (106.5, yo[pos[t]]), color=paleta[t][0], lw=1.0)
nota(ax, XB + 3, 86, "2. suma la potencia de cada grupo", color=INK, size=11, fontweight="bold")
nota(ax, 108, 30, "3. sort_values ordena de menor\na mayor. Por eso hidro queda\nal final y en el gráfico es\nla barra de más arriba.", color=INK, size=10.5)
nota(ax, 108, 12, "20 filas entran y salen 6,\nuna por tecnología.", color=AZUL[0], size=10.5)
titulo(ax, "groupby separa en grupos, suma cada uno y entrega una fila por grupo",
       'centrales.groupby("tecnologia")["potencia_mw"].sum().sort_values()', W, H)
save(fig, "lab01_estudio2_groupby")

# ---------- Estudio 3 · Un Excel con varias hojas ----------
W, H = 17.2, 5.0
fig, ax = lienzo(W, H)
caja(ax, 0, 10, 40, 34, fill="#FFFFFF", edge=VERDE[0], lw=1.6)
ax.add_patch(Rectangle((0, 40), 40, 4, facecolor=VERDE[0], edgecolor=VERDE[0]))
ax.text(2, 42, "centrales.xlsx", color="white", fontsize=10.5, fontweight="bold", va="center")
for i in range(5):
    for j in range(4):
        ax.add_patch(Rectangle((2 + j * 9, 34 - i * 4.5), 9, 4.5, facecolor="#FFFFFF", edgecolor=GRID, lw=0.8))
ax.add_patch(Rectangle((2, 10), 13, 3.6, facecolor=VERDE[1], edgecolor=VERDE[0], lw=1.2))
ax.text(8.5, 11.8, "centrales", ha="center", va="center", fontsize=9.5, fontweight="bold")
ax.add_patch(Rectangle((15.5, 10), 10, 3.6, facecolor=AMBAR[1], edgecolor=AMBAR[0], lw=1.2))
ax.text(20.5, 11.8, "notas", ha="center", va="center", fontsize=9.5, fontweight="bold")
nota(ax, 0, 8, "Dos pestañas abajo, dos hojas")
# sin sheet_name, arriba
flecha(ax, (42, 37), (60, 37), None, color=VERDE[0])
ax.text(51, 39, "read_excel( ... )", ha="center", va="bottom", fontsize=9.5, family="DejaVu Sans Mono", color=MUTED)
caja(ax, 62, 31, 36, 12, fill=VERDE[1], edge=VERDE[0])
ax.text(63.5, 39.5, "primera", fontsize=10.5, family="DejaVu Sans Mono", fontweight="bold", va="center")
ax.text(63.5, 34.5, "tabla 20 × 5, la hoja centrales", fontsize=9.5, color=MUTED, va="center")
nota(ax, 101, 41, "Sin sheet_name, read_excel lee\nsolo la primera hoja.", color=INK, size=10.5)
# con sheet_name, abajo
flecha(ax, (42, 14), (60, 14), None, color=AMBAR[0])
ax.text(51, 16, 'sheet_name="notas"', ha="center", va="bottom", fontsize=9.5, family="DejaVu Sans Mono", color=AMBAR[0])
notas = pd.read_excel(D + "centrales.xlsx", sheet_name="notas")
tabla(ax, 62, 20, ["", "nota"], [3, 67], [(str(i), r.nota) for i, r in notas.iterrows()], [AMBAR] * 2, rh=4.4,
      alin=["right", "left"], rotulo="notas, lo que muestra la celda")
nota(ax, 136, 17, "Con sheet_name se lee\nla hoja que se nombra,\ntal como aparece en\nla pestaña.", color=INK, size=10.5)
titulo(ax, "sheet_name elige qué hoja del Excel se lee",
       "Un Excel puede traer varias hojas. Cada una se lee como una tabla", W, H)
save(fig, "lab01_estudio3_excel")

# ---------- Estudio 4 · De la respuesta del servicio a la tabla ----------
W, H = 16.6, 5.2
fig, ax = lienzo(W, H)
j = json.load(open(D + "precios_nudo.json", encoding="utf-8"))
caja(ax, 0, 4, 78, 44, fill="#F8F9FA")
ax.text(1.5, 46, "respuesta, lo que llega del servicio", fontsize=10, color=MUTED, va="top")
txt = [("{", INK), ('  "metadata": {', MUTED), (f'     "fuente": "{j["metadata"]["fuente"]}",', MUTED),
       (f'     "fecha_consulta": "{j["metadata"]["fecha_consulta"]}",', MUTED), (f'     "unidad": "{j["metadata"]["unidad"]}"', MUTED), ("  },", MUTED), ('  "datos": [', AZUL[0])]
for r in j["datos"][:3]:
    txt.append((f'     {{"fecha": "{r["fecha"]}", "hora": {r["hora"]}, "region": "{r["region"]}", "precio_usd_mwh": {r["precio_usd_mwh"]}}},', AZUL[0]))
txt += [(f"     ... {len(j['datos']):,} registros en total".replace(",", "."), AZUL[0]), ("  ]", AZUL[0]), ("}", INK)]
for i, (t, k) in enumerate(txt):
    ax.text(1.5, 41 - i * 3.0, t, fontsize=6.9, family="DejaVu Sans Mono", va="center", color=k)
ax.add_patch(Rectangle((0.8, 6.3), 76.4, 18.4, facecolor="none", edgecolor=AZUL[0], lw=1.6, ls="--"))
flecha(ax, (80, 22), (95, 22), None, color=AZUL[0])
ax.text(88.5, 25, 'pd.DataFrame(\nrespuesta["datos"])', ha="center", va="bottom", fontsize=9, family="DejaVu Sans Mono", color=MUTED)
tabla(ax, 99, 36, ["", "fecha", "hora", "region", "precio_usd_mwh"], [3, 12, 6, 14, 18],
      [(str(i), r["fecha"], str(r["hora"]), r["region"], f'{r["precio_usd_mwh"]:.2f}') for i, r in enumerate(j["datos"][:3])],
      [AZUL] * 3, rh=4.4, alin=["right", "left", "right", "left", "right"], rotulo="tabla")
nota(ax, 99, 14, "Cada registro pasa a ser una fila y cada llave\nuna columna. metadata queda afuera, solo describe\nlos datos.", color=INK, size=10.5)
titulo(ax, "Un servicio web responde en JSON y pd.DataFrame lo convierte en tabla",
       "La parte datos es una lista de registros con las mismas llaves", W, H)
save(fig, "lab01_estudio4_json")
print("ok")
