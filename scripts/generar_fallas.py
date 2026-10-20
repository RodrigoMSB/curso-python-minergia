#!/usr/bin/env python3
"""Genera la planilla de fallas eléctricas que usa el Paso 5 del Lab 04 guiado.

    python scripts/generar_fallas.py

Sale de datos/mantenimiento.csv y queda en datos/fallas_electricas.csv.

Tiene una fila por cada falla eléctrica de la bitácora, en el mismo orden, con la central,
la fecha y los días que pasaron hasta el primer correctivo de esa misma central, contando
desde el día de la falla. Un correctivo del mismo día cuenta como 0 días. Si la central no
tuvo ningún correctivo desde la falla hasta fin de año, la casilla queda vacía.

Necesita pandas.
"""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "datos"


def main():
    mant = pd.read_csv(DATOS / "mantenimiento.csv", parse_dates=["fecha"])
    fallas = mant[mant["tipo_evento"] == "falla_electrica"][["central", "fecha"]].reset_index(drop=True)
    correctivos = mant[mant["tipo_evento"] == "correctivo"][["central", "fecha"]]

    dias = []
    for falla in fallas.itertuples():
        despues = correctivos[(correctivos["central"] == falla.central) & (correctivos["fecha"] >= falla.fecha)]
        dias.append((despues["fecha"].min() - falla.fecha).days if len(despues) else None)
    fallas["dias_hasta_correctivo"] = pd.array(dias, dtype="Int64")
    fallas["fecha"] = fallas["fecha"].dt.strftime("%Y-%m-%d")

    assert len(fallas) == 47
    assert int((fallas["dias_hasta_correctivo"] <= 3).sum()) == 34
    assert int(fallas["dias_hasta_correctivo"].isna().sum()) == 4
    fallas.to_csv(DATOS / "fallas_electricas.csv", index=False)
    print("fallas_electricas.csv", len(fallas), "filas")


if __name__ == "__main__":
    main()
