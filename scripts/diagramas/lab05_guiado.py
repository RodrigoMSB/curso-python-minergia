"""Diagramas del Lab 05 guiado, los mismos de la presentación corta del Lab 05. Cifras calculadas con datos/ y comprobadas con assert.

Se corre desde la raíz del repo.
    python scripts/diagramas/lab05_guiado.py
Deja ocho imágenes en modulos/modulo05/img/.
"""
import os, warnings
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
warnings.simplefilter("ignore")
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA, LatentDirichletAllocation
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import CountVectorizer

OUT = "modulos/modulo05/img"; os.makedirs(OUT, exist_ok=True)
DATOS = "datos"
INK, MUTED, GRID, SURF = "#202124", "#5F6368", "#DADCE0", "#FFFFFF"
HEAD, CELDA, APAGADO = "#F1F3F4", "#F8F9FA", "#E8EAED"
AZUL = ("#1A73E8", "#E8F0FE"); AMBAR = ("#D99A00", "#FEF3D6"); MORADO = ("#7B4FC9", "#ECE2FA")
VERDE = ("#188038", "#E6F4EA"); ROJO = ("#C5221F", "#FCE8E6"); GRIS = ("#80868B", "#F1F3F4")
TEC = {"hidro": ("hidro", AZUL), "solar": ("solar", AMBAR), "eolica": ("eólica", VERDE), "gas": ("gas", ROJO),
       "carbon": ("carbón", MORADO), "diesel": ("diésel", GRIS)}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.color": INK, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK})


def es(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def lienzo(w, h):
    fig = plt.figure(figsize=(w, h)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w * 10); ax.set_ylim(0, h * 10); ax.axis("off"); return fig, ax


def celda(ax, x, y, w, h, fondo, txt="", ha="center", **kw):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fondo, edgecolor=SURF, lw=2.5))
    if txt != "":
        xx = x + w / 2 if ha == "center" else x + 1.2
        ax.text(xx, y + h / 2, txt, ha=ha, va="center", **kw)


def ejes_limpios(a):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.spines["left"].set_color(GRID); a.spines["bottom"].set_color(GRID); a.tick_params(length=0, labelsize=12)


def guardar(fig, nombre):
    fig.savefig(os.path.join(OUT, nombre + ".png"), dpi=160, bbox_inches="tight", pad_inches=0.05, facecolor=SURF); plt.close(fig)


gen = pd.read_csv(os.path.join(DATOS, "generacion.csv"), parse_dates=["fecha"])
centrales = pd.read_csv(os.path.join(DATOS, "centrales.csv"))
mant = pd.read_csv(os.path.join(DATOS, "mantenimiento.csv"))
perfil = gen.pivot_table(index="central", columns="hora", values="mwh", aggfunc="mean")
potencia = centrales.set_index("central")["potencia_mw"]; tecnologia = centrales.set_index("central")["tecnologia"]
factor = perfil.div(potencia, axis=0)
X = StandardScaler().fit_transform(factor)
assert perfil.shape == (20, 24)

# ---------- Parte 1. Dos centrales, en megawatts y en forma ----------
dos = ["Carboeléctrica Costa Brava", "Central Vega Azul"]
assert round(perfil.loc[dos[0]].max(), 1) == 307.9
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.9), gridspec_kw={"wspace": 0.3})
for a, tabla, tit, yl in ((a1, perfil, "En megawatts, como vienen", "MWh promedio en esa hora"),
                          (a2, factor, "Divididos por su potencia, su forma", "parte de su potencia que usa")):
    for c, k in zip(dos, (MORADO, AZUL)):
        a.plot(range(24), tabla.loc[c].values, lw=3, color=k[0], label=c.replace("Carboeléctrica ", "").replace("Central ", ""))
    a.set_title(tit, loc="left", fontsize=14, fontweight="bold", color=INK, pad=10)
    a.set_xlabel("hora del día", fontsize=12); a.set_ylabel(yl, fontsize=12); a.set_xticks(range(0, 24, 6)); ejes_limpios(a)
    a.grid(axis="y", color=APAGADO, lw=1)
a1.legend(frameon=False, fontsize=12, loc="upper right", bbox_to_anchor=(1, 0.9)); a2.set_ylim(0, 1); a1.set_ylim(0, 340)
a1.text(6, 170, "una genera\n6 veces más", ha="center", fontsize=12, color=MUTED)
a2.text(12, 0.75, "son casi iguales,\nlas dos trabajan parejo\ntodo el día", ha="center", fontsize=12, color=MUTED)
guardar(fig, "lab05_parte1_forma")

# ---------- Parte 2. K-Means con 6 grupos ----------
km6 = KMeans(n_clusters=6, random_state=2026, n_init=10).fit(X)
ct6 = pd.crosstab(tecnologia[factor.index], km6.labels_)
assert (ct6.max(axis=1) == ct6.sum(axis=1)).all() and ct6.shape[1] == 6
grupos6 = {}
for g in sorted(set(km6.labels_)):
    miembros = ct6[g][ct6[g] > 0]; grupos6[g] = [(TEC[t][0], int(n), TEC[t][1]) for t, n in miembros.items()]
W, H = 12, 3.1
fig, ax = lienzo(W, H)
n = len(grupos6); w = (120 - 2 * (n - 1)) / n
for i, (g, miembros) in enumerate(sorted(grupos6.items())):
    x = i * (w + 2)
    ax.add_patch(FancyBboxPatch((x, 1), w, 27, boxstyle="round,pad=0,rounding_size=1.2", facecolor=HEAD, edgecolor=GRID, lw=1.5))
    ax.text(x + w / 2, 25.5, f"grupo {g}", ha="center", fontsize=12, color=MUTED, fontweight="bold")
    y = 19.0; cx = x + 2
    for nom, cnt, k in miembros:
        for _ in range(cnt):
            ax.add_patch(Circle((cx + 1.3, y), 1.2, facecolor=k[0], edgecolor="none"))
            cx += 2.9
            if cx > x + w - 3.5: cx = x + 2; y -= 2.9
        cx = x + 2; y -= 1.7
        ax.text(x + 2, y - 0.2, f"{cnt} {nom}", fontsize=11, color=k[0], fontweight="bold", va="top")
        y -= 4.0
guardar(fig, "lab05_parte2_kmeans6")

# ---------- Parte 2. El codo ----------
iner = [KMeans(n_clusters=k, random_state=2026, n_init=10).fit(X).inertia_ for k in range(1, 9)]
assert [round(v, 1) for v in iner[:4]] == [480.0, 91.8, 36.8, 12.5]
fig, a = plt.subplots(figsize=(12, 4.0))
a.plot(range(1, 9), iner, marker="o", lw=3, color=AZUL[0], markersize=10, zorder=3)
for k, v in zip(range(1, 9), iner):
    a.text(k, v + 18, es(v, 0 if v > 5 else 1), ha="center", fontsize=12, fontweight="bold")
a.axvline(5, color=AMBAR[0], lw=2, ls=(0, (4, 3))); a.text(5.1, 300, "desde 5 grupos\ncasi no queda nada", fontsize=12, color=AMBAR[0])
a.set_xlabel("cuántos grupos le pedimos", fontsize=12); a.set_ylabel("lo que queda sin explicar, la inercia", fontsize=12)
a.set_xticks(range(1, 9)); a.set_ylim(0, 540); ejes_limpios(a); a.grid(axis="y", color=APAGADO, lw=1)
guardar(fig, "lab05_parte2_codo")

# ---------- Parte 3. DBSCAN, el ruido de las eólicas ----------
pdia = gen.pivot_table(index=["central", "fecha"], columns="hora", values="mwh", aggfunc="mean")
fdia = pdia.div(pdia.index.get_level_values("central").map(potencia), axis=0)
Xd = StandardScaler().fit_transform(fdia); td = pdia.index.get_level_values("central").map(tecnologia)
db = DBSCAN(eps=1.5, min_samples=5).fit(Xd)
ctd = pd.crosstab(td, db.labels_)
assert int(ctd.loc["eolica", -1]) == 1464 and int((db.labels_ == -1).sum()) == 1464
filas = []
for t in ["hidro", "gas", "carbon", "solar", "diesel", "eolica"]:
    r = ctd.loc[t]
    filas.append((TEC[t][0], TEC[t][1], int(r.get(-1, 0)), int(r.sum())))
W, H = 12, 3.8
fig, ax = lienzo(W, H)
cols = [("tecnología", 20), ("días en la tabla", 22), ("en un grupo", 22), ("fuera de todo grupo, ruido", 36)]
ty, rh = 32, 4.4
x = 0
for nom, w in cols:
    celda(ax, x, ty, w, rh, HEAD, nom, fontsize=12, fontweight="bold", color=MUTED); x += w
for i, (nom, k, ruido, total) in enumerate(filas):
    y = ty - rh * (i + 1); x = 0
    vals = [nom, str(total), str(total - ruido), str(ruido)]
    for j, ((cn, w), v) in enumerate(zip(cols, vals)):
        resalta = ruido > 0 and j == 3
        celda(ax, x, y, w, rh, k[1] if j == 0 else (ROJO[1] if resalta else CELDA), v, fontsize=13,
              color=k[0] if j == 0 else (ROJO[0] if resalta else INK), fontweight="bold" if (j == 0 or resalta) else "normal")
        x += w
ax.text(0, 2.5, "1.464 es exactamente 4 centrales eólicas por 366 días. Ningún día de una eólica se parece lo suficiente a otro como para formar un grupo.",
        fontsize=12, va="center", color=ROJO[0], fontweight="bold")
guardar(fig, "lab05_parte3_ruido")

# ---------- Parte 3. Cinco días de una solar y cinco de una eólica ----------
sol = fdia.loc["Parque Solar Altiplano"].iloc[:5]; eol = fdia.loc["Eólica Cerro Negro"].iloc[:5]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True, gridspec_kw={"wspace": 0.12})
for a, tabla, tit, k in ((a1, sol, "Cinco días de una solar", AMBAR), (a2, eol, "Cinco días de una eólica", VERDE)):
    for _, fila in tabla.iterrows(): a.plot(range(24), fila.values, lw=2.2, color=k[0], alpha=0.7)
    a.set_title(tit, loc="left", fontsize=14, fontweight="bold", color=INK, pad=10)
    a.set_xlabel("hora del día", fontsize=12); a.set_xticks(range(0, 24, 6)); ejes_limpios(a); a.grid(axis="y", color=APAGADO, lw=1)
a1.set_ylabel("parte de su potencia que usa", fontsize=12); a1.set_ylim(0, 0.75)
a1.text(12, 0.62, "cada día se parece al anterior", ha="center", fontsize=12, color=MUTED)
a2.text(12, 0.68, "cada día es distinto, manda el viento", ha="center", fontsize=12, color=MUTED)
guardar(fig, "lab05_parte3_solar_eolica")

# ---------- Estudio 1. PCA, las veinte centrales en un plano ----------
pca = PCA(n_components=2).fit(X); Z = pca.transform(X)
assert round(pca.explained_variance_ratio_[0], 2) == 0.94
fig, a = plt.subplots(figsize=(12, 4.6))
for t in ["carbon", "gas", "hidro", "eolica", "solar", "diesel"]:
    m = (tecnologia[factor.index] == t).values
    nom, k = TEC[t]; a.scatter(Z[m, 0], Z[m, 1], s=140, color=k[0], label=nom, alpha=0.85, edgecolor=SURF, lw=1.5)
a.set_title("Las veinte centrales en dos dimensiones. De 24 números a 2, y las de una tecnología caen juntas", loc="left", fontsize=13, fontweight="bold", pad=10)
a.set_xlabel(f"componente 1, conserva el {es(pca.explained_variance_ratio_[0] * 100, 0)} % de la variación", fontsize=12)
a.set_ylabel(f"componente 2, el {es(pca.explained_variance_ratio_[1] * 100, 0)} %", fontsize=12)
a.legend(frameon=False, fontsize=12, ncol=3, loc="lower right"); ejes_limpios(a); a.grid(color=APAGADO, lw=1)
guardar(fig, "lab05_estudio1_pca")

# ---------- Estudio 2. La silueta ----------
sil = [silhouette_score(X, KMeans(n_clusters=k, random_state=2026, n_init=10).fit_predict(X)) for k in range(2, 8)]
assert round(sil[4], 2) == 0.92 and sil[4] == max(sil)
fig, a = plt.subplots(figsize=(12, 3.8))
a.plot(range(2, 8), sil, marker="o", lw=3, color=VERDE[0], markersize=10, zorder=3)
for k, v in zip(range(2, 8), sil):
    a.text(k, v + 0.03, es(v, 2), ha="center", fontsize=12, fontweight="bold")
a.set_xlabel("cuántos grupos le pedimos", fontsize=12); a.set_ylabel("silueta, cerca de 1 es mejor", fontsize=12)
a.set_xticks(range(2, 8)); a.set_ylim(0.5, 1.05); ejes_limpios(a); a.grid(axis="y", color=APAGADO, lw=1)
a.text(6, 0.62, "con 6 grupos la silueta es la más alta.\nEs lo mismo que dijo el codo", ha="center", fontsize=12, color=MUTED)
guardar(fig, "lab05_estudio2_silueta")

# ---------- Estudio 3. LDA, temas contra tipo de evento ----------
VACIAS = ["el", "la", "los", "las", "un", "una", "de", "del", "en", "y", "se", "que", "por", "con",
          "sobre", "tras", "su", "sus", "al", "lo", "es", "durante", "ronda", "turno", "registra",
          "detecta", "reporta", "evento", "operador", "revisa"]
vec = CountVectorizer(stop_words=VACIAS, max_df=0.9, min_df=3)
matriz = vec.fit_transform(mant["observacion"])
lda = LatentDirichletAllocation(n_components=6, random_state=2026).fit(matriz)
dominante = lda.transform(matriz).argmax(axis=1)
ctl = pd.crosstab(mant["tipo_evento"], dominante)
assert ctl.shape == (6, 6) and int(ctl.loc["correctivo"].max()) == int(ctl.loc["correctivo"].sum())
nombres = {"preventivo": "preventivo", "correctivo": "correctivo", "inspeccion": "inspección",
           "falla_mecanica": "falla mecánica", "falla_electrica": "falla eléctrica", "evento_climatico": "evento climático"}
W, H = 12, 4.2
fig, ax = lienzo(W, H)
cw, fw, rh = 24, 14, 4.4
ty = 36
celda(ax, 0, ty, cw, rh, HEAD, "tipo de evento", fontsize=12, fontweight="bold", color=MUTED)
for j in range(6):
    celda(ax, cw + j * fw, ty, fw, rh, HEAD, f"tema {j}", fontsize=12, fontweight="bold", color=MUTED)
maximo = ctl.values.max()
for i, tipo in enumerate(ctl.index):
    y = ty - rh * (i + 1)
    celda(ax, 0, y, cw, rh, CELDA, nombres[tipo], ha="left", fontsize=12, fontweight="bold")
    for j in range(6):
        v = int(ctl.loc[tipo, j])
        fondo = AZUL[1] if v > 0 else CELDA
        celda(ax, cw + j * fw, y, fw, rh, fondo, str(v) if v else "", fontsize=13,
              color=AZUL[0] if v >= maximo * 0.5 else INK, fontweight="bold" if v >= maximo * 0.5 else "normal")
ax.text(0, 2.5, "Cada fila es un tipo de evento de la bitácora. Cada columna, un tema que LDA armó solo con las palabras. Casi todos los tipos caen en uno o dos temas.",
        fontsize=11.5, va="center", color=MUTED)
guardar(fig, "lab05_estudio3_lda")

print("inercias", [round(v, 1) for v in iner])
print("siluetas", [round(v, 3) for v in sil])
print("pca", pca.explained_variance_ratio_.round(3))
print(ctl)
print("Listo,", len(os.listdir(OUT)), "imágenes en", OUT)
