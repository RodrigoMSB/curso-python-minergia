#!/usr/bin/env python3
"""Generador de datos sinteticos del Observatorio de Datos Energeticos (ODE).

Caso conductor del curso "Analisis Avanzado de Datos con Python" dictado por
Xpertis para la Subsecretaria de Energia de Chile.

Produce todos los archivos de ``datos/`` de forma determinista a partir de una
semilla fija. Ejecutar el script dos veces genera archivos identicos byte a byte.

Uso:
    uv run python scripts/generar_datos.py              # datasets del curso
    uv run python scripts/generar_datos.py --grande     # + dataset grande local
    uv run python scripts/generar_datos.py --solo-grande

Las cifras son sinteticas pero verosimiles para el Sistema Electrico Nacional.
Ninguna central corresponde a una instalacion real.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Configuracion global
# --------------------------------------------------------------------------- #

SEMILLA = 2026

#: Desplazamientos de semilla por dataset. Mantenerlos fijos preserva el
#: determinismo aunque se agreguen datasets nuevos al final de la lista.
SEMILLAS = {
    "centrales": 0,
    "generacion_2024": 100,
    "demanda_2024": 200,
    "demanda_sucia": 300,
    "mantenimiento": 400,
    "precios_nudo": 500,
    "generacion_2025": 600,
    "demanda_2025": 700,
    "grande": 800,
}

RAIZ = Path(__file__).resolve().parents[1]
DIR_DATOS = RAIZ / "datos"
DIR_API = DIR_DATOS / "api"
DIR_GRANDE = DIR_DATOS / "grande"

#: Fecha fija estampada en los metadatos del XLSX para que el zip sea reproducible.
FECHA_FIJA = datetime(2026, 1, 1, 0, 0, 0)

REGIONES = [
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaiso",
    "Metropolitana",
    "Biobio",
    "Los Lagos",
]

#: Poblacion aproximada por region (proyeccion INE, redondeada).
POBLACION = {
    "Antofagasta": 691_000,
    "Atacama": 314_000,
    "Coquimbo": 836_000,
    "Valparaiso": 1_960_000,
    "Metropolitana": 8_125_000,
    "Biobio": 1_663_000,
    "Los Lagos": 891_000,
}

#: Demanda media horaria base por region, en MWh. La Metropolitana es
#: exactamente el doble de la mayor de las demas (Antofagasta).
DEMANDA_BASE = {
    "Metropolitana": 2300.0,
    "Antofagasta": 1150.0,
    "Biobio": 1100.0,
    "Valparaiso": 950.0,
    "Atacama": 700.0,
    "Coquimbo": 560.0,
    "Los Lagos": 430.0,
}

#: Perfil diario de demanda: valle de madrugada, punta de mediodia y punta de las 20.
PERFIL_DEMANDA = np.array(
    [
        0.88, 0.82, 0.77, 0.74, 0.73, 0.76,  # 0-5   valle de madrugada
        0.84, 0.93, 1.00, 1.04, 1.07, 1.10,  # 6-11  subida matinal
        1.13, 1.15, 1.12, 1.06, 1.02, 1.03,  # 12-17 punta de mediodia
        1.08, 1.15, 1.20, 1.14, 1.04, 0.95,  # 18-23 punta de las 20
    ]
)

HORAS = np.arange(24)

TECNOLOGIAS = ["hidro", "solar", "eolica", "gas", "carbon", "diesel"]


def _rng(clave: str) -> np.random.Generator:
    """Generador aleatorio reproducible para un dataset dado."""
    return np.random.default_rng(SEMILLA + SEMILLAS[clave])


def _horas_del_anio(anio: int) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray]:
    """Devuelve (fechas diarias, dia del anio 1..N, horas 0..23 repetidas)."""
    fechas = pd.date_range(f"{anio}-01-01", f"{anio}-12-31", freq="D")
    dia_anio = np.arange(1, len(fechas) + 1)
    return fechas, dia_anio, HORAS


def _escribir_csv(df: pd.DataFrame, ruta: Path, **kwargs) -> None:
    """Escribe un CSV determinista (UTF-8, LF, sin indice)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8", lineterminator="\n", **kwargs)


# --------------------------------------------------------------------------- #
# 4.1 Tabla maestra de centrales
# --------------------------------------------------------------------------- #

#: Catalogo fijo de centrales. Nombres inventados, sin correspondencia con
#: instalaciones reales del Sistema Electrico Nacional.
CATALOGO_CENTRALES = [
    # (central, tecnologia, region, potencia_mw, anio_inicio)
    ("Central Rio Manso Alto", "hidro", "Biobio", 420, 1998),
    ("Central Salto del Pehuen", "hidro", "Biobio", 310, 2004),
    ("Central Quebrada Azul", "hidro", "Los Lagos", 185, 2011),
    ("Central Lago Ventisquero", "hidro", "Los Lagos", 96, 2016),
    ("Central Vega Escondida", "hidro", "Biobio", 240, 1995),
    ("Parque Solar Pampa Alta", "solar", "Antofagasta", 230, 2017),
    ("Parque Solar Llano Blanco", "solar", "Antofagasta", 145, 2019),
    ("Parque Solar Salar Nuevo", "solar", "Atacama", 195, 2018),
    ("Parque Solar Cerro Dorado", "solar", "Atacama", 110, 2021),
    ("Parque Solar Media Luna", "solar", "Atacama", 78, 2023),
    ("Eolica Cerro Negro", "eolica", "Coquimbo", 160, 2015),
    ("Eolica Punta Ventosa", "eolica", "Coquimbo", 124, 2020),
    ("Eolica Loma Larga", "eolica", "Biobio", 98, 2013),
    ("Eolica Vientos del Sur", "eolica", "Los Lagos", 142, 2022),
    ("Termoelectrica Bahia Norte", "gas", "Antofagasta", 375, 2007),
    ("Termoelectrica Valle Central", "gas", "Metropolitana", 290, 2010),
    ("Termoelectrica Puerto Nuevo", "gas", "Valparaiso", 340, 2003),
    ("Termoelectrica Costa Brava", "carbon", "Valparaiso", 480, 1999),
    ("Termoelectrica Peninsula Gris", "carbon", "Biobio", 355, 2001),
    ("Diesel Respaldo Cordillera", "diesel", "Metropolitana", 45, 2012),
]


def construir_centrales() -> pd.DataFrame:
    """Tabla maestra de las 20 centrales del ODE."""
    return pd.DataFrame(
        CATALOGO_CENTRALES,
        columns=["central", "tecnologia", "region", "potencia_mw", "anio_inicio"],
    )


def escribir_centrales(centrales: pd.DataFrame) -> None:
    """Escribe centrales.csv y centrales.xlsx (con segunda hoja ``notas``)."""
    _escribir_csv(centrales, DIR_DATOS / "centrales.csv")

    notas = pd.DataFrame(
        {
            "nota": [
                "Datos sinteticos generados para el curso de Python de la "
                "Subsecretaria de Energia. Ninguna central corresponde a una "
                "instalacion real del Sistema Electrico Nacional.",
                "La potencia esta expresada en MW y el anio de inicio "
                "corresponde a la entrada en operacion comercial simulada. "
                "Regenerar con scripts/generar_datos.py.",
            ]
        }
    )

    ruta = DIR_DATOS / "centrales.xlsx"
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        centrales.to_excel(writer, sheet_name="centrales", index=False)
        notas.to_excel(writer, sheet_name="notas", index=False)
        propiedades = writer.book.properties
        propiedades.created = FECHA_FIJA
        propiedades.modified = FECHA_FIJA
        propiedades.creator = "Xpertis"
        propiedades.lastModifiedBy = "Xpertis"
    _normalizar_zip(ruta)


def _normalizar_zip(ruta: Path) -> None:
    """Reescribe un zip (xlsx) con timestamps fijos para que sea reproducible.

    openpyxl sobrescribe ``dcterms:modified`` con la hora del sistema al
    guardar, asi que ademas de fijar los timestamps de las entradas del zip
    hay que reemplazar esa marca dentro de ``docProps/core.xml``.
    """
    marca = FECHA_FIJA.strftime("%Y-%m-%dT%H:%M:%SZ").encode()
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with zipfile.ZipFile(ruta) as entrada:
        nombres = sorted(entrada.namelist())
        contenidos = {nombre: entrada.read(nombre) for nombre in nombres}
    if "docProps/core.xml" in contenidos:
        contenidos["docProps/core.xml"] = re.sub(
            rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:)",
            lambda m: m.group(1) + marca + m.group(2),
            contenidos["docProps/core.xml"],
        )
    with zipfile.ZipFile(temporal, "w", zipfile.ZIP_DEFLATED) as salida:
        for nombre in nombres:
            info = zipfile.ZipInfo(nombre, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            salida.writestr(info, contenidos[nombre])
    temporal.replace(ruta)


# --------------------------------------------------------------------------- #
# 4.2 Generacion horaria
# --------------------------------------------------------------------------- #

def _bloques_mantenimiento(
    n_horas: int, rng: np.random.Generator, fraccion: float = 0.02
) -> np.ndarray:
    """Mascara booleana de horas en cero por mantenimiento.

    Los ceros se agrupan en bloques contiguos de 1 a 3 dias hasta cubrir
    aproximadamente ``fraccion`` de las horas del periodo.
    """
    objetivo = int(round(n_horas * fraccion))
    mascara = np.zeros(n_horas, dtype=bool)
    acumulado = 0
    while acumulado < objetivo:
        dias = int(rng.integers(1, 4))
        largo = min(dias * 24, objetivo - acumulado)
        inicio = int(rng.integers(0, n_horas - largo))
        if mascara[inicio : inicio + largo].any():
            continue
        mascara[inicio : inicio + largo] = True
        acumulado += largo
    return mascara


def _ar1(n: int, rng: np.random.Generator, phi: float = 0.92) -> np.ndarray:
    """Proceso AR(1) estacionario vectorizado (kernel truncado)."""
    ruido = rng.standard_normal(n + 200)
    kernel = phi ** np.arange(200)
    serie = np.convolve(ruido, kernel, mode="valid")[:n]
    return serie * np.sqrt(1 - phi**2)


def _perfil_solar() -> np.ndarray:
    """Campana solar horaria: cero entre las 20 y las 6, maximo al mediodia."""
    perfil = np.clip(np.sin(np.pi * (HORAS - 6.5) / 13.0), 0.0, None)
    perfil[(HORAS < 7) | (HORAS >= 20)] = 0.0
    return perfil


def _serie_central(
    tecnologia: str,
    potencia: int,
    dia_anio: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Serie horaria de generacion (MWh) para una central, ordenada dia-hora."""
    n_dias = len(dia_anio)
    n_horas = n_dias * 24
    angulo = 2 * np.pi * dia_anio / n_dias

    if tecnologia == "solar":
        # Campana diaria + estacionalidad de verano + nubosidad diaria.
        estacional = 1 + 0.22 * np.cos(angulo - 2 * np.pi * 15 / n_dias)
        nubosidad = np.clip(rng.normal(1.0, 0.07, n_dias), 0.55, 1.05)
        matriz = (
            potencia
            * 0.75
            * _perfil_solar()[None, :]
            * (estacional * nubosidad)[:, None]
        )

    elif tecnologia == "eolica":
        # Ruido persistente alto + leve refuerzo vespertino. El piso es
        # positivo (turbina en vacio) para que el unico cero exacto de la
        # serie provenga de los bloques de mantenimiento.
        base = np.clip(0.35 + 0.22 * _ar1(n_horas, rng), 0.02, 0.95)
        tarde = 1 + 0.12 * np.clip(np.sin(np.pi * (HORAS - 9) / 14.0), 0, None)
        matriz = potencia * base.reshape(n_dias, 24) * tarde[None, :]

    elif tecnologia == "hidro":
        # Estable, con maximo en primavera por deshielos (peak ~1 de noviembre).
        estacional = 1 + 0.25 * np.cos(angulo - 2 * np.pi * 305 / n_dias)
        factor_base = rng.uniform(0.50, 0.68)
        diario = 1 + 0.08 * (PERFIL_DEMANDA - PERFIL_DEMANDA.mean())
        ruido = rng.normal(1.0, 0.04, (n_dias, 24))
        matriz = (
            potencia * factor_base * estacional[:, None] * diario[None, :] * ruido
        )

    elif tecnologia == "diesel":
        # Solo horas punta (18 a 22) y solo en parte de los dias.
        factor_base = rng.uniform(0.50, 0.90)
        invierno = 0.18 + 0.22 * np.clip(np.cos(angulo - 2 * np.pi * 182 / n_dias), 0, None)
        activo = rng.random(n_dias) < invierno
        punta = np.zeros(24)
        punta[18:23] = 1.0
        ruido = rng.normal(1.0, 0.08, (n_dias, 24))
        matriz = potencia * factor_base * activo[:, None] * punta[None, :] * ruido

    else:  # gas, carbon
        # Operacion de base con factor de planta entre 0.5 y 0.9.
        factor_base = rng.uniform(0.50, 0.90)
        deriva = 1 + 0.10 * _ar1(n_dias, rng, phi=0.85)
        diario = 1 + 0.08 * (PERFIL_DEMANDA - PERFIL_DEMANDA.mean())
        ruido = rng.normal(1.0, 0.03, (n_dias, 24))
        matriz = potencia * factor_base * deriva[:, None] * diario[None, :] * ruido

    serie = np.clip(matriz.reshape(-1), 0.0, None)
    serie[_bloques_mantenimiento(n_horas, rng)] = 0.0
    return np.round(np.minimum(serie, float(potencia)), 2)


def generar_generacion(anio: int, centrales: pd.DataFrame, clave: str) -> pd.DataFrame:
    """Generacion horaria por central para un anio completo."""
    rng = _rng(clave)
    fechas, dia_anio, _ = _horas_del_anio(anio)
    n_horas = len(fechas) * 24

    columnas = [
        _serie_central(fila.tecnologia, fila.potencia_mw, dia_anio, rng)
        for fila in centrales.itertuples()
    ]
    valores = np.stack(columnas, axis=1).reshape(-1)  # orden: fecha, hora, central

    n_centrales = len(centrales)
    return pd.DataFrame(
        {
            "fecha": np.repeat(
                fechas.strftime("%Y-%m-%d").to_numpy(), 24 * n_centrales
            ),
            "hora": np.tile(np.repeat(HORAS, n_centrales), len(fechas)),
            "central": np.tile(centrales["central"].to_numpy(), n_horas),
            "mwh": valores,
        }
    )


# --------------------------------------------------------------------------- #
# 4.3 Demanda horaria
# --------------------------------------------------------------------------- #

def generar_demanda(anio: int, clave: str) -> pd.DataFrame:
    """Demanda horaria por region para un anio completo."""
    rng = _rng(clave)
    fechas, dia_anio, _ = _horas_del_anio(anio)
    n_dias = len(fechas)
    angulo = 2 * np.pi * dia_anio / n_dias

    # Mayor en invierno (maximo alrededor del 1 de julio en el hemisferio sur).
    estacional = 1 + 0.12 * np.cos(angulo - 2 * np.pi * 182 / n_dias)
    finde = np.isin(fechas.dayofweek.to_numpy(), [5, 6])
    laboral = np.where(finde, 0.92, 1.0)

    bloques = []
    for region in REGIONES:
        base = DEMANDA_BASE[region]
        ruido = rng.normal(1.0, 0.02, (n_dias, 24))
        matriz = (
            base
            * (estacional * laboral)[:, None]
            * PERFIL_DEMANDA[None, :]
            * ruido
        )
        bloques.append(np.round(matriz.reshape(-1), 2))

    valores = np.stack(bloques, axis=1).reshape(-1)  # orden: fecha, hora, region
    n_horas = n_dias * 24

    return pd.DataFrame(
        {
            "fecha": np.repeat(
                fechas.strftime("%Y-%m-%d").to_numpy(), 24 * len(REGIONES)
            ),
            "hora": np.tile(np.repeat(HORAS, len(REGIONES)), n_dias),
            "region": np.tile(np.array(REGIONES), n_horas),
            "mwh": valores,
        }
    )


# --------------------------------------------------------------------------- #
# 4.4 Demanda sucia
# --------------------------------------------------------------------------- #

VARIANTES_REGION = [
    lambda r: r.upper(),
    lambda r: r.lower(),
    lambda r: r + " ",
    lambda r: " " + r,
    lambda r: r.lower() + " ",
    lambda r: "  " + r.upper(),
]


def generar_demanda_sucia(demanda: pd.DataFrame) -> pd.DataFrame:
    """Version con defectos plantados de ``demanda.csv`` para el lab de limpieza."""
    rng = _rng("demanda_sucia")
    df = demanda.copy()
    n_filas = len(df)
    n_regiones = len(REGIONES)
    n_horas = n_filas // n_regiones

    # El orden es fecha, hora, region: la fila de la hora h para la region r
    # esta en la posicion h * n_regiones + r. Eso permite construir bloques
    # de horas contiguas dentro de una misma region.
    objetivo_nulos = int(round(n_filas * 0.03))
    posiciones_nulas: set[int] = set()
    while len(posiciones_nulas) < int(objetivo_nulos * 0.70):
        largo = int(rng.integers(2, 13))
        region = int(rng.integers(0, n_regiones))
        inicio = int(rng.integers(0, n_horas - largo))
        posiciones_nulas.update(
            (inicio + k) * n_regiones + region for k in range(largo)
        )
    while len(posiciones_nulas) < objetivo_nulos:
        posiciones_nulas.add(int(rng.integers(0, n_filas)))

    restantes = np.setdiff1d(np.arange(n_filas), np.fromiter(posiciones_nulas, int))
    sorteo = rng.permutation(restantes)
    idx_picos = np.sort(sorteo[:40])
    idx_negativos = np.sort(sorteo[40:55])

    mwh = df["mwh"].to_numpy(dtype=float).copy()
    mwh[idx_picos] = np.round(mwh[idx_picos] * 10.0, 2)
    mwh[idx_negativos] = np.round(
        -np.abs(mwh[idx_negativos]) * rng.uniform(0.1, 1.0, len(idx_negativos)), 2
    )
    idx_nulos = np.sort(np.fromiter(posiciones_nulas, int))

    # fecha como texto DD/MM/YYYY y mwh como texto con coma decimal.
    fecha_txt = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
    mwh_txt = np.array([f"{v:.2f}".replace(".", ",") for v in mwh], dtype=object)
    mwh_txt[idx_nulos] = ""

    region_txt = df["region"].to_numpy(dtype=object).copy()
    idx_region = rng.choice(n_filas, size=int(round(n_filas * 0.01)), replace=False)
    for pos in idx_region:
        variante = VARIANTES_REGION[int(rng.integers(0, len(VARIANTES_REGION)))]
        region_txt[pos] = variante(region_txt[pos])

    sucia = pd.DataFrame(
        {
            "fecha": fecha_txt.to_numpy(dtype=object),
            "hora": df["hora"].to_numpy(),
            "region": region_txt,
            "mwh": mwh_txt,
        }
    )

    # 20 filas duplicadas exactas, insertadas junto a su original.
    idx_dup = np.sort(rng.choice(n_filas, size=20, replace=False))
    orden = np.sort(np.concatenate([np.arange(n_filas), idx_dup]), kind="stable")
    return sucia.iloc[orden].reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 4.5 Base SQLite
# --------------------------------------------------------------------------- #

def escribir_sqlite(demanda: pd.DataFrame, ruta: Path) -> None:
    """Base SQLite con las tablas ``demanda`` y ``regiones``."""
    ruta.unlink(missing_ok=True)
    conexion = sqlite3.connect(ruta)
    try:
        conexion.execute("PRAGMA page_size = 4096")
        conexion.execute(
            "CREATE TABLE demanda ("
            "fecha TEXT NOT NULL, hora INTEGER NOT NULL, "
            "region TEXT NOT NULL, mwh REAL NOT NULL)"
        )
        conexion.execute(
            "CREATE TABLE regiones (region TEXT PRIMARY KEY, poblacion INTEGER NOT NULL)"
        )
        conexion.executemany(
            "INSERT INTO demanda VALUES (?, ?, ?, ?)",
            demanda.itertuples(index=False, name=None),
        )
        conexion.executemany(
            "INSERT INTO regiones VALUES (?, ?)",
            [(region, POBLACION[region]) for region in REGIONES],
        )
        conexion.commit()
        conexion.execute("VACUUM")
    finally:
        conexion.close()


# --------------------------------------------------------------------------- #
# 4.6 Bitacora de mantenimiento
# --------------------------------------------------------------------------- #

TIPOS_EVENTO = [
    "preventivo",
    "correctivo",
    "falla_electrica",
    "falla_mecanica",
    "evento_climatico",
    "inspeccion",
]

#: Duracion tipica por tipo de evento, en horas (minimo, maximo).
DURACION = {
    "preventivo": (4, 24),
    "correctivo": (6, 72),
    "falla_electrica": (2, 48),
    "falla_mecanica": (8, 96),
    "evento_climatico": (3, 36),
    "inspeccion": (1, 8),
}

#: Vocabulario propio de cada tipo de evento. Las observaciones se arman
#: combinando estas listas con plantillas, de modo que un LDA sobre el texto
#: encuentre topicos claramente separables por tipo.
VOCABULARIO = {
    "falla_electrica": {
        "componente": [
            "el transformador de poder", "el interruptor principal",
            "la barra de media tension", "el rele de proteccion",
            "el aislador de linea", "el alimentador de la subestacion",
            "el banco de condensadores", "el pararrayos del patio",
        ],
        "sintoma": [
            "sobretension sostenida", "un cortocircuito monofasico",
            "el disparo de la proteccion diferencial", "corriente de fuga elevada",
            "un arco electrico en el borne", "una caida brusca de tension",
        ],
        "accion": [
            "se aisla el circuito y se normaliza la tension",
            "se reemplaza el rele y se recalibra la proteccion",
            "se reconecta el interruptor tras verificar la aislacion",
            "se energiza la barra en forma escalonada",
        ],
    },
    "falla_mecanica": {
        "componente": [
            "el rodamiento del eje principal", "la turbina de baja presion",
            "la caja multiplicadora", "la bomba de lubricacion",
            "el acoplamiento del generador", "el sello mecanico",
            "el alabe del rotor", "el sistema de refrigeracion",
        ],
        "sintoma": [
            "vibracion excesiva en el eje", "desgaste anormal del rodamiento",
            "perdida de presion de aceite", "desalineamiento del acoplamiento",
            "fatiga del material en el alabe", "temperatura elevada en el descanso",
        ],
        "accion": [
            "se reemplaza el rodamiento y se realinea el eje",
            "se purga el circuito de lubricacion y se ajusta el torque",
            "se equilibra el rotor y se repite la medicion de vibracion",
            "se cambia el sello y se verifica la estanqueidad",
        ],
    },
    "evento_climatico": {
        "componente": [
            "el aerogenerador del sector norte", "la torre de medicion de viento",
            "la linea de evacuacion", "la estructura del parque",
            "el sistema de orientacion", "el anemometro de la gondola",
        ],
        "sintoma": [
            "rafagas de viento sobre el limite operativo",
            "acumulacion de hielo en las palas", "una tormenta electrica en la zona",
            "nevada intensa en el acceso", "granizo sobre la estructura",
            "lluvia y humedad extrema",
        ],
        "accion": [
            "se detiene la unidad por viento y se espera mejor tiempo",
            "se descongelan las palas antes de reanudar la operacion",
            "se despeja el acceso tras la nevada y se revisa la torre",
            "se inspecciona la estructura despues del frente de mal tiempo",
        ],
    },
    "preventivo": {
        "componente": [
            "el plan anual de la unidad", "la pauta de rutina trimestral",
            "el filtro de admision", "el circuito de aceite",
            "el calendario de disponibilidad", "el tablero de control",
        ],
        "sintoma": [
            "el cumplimiento del programa de mantenimiento",
            "el vencimiento de la pauta periodica",
            "las horas de operacion acumuladas", "el ciclo de limpieza programado",
        ],
        "accion": [
            "se ejecuta la rutina programada y se actualiza el calendario",
            "se cambia el aceite y el filtro segun la pauta del fabricante",
            "se ajusta el torque de los pernos y se limpia el tablero",
            "se repone la disponibilidad de la unidad dentro del plazo",
        ],
    },
    "correctivo": {
        "componente": [
            "el equipo intervenido en taller", "el repuesto critico de bodega",
            "la unidad fuera de servicio", "el conjunto reparado en terreno",
            "el modulo reemplazado", "la cuadrilla de intervencion",
        ],
        "sintoma": [
            "indisponibilidad forzada de la unidad", "una reparacion mayor pendiente",
            "la espera de un repuesto importado", "reincidencia de la falla anterior",
        ],
        "accion": [
            "se repara el conjunto y se realiza la puesta en marcha",
            "se instala el repuesto y se ejecutan las pruebas de normalizacion",
            "la cuadrilla interviene en terreno y devuelve la unidad al despacho",
            "se completa la reparacion dentro del plazo comprometido",
        ],
    },
    "inspeccion": {
        "componente": [
            "el registro fotografico de la unidad", "el informe de termografia",
            "el checklist del recorrido", "el parametro fuera de tolerancia",
            "la medicion de espesores", "la endoscopia del ducto",
        ],
        "sintoma": [
            "un hallazgo menor sin indisponibilidad", "una lectura dentro de tolerancia",
            "una observacion levantada en auditoria",
            "una desviacion leve del parametro medido",
        ],
        "accion": [
            "se documenta el hallazgo y se emite el informe correspondiente",
            "se registra la medicion en la ficha de la unidad",
            "se levanta la observacion y se programa el seguimiento",
            "se completa el checklist sin desviaciones relevantes",
        ],
    },
}

#: Plantillas de largo variable. El texto final queda entre 10 y 30 palabras
#: sin necesidad de truncarlo.
PLANTILLAS = [
    "Se registra {sintoma} en {componente} durante la ronda del turno.",
    "Se detecta {sintoma} en {componente}; {accion}.",
    "{sintoma_cap} en {componente}. {accion_cap}.",
    "El operador reporta {sintoma}; se revisa {componente} y {accion}.",
    "Evento por {sintoma} en {componente}; {accion}.",
    "{accion_cap} tras detectar {sintoma} en {componente}.",
    "Durante el turno: {sintoma} en {componente}; {accion}.",
]


def _observacion(tipo: str, rng: np.random.Generator) -> str:
    """Texto libre en espanol de 10 a 30 palabras, con vocabulario del tipo."""
    vocabulario = VOCABULARIO[tipo]
    elegir = lambda clave: vocabulario[clave][int(rng.integers(0, len(vocabulario[clave])))]
    sintoma, componente, accion = elegir("sintoma"), elegir("componente"), elegir("accion")
    plantilla = PLANTILLAS[int(rng.integers(0, len(PLANTILLAS)))]
    return plantilla.format(
        sintoma=sintoma,
        componente=componente,
        accion=accion,
        sintoma_cap=sintoma[0].upper() + sintoma[1:],
        accion_cap=accion[0].upper() + accion[1:],
    )


#: Peso relativo de cada tipo de evento base segun tecnologia.
PESOS_EVENTO = {
    "hidro": [0.34, 0.14, 0.12, 0.16, 0.02, 0.22],
    "solar": [0.38, 0.12, 0.16, 0.08, 0.02, 0.24],
    "eolica": [0.26, 0.12, 0.12, 0.20, 0.08, 0.22],
    "gas": [0.30, 0.18, 0.14, 0.18, 0.01, 0.19],
    "carbon": [0.28, 0.18, 0.14, 0.20, 0.01, 0.19],
    "diesel": [0.14, 0.52, 0.10, 0.12, 0.01, 0.11],
}

TOTAL_EVENTOS = 600


def generar_mantenimiento(anio: int, centrales: pd.DataFrame) -> pd.DataFrame:
    """Bitacora de eventos de mantenimiento con patrones descubribles."""
    rng = _rng("mantenimiento")
    fechas, _, _ = _horas_del_anio(anio)
    n_dias = len(fechas)
    mes = fechas.month.to_numpy()
    es_invierno = np.isin(mes, [5, 6, 7, 8])

    # Probabilidad diaria de evento climatico: concentrado en invierno.
    peso_clima = np.where(es_invierno, 4.0, 1.0)
    peso_clima = peso_clima / peso_clima.sum()

    eventos: list[tuple[str, int, str]] = []  # (central, indice de dia, tipo)

    for fila in centrales.itertuples():
        pesos = np.array(PESOS_EVENTO[fila.tecnologia], dtype=float)
        n_base = 22 if fila.tecnologia != "diesel" else 30
        tipos = rng.choice(TIPOS_EVENTO, size=n_base, p=pesos / pesos.sum())
        dias = rng.integers(0, n_dias, size=n_base)
        for tipo, dia in zip(tipos, dias):
            eventos.append((fila.central, int(dia), str(tipo)))

        # Los eventos climaticos se concentran en las eolicas y en invierno.
        n_clima = 12 if fila.tecnologia == "eolica" else 1
        for dia in rng.choice(n_dias, size=n_clima, replace=False, p=peso_clima):
            eventos.append((fila.central, int(dia), "evento_climatico"))

    # Las reglas se aplican sobre una muestra de tamano exacto (y no con una
    # moneda por evento) para que la proporcion observada en el archivo sea la
    # buscada y el lab 04 la pueda medir sin ruido de muestreo.
    def _muestra(indices: list[int], proporcion: float) -> np.ndarray:
        cantidad = int(round(len(indices) * proporcion))
        return rng.choice(np.array(indices), size=cantidad, replace=False)

    electricas = [i for i, e in enumerate(eventos) if e[2] == "falla_electrica"]
    climaticos = [i for i, e in enumerate(eventos) if e[2] == "evento_climatico"]

    derivados: list[tuple[str, int, str]] = []
    # 70% de las fallas electricas son seguidas de un correctivo en la misma
    # central dentro de los 3 dias siguientes.
    for i in sorted(_muestra(electricas, 0.70)):
        central, dia, _ = eventos[i]
        derivados.append(
            (central, min(dia + int(rng.integers(0, 4)), n_dias - 1), "correctivo")
        )
    # 50% de los eventos climaticos vienen con una falla mecanica el mismo dia.
    for i in sorted(_muestra(climaticos, 0.50)):
        central, dia, _ = eventos[i]
        derivados.append((central, dia, "falla_mecanica"))
    eventos.extend(derivados)

    # Relleno hasta el total objetivo con eventos programados.
    nombres = centrales["central"].to_numpy()
    while len(eventos) < TOTAL_EVENTOS:
        central = nombres[int(rng.integers(0, len(nombres)))]
        tipo = "preventivo" if rng.random() < 0.6 else "inspeccion"
        eventos.append((str(central), int(rng.integers(0, n_dias)), tipo))
    eventos = eventos[:TOTAL_EVENTOS]

    filas = []
    for central, dia, tipo in eventos:
        minimo, maximo = DURACION[tipo]
        filas.append(
            {
                "central": central,
                "fecha": fechas[dia].strftime("%Y-%m-%d"),
                "tipo_evento": tipo,
                "duracion_horas": int(rng.integers(minimo, maximo + 1)),
                "observacion": _observacion(tipo, rng),
            }
        )

    df = pd.DataFrame(filas)
    return df.sort_values(["fecha", "central"], kind="stable").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 4.7 API simulada de precios de nudo
# --------------------------------------------------------------------------- #

def generar_precios_nudo(demanda: pd.DataFrame, anio: int) -> dict:
    """Respuesta simulada de una API REST con los precios de nudo de enero."""
    rng = _rng("precios_nudo")
    enero = demanda[demanda["fecha"].str.startswith(f"{anio}-01")].reset_index(drop=True)

    # El precio sigue a la demanda del sistema y, en menor medida, a la de la region.
    total_hora = enero.groupby(["fecha", "hora"], sort=False)["mwh"].transform("sum")
    media_region = enero.groupby("region", sort=False)["mwh"].transform("mean")

    def normalizar(serie: pd.Series) -> np.ndarray:
        valores = serie.to_numpy(dtype=float)
        return (valores - valores.min()) / (valores.max() - valores.min())

    sistema = normalizar(total_hora)
    relativo = normalizar(enero["mwh"] / media_region)
    nivel = normalizar(enero["mwh"])
    precio = 40 + 125 * (0.40 * sistema + 0.30 * relativo + 0.30 * nivel)
    precio = np.clip(precio + rng.normal(0, 4.0, len(enero)), 40.0, 180.0)

    datos = [
        {
            "fecha": fecha,
            "hora": int(hora),
            "region": region,
            "precio_usd_mwh": round(float(valor), 2),
        }
        for fecha, hora, region, valor in zip(
            enero["fecha"], enero["hora"], enero["region"], precio
        )
    ]

    return {
        "metadata": {
            "fuente": "Observatorio de Datos Energeticos (ODE) - datos sinteticos",
            "fecha_consulta": f"{anio}-02-01T09:00:00-03:00",
            "unidad": "USD/MWh",
            "periodo": f"{anio}-01",
            "registros": len(datos),
        },
        "datos": datos,
    }


# --------------------------------------------------------------------------- #
# 5. Dataset grande (no versionado)
# --------------------------------------------------------------------------- #

def catalogo_grande(n_centrales: int = 200, semilla: int = SEMILLA + 800) -> pd.DataFrame:
    """Catalogo sintetico de ``n_centrales`` centrales para el dataset grande."""
    rng = np.random.default_rng(semilla)
    pesos = np.array([0.25, 0.25, 0.20, 0.15, 0.10, 0.05])
    rangos = {
        "hidro": (80, 500), "solar": (50, 250), "eolica": (50, 200),
        "gas": (100, 400), "carbon": (200, 500), "diesel": (20, 60),
    }
    tecnologias = rng.choice(TECNOLOGIAS, size=n_centrales, p=pesos)
    return pd.DataFrame(
        {
            "central": [f"Central Sintetica {i:03d}" for i in range(1, n_centrales + 1)],
            "tecnologia": tecnologias,
            "region": rng.choice(REGIONES, size=n_centrales),
            "potencia_mw": [
                int(rng.integers(*rangos[t])) for t in tecnologias
            ],
        }
    )


def generar_dataset_grande(
    ruta_salida: Path,
    anios: tuple[int, ...] = (2020, 2021, 2022, 2023, 2024),
    n_centrales: int = 200,
    semilla: int = SEMILLA + 800,
) -> Path:
    """Genera el CSV grande de generacion horaria (~9 millones de filas).

    Funcion aislada y sin efectos secundarios de modulo: el notebook del lab 01
    la importa para reproducir el archivo directamente en Colab.
    """
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.unlink(missing_ok=True)

    centrales = catalogo_grande(n_centrales, semilla)
    rng = np.random.default_rng(semilla)
    primero = True

    for anio in anios:
        fechas, dia_anio, _ = _horas_del_anio(anio)
        n_horas = len(fechas) * 24
        fecha_col = np.repeat(fechas.strftime("%Y-%m-%d").to_numpy(), 24)
        hora_col = np.tile(HORAS, len(fechas))

        for fila in centrales.itertuples():
            serie = _serie_central(fila.tecnologia, fila.potencia_mw, dia_anio, rng)
            trozo = pd.DataFrame(
                {
                    "fecha": fecha_col,
                    "hora": hora_col,
                    "central": np.repeat(fila.central, n_horas),
                    "mwh": serie,
                }
            )
            trozo.to_csv(
                ruta_salida,
                mode="w" if primero else "a",
                header=primero,
                index=False,
                encoding="utf-8",
                lineterminator="\n",
                float_format="%.2f",
            )
            primero = False

    return ruta_salida


# --------------------------------------------------------------------------- #
# Orquestacion
# --------------------------------------------------------------------------- #

def generar_todo() -> None:
    """Genera todos los datasets versionados de ``datos/``."""
    DIR_DATOS.mkdir(parents=True, exist_ok=True)
    DIR_API.mkdir(parents=True, exist_ok=True)

    centrales = construir_centrales()
    escribir_centrales(centrales)
    print("  centrales.csv / centrales.xlsx")

    generacion = generar_generacion(2024, centrales, "generacion_2024")
    _escribir_csv(generacion, DIR_DATOS / "generacion.csv", float_format="%.2f")
    print(f"  generacion.csv ({len(generacion):,} filas)")

    demanda = generar_demanda(2024, "demanda_2024")
    _escribir_csv(demanda, DIR_DATOS / "demanda.csv", float_format="%.2f")
    print(f"  demanda.csv ({len(demanda):,} filas)")

    sucia = generar_demanda_sucia(demanda)
    _escribir_csv(sucia, DIR_DATOS / "demanda_sucia.csv", sep=";")
    print(f"  demanda_sucia.csv ({len(sucia):,} filas)")

    escribir_sqlite(demanda, DIR_DATOS / "demanda.db")
    print("  demanda.db")

    mantenimiento = generar_mantenimiento(2024, centrales)
    _escribir_csv(mantenimiento, DIR_DATOS / "mantenimiento.csv")
    print(f"  mantenimiento.csv ({len(mantenimiento):,} filas)")

    precios = generar_precios_nudo(demanda, 2024)
    with open(DIR_API / "precios_nudo.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(precios, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"  api/precios_nudo.json ({len(precios['datos']):,} registros)")

    generacion_2025 = generar_generacion(2025, centrales, "generacion_2025")
    _escribir_csv(generacion_2025, DIR_DATOS / "generacion_2025.csv", float_format="%.2f")
    print(f"  generacion_2025.csv ({len(generacion_2025):,} filas)")

    demanda_2025 = generar_demanda(2025, "demanda_2025")
    _escribir_csv(demanda_2025, DIR_DATOS / "demanda_2025.csv", float_format="%.2f")
    print(f"  demanda_2025.csv ({len(demanda_2025):,} filas)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--grande",
        action="store_true",
        help="genera ademas datos/grande/generacion_grande.csv (no versionado)",
    )
    parser.add_argument(
        "--solo-grande",
        action="store_true",
        help="genera unicamente el dataset grande",
    )
    args = parser.parse_args()

    if not args.solo_grande:
        print("Generando datasets del curso...")
        generar_todo()

    if args.grande or args.solo_grande:
        print("Generando dataset grande (puede tardar varios minutos)...")
        ruta = generar_dataset_grande(DIR_GRANDE / "generacion_grande.csv")
        print(f"  {ruta.relative_to(RAIZ)}")

    print("Listo.")


if __name__ == "__main__":
    main()
