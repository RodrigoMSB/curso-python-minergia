import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import pandas as pd

D = "datos"
INK, MUTED, GRID, SURF = "#202124", "#5F6368", "#DADCE0", "#FFFFFF"
HEAD = "#F1F3F4"
# Pares (fuerte, tinte) para seguir a cada fila con su color
AZUL = ("#1a6fd4", "#dbe9fb"); AMBAR = ("#d99a00", "#fdf0c8"); MORADO = ("#7b4fc9", "#ece2fa")
VERDE = ("#1e8e3e", "#dcefe0")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK})

def es(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

from estilo import save

def lienzo(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w * 10); ax.set_ylim(0, h * 10); ax.axis("off")
    return fig, ax

def titulo(ax, t, sub, w, h):
    ax.text(0, h * 10 + 6, t, fontsize=15, fontweight="bold")
    ax.text(0, h * 10 + 1.5, sub, fontsize=11, color=MUTED)

def tabla(ax, x, y, cols, anchos, filas, colores, rh=4.2, rotulo=None, alin=None):
    """Dibuja una tabla con la esquina superior izquierda en (x, y). Devuelve el centro vertical de cada fila."""
    alin = alin or ["left"] * len(cols)
    if rotulo:
        ax.text(x, y + 1.6, rotulo, fontsize=11, fontweight="bold", va="bottom")
    cx = x
    for c, w, a in zip(cols, anchos, alin):
        ax.add_patch(Rectangle((cx, y - rh), w, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
        ax.text(cx + (w - 1 if a == "right" else 1), y - rh / 2, c, fontsize=10, fontweight="bold",
                color=MUTED, va="center", ha=a, family="DejaVu Sans Mono")
        cx += w
    centros = []
    for i, (fila, col) in enumerate(zip(filas, colores)):
        yy = y - rh * (i + 2)
        cx = x
        fuerte, tinte = col if col else (GRID, "#F8F9FA")
        for v, w, a in zip(fila, anchos, alin):
            ax.add_patch(Rectangle((cx, yy), w, rh, facecolor=tinte, edgecolor=SURF, lw=1.5))
            ax.text(cx + (w - 1 if a == "right" else 1), yy + rh / 2, v, fontsize=10, va="center", ha=a,
                    family="DejaVu Sans Mono", color=INK if col else "#9AA0A6")
            cx += w
        ax.add_patch(Rectangle((x - 0.9, yy), 0.9, rh, facecolor=fuerte, edgecolor=SURF, lw=1.5))
        centros.append(yy + rh / 2)
    return centros

def flecha(ax, a, b, texto=None, color=INK, rad=0.0, lw=1.4):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}"))
    if texto:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 2, texto, ha="center", va="bottom", fontsize=10,
                color=MUTED, family="DejaVu Sans Mono")

# ---------- Paso 5 · groupby con agg ----------
filas = [("Río Manso Alto", "hidro", 179.67), ("Pampa Alta", "solar", 81.80), ("Bahía Norte", "gas", 239.52),
         ("Aguas Claras", "hidro", 79.52), ("Sol Naciente", "solar", 54.49), ("Puerto Sur", "gas", 189.31),
         ("Tres Saltos", "hidro", 112.69)]
col = {"hidro": AZUL, "solar": AMBAR, "gas": MORADO}
W, H = 15, 5.6
fig, ax = lienzo(W, H)
tabla(ax, 1, 52, ["central", "tecnologia", "mwh"], [17, 13, 10],
      [(n, t, f"{m:.2f}") for n, t, m in filas], [col[t] for _, t, _ in filas], alin=["left", "left", "right"],
      rotulo="gen  (siete filas de las 175.680)")
# grupos
gy = 52
centros_g = {}
for t in ["hidro", "solar", "gas"]:
    sub = [f for f in filas if f[1] == t]
    c = tabla(ax, 52, gy, ["tecnologia", "mwh"], [13, 10], [(t, f"{m:.2f}") for _, _, m in sub], [col[t]] * len(sub),
              rh=3.6, alin=["left", "right"])
    centros_g[t] = (c[0] + c[-1]) / 2
    gy -= 3.6 * (len(sub) + 1) + 2.4
ax.text(52, 53.6, "1. separa por grupo", fontsize=11, fontweight="bold", va="bottom")
flecha(ax, (42.5, 30), (49.5, 30))
# resultado
res = []
for t in ["gas", "hidro", "solar"]:
    v = [m for _, tt, m in filas if tt == t]
    res.append((t, f"{sum(v):.1f}", f"{sum(v) / len(v):.1f}", str(len(v))))
tabla(ax, 86, 46, ["tecnologia", "total_mwh", "promedio_hora", "centrales"], [13, 13, 17, 13], res,
      [col[r[0]] for r in res], alin=["left", "right", "right", "right"],
      rotulo="2. tres cálculos por grupo, una fila por grupo")
flecha(ax, (77, 30), (84, 36))
ax.text(89, 18.5, 'total_mwh       =  ("mwh", "sum")      suma', fontsize=10, family="DejaVu Sans Mono", color=MUTED)
ax.text(89, 14.5, 'promedio_hora   =  ("mwh", "mean")     promedio', fontsize=10, family="DejaVu Sans Mono", color=MUTED)
ax.text(89, 10.5, 'centrales       =  ("central", "nunique")  cuántas distintas', fontsize=10, family="DejaVu Sans Mono", color=MUTED)
titulo(ax, "agg calcula varias cosas por grupo de una vez",
       "Siete filas del 1 de enero a mediodía. En Colab se hace lo mismo con las 175.680 filas del año", W, H)
save(fig, "lab02_paso5_agg")

# ---------- Paso 6 · pivot_table ----------
largo = [("Biobío", "carbon", 2698913), ("Biobío", "gas", 1688455), ("Biobío", "hidro", 4151930),
         ("Valparaíso", "eolica", 233637), ("Valparaíso", "gas", 2182673),
         ("Metropolitana", "diesel", 40710), ("Metropolitana", "gas", 1222999)]
rc = {"Biobío": AZUL, "Valparaíso": VERDE, "Metropolitana": MORADO}
techs = ["carbon", "diesel", "eolica", "gas", "hidro"]
W, H = 15, 5.0
fig, ax = lienzo(W, H)
tabla(ax, 1, 44, ["region", "tecnologia", "mwh"], [17, 13, 11],
      [(r, t, str(m)) for r, t, m in largo], [rc[r] for r, _, _ in largo], alin=["left", "left", "right"],
      rotulo="Tabla larga, una fila por combinación")
flecha(ax, (43, 28), (55, 28), "pivot_table")
ax.text(49, 24, "region queda\nen las filas\n\ntecnologia pasa\na columnas", ha="center", va="top", fontsize=9.5, color=MUTED)
# tabla ancha, celda por celda para pintar solo las que tienen dato
x0, y0, rh = 59, 44, 4.2
anchos = [17] + [10] * len(techs)
ax.text(x0, y0 + 1.6, "Tabla ancha, de doble entrada", fontsize=11, fontweight="bold", va="bottom")
cx = x0
for c, w in zip(["region"] + techs, anchos):
    ax.add_patch(Rectangle((cx, y0 - rh), w, rh, facecolor=HEAD, edgecolor=SURF, lw=1.5))
    ax.text(cx + (1 if c == "region" else w - 1), y0 - rh / 2, c, fontsize=10, fontweight="bold", color=MUTED,
            va="center", ha="left" if c == "region" else "right", family="DejaVu Sans Mono")
    cx += w
for i, reg in enumerate(["Biobío", "Metropolitana", "Valparaíso"]):
    yy = y0 - rh * (i + 2)
    fuerte, tinte = rc[reg]
    ax.add_patch(Rectangle((x0 - 0.9, yy), 0.9, rh, facecolor=fuerte, edgecolor=SURF, lw=1.5))
    ax.add_patch(Rectangle((x0, yy), 17, rh, facecolor=tinte, edgecolor=SURF, lw=1.5))
    ax.text(x0 + 1, yy + rh / 2, reg, fontsize=10, va="center", family="DejaVu Sans Mono")
    cx = x0 + 17
    for t in techs:
        v = [m for r, tt, m in largo if r == reg and tt == t]
        ax.add_patch(Rectangle((cx, yy), 10, rh, facecolor=tinte if v else "#F8F9FA", edgecolor=SURF, lw=1.5))
        ax.text(cx + 9, yy + rh / 2, str(v[0]) if v else "0", fontsize=10, va="center", ha="right",
                family="DejaVu Sans Mono", color=INK if v else "#9AA0A6")
        cx += 10
ax.text(x0, y0 - rh * 5 - 1, "Las casillas grises no tenían fila en la tabla larga.\nfill_value=0 las rellena con cero.",
        fontsize=10, color=MUTED, va="top")
titulo(ax, "pivot_table convierte filas en columnas",
       "Tres regiones de las siete, energía del año en MWh. Cada color sigue a su región", W, H)
save(fig, "lab02_paso6_pivot")

# ---------- Paso 8 · merge por tres llaves ----------
pre = [("2024-01-01", "0", "Antofagasta", "47.97"), ("2024-01-01", "1", "Antofagasta", "40.81"),
       ("2024-01-01", "0", "Atacama", "48.79"), ("2024-01-01", "1", "Atacama", "40.00")]
dem = [("2024-01-01", "0", "Atacama", "23.61"), ("2024-01-01", "1", "Antofagasta", "49.02"),
       ("2024-01-01", "1", "Atacama", "22.47"), ("2024-01-01", "0", "Antofagasta", "51.95")]
kc = {("0", "Antofagasta"): AZUL, ("1", "Antofagasta"): VERDE, ("0", "Atacama"): AMBAR, ("1", "Atacama"): MORADO}
W, H = 15, 6.6
fig, ax = lienzo(W, H)
ancho = [13, 6, 14, 17]
cp = tabla(ax, 1, 61, ["fecha", "hora", "region", "precio_usd_mwh"], ancho, pre,
           [kc[(h, r)] for _, h, r, _ in pre], alin=["left", "right", "left", "right"], rotulo="precios")
cd = tabla(ax, 1, 31, ["fecha", "hora", "region", "mwh"], [13, 6, 14, 17], dem,
           [kc[(h, r)] for _, h, r, _ in dem], alin=["left", "right", "left", "right"], rotulo="demanda  (en otro orden)")
# resultado
res = []
for f, h, r, p in pre:
    m = [x[3] for x in dem if x[1] == h and x[2] == r][0]
    res.append((f, h, r, p, m))
cr = tabla(ax, 80, 47, ["fecha", "hora", "region", "precio_usd_mwh", "mwh"], [13, 6, 14, 17, 8], res,
           [kc[(h, r)] for _, h, r, _, _ in res], alin=["left", "right", "left", "right", "right"],
           rotulo="mix")
for i, (f, h, r, p) in enumerate(pre):
    j = [k for k, x in enumerate(dem) if x[1] == h and x[2] == r][0]
    fuerte = kc[(h, r)][0]
    flecha(ax, (51.5, cp[i]), (78.5, cr[i]), color=fuerte, lw=1.2)
    flecha(ax, (51.5, cd[j]), (78.5, cr[i]), color=fuerte, lw=1.2)
ax.text(80, 21, "Una fila de precios se junta con la de demanda\nsolo si coinciden fecha, hora y región a la vez.",
        fontsize=10.5, va="top")
ax.text(80, 12, "La hora 0 de Antofagasta no se junta con la hora 0\nde Atacama. El orden de las filas no importa.",
        fontsize=10, color=MUTED, va="top")
titulo(ax, "Unir por tres columnas a la vez",
       'pd.merge(precios, demanda, on=["fecha", "hora", "region"])', W, H)
save(fig, "lab02_paso8_merge")

# ---------- Paso 9 · la cifra global engaña ----------
p = pd.json_normalize(json.load(open(f"{D}/precios_nudo.json"))["datos"]); p["fecha"] = pd.to_datetime(p["fecha"])
d = pd.read_csv(f"{D}/demanda.csv", parse_dates=["fecha"])
mix = pd.merge(p, d, on=["fecha", "hora", "region"])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"wspace": 0.28})
otras = mix[mix.region != "Metropolitana"]; met = mix[mix.region == "Metropolitana"]; ata = mix[mix.region == "Atacama"]
a1.scatter(otras.mwh, otras.precio_usd_mwh, s=4, color="#BDC1C6", alpha=0.5, lw=0)
a1.scatter(met.mwh, met.precio_usd_mwh, s=4, color=AZUL[0], alpha=0.35, lw=0)
a1.scatter(ata.mwh, ata.precio_usd_mwh, s=4, color=AMBAR[0], alpha=0.6, lw=0)
a1.text(820, 95, "Metropolitana", color=AZUL[0], fontsize=11, fontweight="bold", ha="center")
a1.text(110, 118, "las otras seis regiones,\namontonadas abajo", color=MUTED, fontsize=10, va="bottom")
a1.annotate("", xy=(140, 76), xytext=(170, 116), arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
a1.text(0.02, 0.97, "Todas juntas  0,979", transform=a1.transAxes, fontsize=14, fontweight="bold", va="top")
a1.text(0.02, 0.88, "parece una línea casi perfecta", transform=a1.transAxes, fontsize=10.5, color=MUTED, va="top")
a2.scatter(ata.mwh, ata.precio_usd_mwh, s=9, color=AMBAR[0], alpha=0.5, lw=0)
a2.text(0.02, 0.97, "Solo Atacama  0,125", transform=a2.transAxes, fontsize=14, fontweight="bold", va="top")
a2.text(0.02, 0.88, "una nube sin forma, casi no hay relación", transform=a2.transAxes, fontsize=10.5, color=MUTED, va="top")
for a in (a1, a2):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    for s in ("left", "bottom"): a.spines[s].set_color(GRID)
    a.tick_params(colors=MUTED, labelsize=9)
    a.set_xlabel("demanda en MWh por hora", color=MUTED, fontsize=10)
    a.set_ylabel("precio en USD por MWh", color=MUTED, fontsize=10)
a1.set_ylim(30, 180); a2.set_ylim(35, 70)
a1.set_xlim(0, 1000); a2.set_xticks([20, 25, 30, 35])
fig.text(0.125, 1.04, "Una cifra global puede esconder lo que pasa dentro de cada grupo", fontsize=15, fontweight="bold")
fig.text(0.125, 0.985, "Precio y demanda de cada hora de enero. Atacama en ámbar en los dos gráficos", fontsize=11, color=MUTED)
save(fig, "lab02_paso9_global")
print("ok")
