#!/usr/bin/env python3
"""Genera los archivos de datos/ con la misma lógica y la misma semilla que los notebooks.

Cada notebook del curso arma sus datos adentro, en la celda plegada Datos del curso,
así que funciona en Colab sin descargar nada. Este script es esa misma celda, copiada
tal cual, y deja los archivos en datos/ para quien quiera trabajar fuera de Colab.

    python scripts/generar_datos.py

El cuerpo de generar_todo() es la celda de datos del Lab 07, que es la más completa y
arma 2024 y 2025. generar_demanda_sucia() es el agregado de la celda del Lab 03.
scripts/verificar_datos.py comprueba que los archivos sean idénticos a los que
producen los notebooks. Si se cambia la celda de datos, se cambia también acá.

Necesita pandas, numpy y openpyxl.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd
import json
import sqlite3

DATOS = Path(__file__).resolve().parents[1] / "datos"

ARCHIVOS = ["centrales.csv", "centrales.xlsx", "generacion.csv", "demanda.csv", "demanda.db",
            "precios_nudo.json", "mantenimiento.csv", "demanda_sucia.csv",
            "centrales_2025.csv", "generacion_2025.csv", "mantenimiento_2025.csv",
            "demanda_2025.csv", "lecturas_2025.csv"]


def generar_todo():
    rng = np.random.default_rng(2026)
    centrales = pd.DataFrame([
     ("Central Río Manso Alto","hidro","Biobío",420,2004),("Central Salto Verde","hidro","Los Lagos",310,1998),
     ("Central Aguas Claras","hidro","Biobío",180,2011),("Central Vega Azul","hidro","Los Lagos",95,2016),
     ("Central Tres Saltos","hidro","Biobío",260,1995),
     ("Parque Solar Pampa Alta","solar","Antofagasta",230,2019),("Parque Solar Llano Seco","solar","Atacama",180,2020),
     ("Parque Solar Sol Naciente","solar","Antofagasta",145,2021),("Parque Solar Quebrada Honda","solar","Atacama",95,2022),
     ("Parque Solar Altiplano","solar","Antofagasta",310,2023),
     ("Eólica Cerro Negro","eolica","Coquimbo",160,2017),("Eólica Punta Ventosa","eolica","Coquimbo",120,2018),
     ("Eólica Loma Fría","eolica","Valparaíso",85,2020),("Eólica Campo Abierto","eolica","Coquimbo",200,2021),
     ("Termoeléctrica Bahía Norte","gas","Valparaíso",375,2008),("Termoeléctrica Puerto Sur","gas","Biobío",290,2012),
     ("Termoeléctrica Valle Central","gas","Metropolitana",210,2006),
     ("Carboeléctrica Costa Brava","carbon","Biobío",480,2001),("Carboeléctrica Roca Gris","carbon","Antofagasta",350,1999),
     ("Diésel Respaldo Cordillera","diesel","Metropolitana",45,2014),
    ], columns=["central","tecnologia","region","potencia_mw","anio_inicio"])
    fechas = pd.date_range("2024-01-01","2024-12-31",freq="D")
    perfil = np.array([0,0,0,0,0,0,.05,.18,.38,.58,.75,.87,.93,.9,.8,.63,.42,.2,.05,0,0,0,0,0])
    filas=[]
    for _,c in centrales.iterrows():
        p,t = c.potencia_mw, c.tecnologia
        for f in fechas:
            est = 1+0.25*np.cos(2*np.pi*(f.dayofyear-15)/365)
            if t=="solar": base = p*perfil*0.30*est*rng.uniform(.8,1.1)
            elif t=="eolica": base = p*0.36*rng.uniform(.15,1.6,24)
            elif t=="hidro": base = p*0.55*(2-est)*rng.uniform(.9,1.1,24)
            elif t=="gas": base = p*0.68*rng.uniform(.9,1.05,24)
            elif t=="carbon": base = p*0.65*rng.uniform(.95,1.02,24)
            else:
                base = np.zeros(24); base[18:23] = p*0.55*rng.uniform(.8,1,5)
            filas.append(pd.DataFrame({"fecha":f.strftime("%Y-%m-%d"),"hora":range(24),
                                       "central":c.central,"mwh":np.clip(base,0,p).round(2)}))
    centrales.to_csv("centrales.csv", index=False)
    pd.concat(filas, ignore_index=True).to_csv("generacion.csv", index=False)

    # Excel con dos hojas, la segunda con notas en texto libre
    with pd.ExcelWriter("centrales.xlsx") as w:
        centrales.to_excel(w, sheet_name="centrales", index=False)
        pd.DataFrame({"nota":["Potencias declaradas al 31 de diciembre de 2024",
                              "Las centrales de pasada se informan con su potencia máxima"]}
                     ).to_excel(w, sheet_name="notas", index=False)

    # Demanda por región, base de datos SQLite
    regs = ["Antofagasta","Atacama","Coquimbo","Valparaíso","Metropolitana","Biobío","Los Lagos"]
    pobl = [700000,320000,850000,1900000,8100000,1700000,900000]
    perfil_d = np.array([.72,.68,.66,.65,.66,.70,.78,.88,.95,.98,1.0,1.02,1.03,1.0,.97,.96,.97,1.0,1.06,1.10,1.08,.98,.88,.79])
    dem=[]
    for r,p in zip(regs,pobl):
        base_r = p/8000
        for f in fechas:
            inv = 1+0.18*np.cos(2*np.pi*(f.dayofyear-190)/365)
            finde = 0.92 if f.dayofweek>=5 else 1.0
            v = base_r*perfil_d*inv*finde*rng.uniform(.97,1.03,24)
            dem.append(pd.DataFrame({"fecha":f.strftime("%Y-%m-%d"),"hora":range(24),
                                     "region":r,"mwh":v.round(2)}))
    demanda = pd.concat(dem, ignore_index=True)
    demanda.to_csv("demanda.csv", index=False)
    con = sqlite3.connect("demanda.db")
    demanda.to_sql("demanda", con, index=False, if_exists="replace")
    pd.DataFrame({"region":regs,"poblacion":pobl}).to_sql("regiones", con, index=False, if_exists="replace")
    con.close()

    # Precios de nudo de enero, como los entregaría una API REST
    ene = demanda[demanda["fecha"].str.startswith("2024-01")]
    pr = ene.assign(precio_usd_mwh=(40 + ene["mwh"]/ene["mwh"].max()*110
                                    + rng.normal(0,6,len(ene))).clip(40,180).round(2))
    with open("precios_nudo.json","w") as f:
        json.dump({"metadata":{"fuente":"Observatorio de Datos Energéticos",
                               "fecha_consulta":"2024-02-01","unidad":"USD por MWh"},
                   "datos": pr[["fecha","hora","region","precio_usd_mwh"]].to_dict("records")},
                  f)

    # Se ordena por el nombre sin tildes, así el sorteo de más abajo cae siempre
    # sobre las mismas filas.
    _sin_tilde = lambda s: (s.str.normalize("NFKD").str.encode("ascii", "ignore")
                            .str.decode("ascii") if s.name == "central" else s)

    # ------------------------------------------------ bitácora de mantenimiento
    # Seiscientos eventos del año, con dos patrones plantados a propósito que el
    # lab va a tener que encontrar y medir.
    rngm = np.random.default_rng(404)
    TIPOS = ["preventivo","correctivo","falla_electrica","falla_mecanica",
             "evento_climatico","inspeccion"]
    PESOS = {"hidro":[.34,.14,.12,.16,.02,.22], "solar":[.38,.12,.16,.08,.02,.24],
             "eolica":[.26,.12,.12,.20,.08,.22], "gas":[.30,.18,.14,.18,.01,.19],
             "carbon":[.28,.18,.14,.20,.01,.19], "diesel":[.14,.52,.10,.12,.01,.11]}
    DURA = {"preventivo":(4,24), "correctivo":(6,72), "falla_electrica":(2,48),
            "falla_mecanica":(8,96), "evento_climatico":(3,36), "inspeccion":(1,8)}
    n_dias = len(fechas)
    invierno = np.isin(fechas.month.to_numpy(), [5,6,7,8])
    peso_clima = np.where(invierno, 4.0, 1.0); peso_clima /= peso_clima.sum()

    ev = []
    for _,c in centrales.iterrows():
        p = np.array(PESOS[c.tecnologia]); p = p/p.sum()
        n = 30 if c.tecnologia=="diesel" else 22
        for tipo, d in zip(rngm.choice(TIPOS, size=n, p=p), rngm.integers(0, n_dias, size=n)):
            ev.append([c.central, int(d), str(tipo)])
        n_cl = 12 if c.tecnologia=="eolica" else 1
        for d in rngm.choice(n_dias, size=n_cl, replace=False, p=peso_clima):
            ev.append([c.central, int(d), "evento_climatico"])

    # Patrón 1, el 70 por ciento de las fallas eléctricas arrastra un correctivo
    # en la misma central dentro de los tres días siguientes.
    elec = [i for i,e in enumerate(ev) if e[2]=="falla_electrica"]
    for i in sorted(rngm.choice(elec, size=int(round(len(elec)*0.70)), replace=False)):
        ev.append([ev[i][0], min(ev[i][1] + int(rngm.integers(0,4)), n_dias-1), "correctivo"])
    # Patrón 2, la mitad de los eventos climáticos trae una falla mecánica el mismo día.
    clim = [i for i,e in enumerate(ev) if e[2]=="evento_climatico"]
    for i in sorted(rngm.choice(clim, size=int(round(len(clim)*0.50)), replace=False)):
        ev.append([ev[i][0], ev[i][1], "falla_mecanica"])

    nombres = centrales["central"].to_numpy()
    while len(ev) < 600:
        ev.append([str(nombres[int(rngm.integers(0,len(nombres)))]),
                   int(rngm.integers(0,n_dias)),
                   "preventivo" if rngm.random()<0.6 else "inspeccion"])
    ev = ev[:600]

    mant = pd.DataFrame([{"central":c, "fecha":fechas[d].strftime("%Y-%m-%d"),
                          "tipo_evento":t,
                          "duracion_horas":int(rngm.integers(DURA[t][0], DURA[t][1]+1))}
                         for c,d,t in ev])

    # ------------------------------------------- texto libre de cada evento
    # Una observación escrita como la escribiría el turno, con vocabulario
    # propio de cada tipo. El Módulo 5 busca temas ahí adentro.
    VOCAB = {
     "falla_electrica": (["el transformador de poder","el interruptor principal",
        "la barra de media tensión","el relé de protección","el aislador de línea"],
        ["sobretensión sostenida","un cortocircuito monofásico","corriente de fuga elevada",
         "el disparo de la protección diferencial"],
        ["se aísla el circuito y se normaliza la tensión","se reemplaza el relé y se recalibra",
         "se reconecta el interruptor tras verificar la aislación"]),
     "falla_mecanica": (["el rodamiento del eje","la caja multiplicadora","el acoplamiento",
        "el sello del descanso","la bomba de lubricación"],
        ["vibración fuera de norma","temperatura elevada en el descanso","ruido anormal",
         "pérdida de aceite"],
        ["se reemplaza el rodamiento y se alinea el eje","se rellena y se purga el circuito de aceite",
         "se ajusta el acoplamiento y se mide la vibración"]),
     "evento_climatico": (["la línea de evacuación","el patio de alta tensión",
        "el camino de acceso","la estructura de la torre","el pararrayos del patio"],
        ["viento sobre lo previsto","una descarga atmosférica cercana","acumulación de nieve",
         "lluvia intensa con anegamiento"],
        ["se inspecciona la estructura y se despeja la faja","se repone el servicio al amainar",
         "se drena el sector y se revisa la puesta a tierra"]),
     "preventivo": (["el sistema de refrigeración","los filtros de aire","el tablero de control",
        "las conexiones de fuerza","el grupo hidráulico"],
        ["la mantención programada","el cambio de filtros","el ajuste de rutina",
         "la lubricación periódica"],
        ["se cambian filtros y se registra la lectura","se reaprietan las conexiones y se sella",
         "se completa la pauta sin observaciones"]),
     "correctivo": (["el equipo afectado","la unidad detenida","el componente dañado",
        "la sección fuera de servicio","el módulo de potencia"],
        ["la reparación de la falla del turno anterior","el levantamiento de la indisponibilidad",
         "la orden de trabajo pendiente","la intervención de emergencia"],
        ["se repara y se devuelve a servicio","se reemplaza la pieza y se prueba en vacío",
         "se normaliza y se informa al despacho"]),
     "inspeccion": (["el conjunto de medida","la señalética del área","los niveles de aceite",
        "el estado de los accesos","el registro de alarmas"],
        ["la ronda de rutina","la verificación visual","la lectura de instrumentos",
         "el chequeo de seguridad"],
        ["se deja constancia sin hallazgos","se anota una observación menor",
         "se programa revisión de detalle"]),
    }
    PLANT = ["Se registra {s} sobre {c}.",
             "Se detecta {s} en {c}, {a}.",
             "El operador reporta {s}, se revisa {c} y {a}.",
             "Evento por {s} en {c}, {a}."]
    def _obs(t):
        c, s, a = (VOCAB[t][k][int(rngm.integers(0, len(VOCAB[t][k])))] for k in (0, 1, 2))
        return PLANT[int(rngm.integers(0, len(PLANT)))].format(s=s, c=c, a=a)
    mant["observacion"] = [_obs(t) for t in mant["tipo_evento"]]

    # ---------------------------------------------------- el año 2025
    # El archivo nuevo de la evaluación. Tiene tres cosas adentro que el
    # participante va a tener que encontrar, y además llega con defectos de
    # formato porque viene de otra fuente.
    rng25 = np.random.default_rng(2025)
    fechas25 = pd.date_range("2025-01-01", "2025-12-31", freq="D")

    # 1. La demanda crece, pero no parejo. La Metropolitana crece poco y
    #    Antofagasta mucho, porque entró un consumo minero nuevo.
    CRECE = {"Metropolitana": 1.012, "Antofagasta": 1.094, "Atacama": 1.031,
             "Coquimbo": 1.025, "Valparaíso": 1.018, "Biobío": 1.021,
             "Los Lagos": 1.016}
    dem25 = []
    for r, p in zip(regs, pobl):
        base_r = p / 8000 * CRECE[r]
        for f in fechas25:
            inv = 1 + 0.18 * np.cos(2 * np.pi * (f.dayofyear - 190) / 365)
            finde = 0.92 if f.dayofweek >= 5 else 1.0
            v = base_r * perfil_d * inv * finde * rng25.uniform(.97, 1.03, 24)
            dem25.append(pd.DataFrame({"fecha": f.strftime("%Y-%m-%d"), "hora": range(24),
                                       "region": r, "mwh": v.round(2)}))
    demanda25 = pd.concat(dem25, ignore_index=True)

    # 2. La generación. Dos cosas cambian. El año fue seco, así que la hidro
    #    baja, y entró en servicio un parque solar nuevo a mitad de año.
    nueva = pd.DataFrame([("Parque Solar Río Seco", "solar", "Atacama", 260, 2025)],
                         columns=["central", "tecnologia", "region", "potencia_mw", "anio_inicio"])
    centrales25 = pd.concat([centrales, nueva], ignore_index=True)
    filas25 = []
    for _, c in centrales25.iterrows():
        p, t = c.potencia_mw, c.tecnologia
        for f in fechas25:
            if c.central == "Parque Solar Río Seco" and f < pd.Timestamp("2025-07-01"):
                base = np.zeros(24)                       # todavía no entraba en servicio
            else:
                est = 1 + 0.25 * np.cos(2 * np.pi * (f.dayofyear - 15) / 365)
                if t == "solar":    base = p * perfil * 0.30 * est * rng25.uniform(.8, 1.1)
                elif t == "eolica": base = p * 0.36 * rng25.uniform(.15, 1.6, 24)
                elif t == "hidro":  base = p * 0.55 * (2 - est) * rng25.uniform(.9, 1.1, 24) * 0.68
                elif t == "gas":    base = p * 0.68 * rng25.uniform(.9, 1.05, 24) * 1.12
                elif t == "carbon": base = p * 0.65 * rng25.uniform(.95, 1.02, 24)
                else:
                    base = np.zeros(24); base[18:23] = p * 0.55 * rng25.uniform(.8, 1, 5)
            filas25.append(pd.DataFrame({"fecha": f.strftime("%Y-%m-%d"), "hora": range(24),
                                         "central": c.central, "mwh": np.clip(base, 0, p).round(2)}))
    generacion25 = pd.concat(filas25, ignore_index=True)

    # 3. La bitácora del año, con una central que concentra fallas.
    ev25 = []
    n_dias25 = len(fechas25)
    for _, c in centrales25.iterrows():
        p = np.array(PESOS[c.tecnologia]); p = p / p.sum()
        n = 30 if c.tecnologia == "diesel" else 22
        if c.central == "Termoeléctrica Puerto Sur":
            n = 64                                        # la central con problemas
            p = np.array([.10, .30, .24, .24, .02, .10]); p = p / p.sum()
        for tipo, d in zip(rng25.choice(TIPOS, size=n, p=p),
                           rng25.integers(0, n_dias25, size=n)):
            ev25.append([c.central, int(d), str(tipo)])
    mant25 = pd.DataFrame([{"central": c, "fecha": fechas25[d].strftime("%Y-%m-%d"),
                            "tipo_evento": t,
                            "duracion_horas": int(rng25.integers(DURA[t][0], DURA[t][1] + 1))}
                           for c, d, t in ev25])

    # El archivo llega con defectos de formato, porque viene de otra fuente.
    centrales25.to_csv("centrales_2025.csv", index=False)
    generacion25.to_csv("generacion_2025.csv", index=False)
    mant25.sort_values(["fecha", "central"], kind="stable", key=_sin_tilde).reset_index(drop=True) \
          .to_csv("mantenimiento_2025.csv", index=False)
    d25 = demanda25.copy()
    d25["fecha"] = pd.to_datetime(d25["fecha"]).dt.strftime("%d/%m/%Y")
    d25["mwh"] = d25["mwh"].map(lambda v: f"{v:.2f}".replace(".", ","))
    rr = rng25.choice(len(d25), size=int(len(d25) * 0.012), replace=False)
    d25.loc[rr, "region"] = d25.loc[rr, "region"].str.upper()
    d25.to_csv("demanda_2025.csv", sep=";", index=False)
    # 4. Las lecturas del medidor de cuatro centrales, que llegan de otra fuente
    #    y traen lo que trae cualquier archivo de terreno. Huecos y un imposible.
    vigiladas = ["Central Río Manso Alto", "Termoeléctrica Puerto Sur",
                 "Parque Solar Pampa Alta", "Eólica Cerro Negro"]
    lec = generacion25[generacion25["central"].isin(vigiladas)].copy()
    lec = lec.merge(centrales25[["central", "potencia_mw"]], on="central")
    lec = lec.rename(columns={"mwh": "lectura_mwh"})
    lec = lec.sort_values(["central", "fecha", "hora"], kind="stable",
                      key=_sin_tilde).reset_index(drop=True)

    # Huecos sueltos, el 2 por ciento, como cuando el medidor no reporta una hora.
    sueltos = rng25.choice(len(lec), size=int(len(lec) * 0.02), replace=False)
    lec.loc[sueltos, "lectura_mwh"] = np.nan

    # Y un corte largo, doce horas seguidas de una sola central.
    corte = lec[(lec["central"] == "Eólica Cerro Negro")
                & (lec["fecha"] == "2025-03-14") & (lec["hora"] < 12)].index
    lec.loc[corte, "lectura_mwh"] = np.nan

    # El valor imposible. Una central no puede entregar más que su potencia.
    imposible = lec[(lec["central"] == "Central Río Manso Alto")
                    & (lec["fecha"] == "2025-09-02") & (lec["hora"] == 14)].index
    lec.loc[imposible, "lectura_mwh"] = 9999.0

    lec[["central", "fecha", "hora", "lectura_mwh", "potencia_mw"]] \
        .to_csv("lecturas_2025.csv", index=False)

    mant.sort_values(["fecha","central"], kind="stable", key=_sin_tilde).reset_index(drop=True) \
        .to_csv("mantenimiento.csv", index=False)


def generar_demanda_sucia():
    # ---------------------------------------------------------------- demanda sucia
    # La misma demanda, estropeada a propósito con siete defectos, que es el archivo
    # con el que trabaja este lab. Se genera con semilla fija, así que es siempre igual.
    if not os.path.exists("demanda_sucia.csv"):
        base = pd.read_csv("demanda.csv")
        rng = np.random.default_rng(303)
        n, regs_n = len(base), base["region"].nunique()
        n_horas = n // regs_n

        # 1. bloques de horas sin dato, más algunos sueltos, cerca del 3 por ciento
        nulos = set()
        while len(nulos) < int(n * 0.021):
            largo, reg = int(rng.integers(2, 13)), int(rng.integers(0, regs_n))
            ini = int(rng.integers(0, n_horas - largo))
            nulos.update((ini + k) * regs_n + reg for k in range(largo))
        while len(nulos) < int(n * 0.03):
            nulos.add(int(rng.integers(0, n)))
        idx_nulos = np.sort(np.fromiter(nulos, int))

        # 2. picos imposibles y valores negativos
        resto = rng.permutation(np.setdiff1d(np.arange(n), idx_nulos))
        picos, negativos = np.sort(resto[:40]), np.sort(resto[40:55])
        mwh = base["mwh"].to_numpy(float).copy()
        mwh[picos] = np.round(mwh[picos] * 10, 2)
        mwh[negativos] = np.round(-np.abs(mwh[negativos]) * rng.uniform(.1, 1, len(negativos)), 2)

        # 3. fecha en formato chileno y número con coma decimal, los dos como texto
        fecha_txt = pd.to_datetime(base["fecha"]).dt.strftime("%d/%m/%Y")
        mwh_txt = np.array([f"{v:.2f}".replace(".", ",") for v in mwh], dtype=object)
        mwh_txt[idx_nulos] = ""

        # 4. la región escrita de varias formas
        VARIANTES = [str.upper, str.lower, lambda r: r + " ", lambda r: " " + r,
                     lambda r: r.lower() + " ", lambda r: "  " + r.upper()]
        region_txt = base["region"].to_numpy(dtype=object).copy()
        for pos in rng.choice(n, size=int(n * 0.01), replace=False):
            region_txt[pos] = VARIANTES[int(rng.integers(0, len(VARIANTES)))](region_txt[pos])

        suc = pd.DataFrame({"fecha": fecha_txt.to_numpy(dtype=object), "hora": base["hora"].to_numpy(),
                            "region": region_txt, "mwh": mwh_txt})

        # 5. veinte filas duplicadas exactas, pegadas a su original
        dup = np.sort(rng.choice(n, size=20, replace=False))
        orden = np.sort(np.concatenate([np.arange(n), dup]), kind="stable")
        # 6. separador punto y coma, como lo guarda Excel en Chile
        suc.iloc[orden].to_csv("demanda_sucia.csv", sep=";", index=False)


def main():
    DATOS.mkdir(exist_ok=True)
    os.chdir(DATOS)
    # Se parte de cero, así ningún archivo viejo queda sin regenerar.
    for nombre in ARCHIVOS:
        if os.path.exists(nombre):
            os.remove(nombre)
    generar_todo()
    generar_demanda_sucia()
    for nombre in ARCHIVOS:
        print(f"{nombre:24} {os.path.getsize(nombre) / 1024:9.0f} KB")


if __name__ == "__main__":
    main()
