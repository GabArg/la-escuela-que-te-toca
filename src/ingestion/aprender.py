"""Pipeline reproducible para Aprender Secundaria 2024 agregado.

Los archivos oficiales publican conteos ponderados por departamento, sector y
ambito. Este modulo conserva esos conteos y calcula porcentajes solo despues de
agregar las cuatro categorias de desempeno en un mismo grano territorial.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

from src.ingestion.educacion_departamental import (
    attach_georef_ids,
    load_bridge,
    load_georef,
    normalize_column_name,
)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw/aprender"
OUTPUT = ROOT / "data/processed/aprender_analitico.parquet"
AREAS = {
    "Lengua": ("2024_secundaria_lengua_agregada.csv", "ldesemp"),
    "Matematica": ("2024_secundaria_matematica_agregada.csv", "mdesemp"),
}
LEVELS = {
    "por_debajo_del_nivel_basico": "por_debajo_del_basico",
    "basico": "basico",
    "satisfactorio": "satisfactorio",
    "avanzado": "avanzado",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype("string").str.strip().replace("", pd.NA).str.replace(",", ".", regex=False), errors="coerce")


def load_area(area: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    filename, prefix = AREAS[area]
    frame = pd.read_csv(raw_dir / filename, sep=";", dtype="string", encoding="utf-8-sig")
    frame.columns = [normalize_column_name(c) for c in frame.columns]
    frame = frame.rename(columns={"jurisdiccion": "provincia"})
    required = {"provincia", "departamento", "sector", "ambito"}
    performance = {f"{prefix}_{source}": target for source, target in LEVELS.items()}
    missing = required.union(performance).difference(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas oficiales requeridas: {sorted(missing)}")
    result = frame[[*required, *performance]].rename(columns=performance)
    for column in LEVELS.values():
        result[column] = _numeric(result[column])
    result["area"] = area
    result["anio"] = 2024
    result["nivel"] = "Secundaria"
    result["grado"] = "ultimo_ano_5_6"
    result["ponderado"] = True
    return result


def prepare_area(area: str) -> pd.DataFrame:
    frame = load_area(area)
    matched = attach_georef_ids(frame, load_georef(), load_bridge())
    special = matched["departamento_id"].isna()
    allowed_unmatched = matched.loc[special, "match_metodo"].isin(
        ["no_identificable_en_fuente", "puente_pendiente"]
    )
    if not allowed_unmatched.all():
        raise ValueError("Hay filas sin ID que no estan documentadas.")
    id_columns = ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre"]
    values = list(LEVELS.values())
    identifiable = matched.loc[~special].copy()
    grouped = identifiable.groupby(id_columns, observed=True, dropna=False)[values].sum(min_count=1).reset_index()
    grouped["desempeno_completo"] = grouped[values].notna().all(axis=1)
    long = grouped.melt(id_vars=id_columns, value_vars=values, var_name="indicador", value_name="conteo_ponderado")
    denominator = long.groupby(id_columns, observed=True)["conteo_ponderado"].transform("sum")
    complete = long[id_columns].merge(grouped[id_columns + ["desempeno_completo"]], on=id_columns, how="left")["desempeno_completo"]
    long["valor"] = long["conteo_ponderado"].div(denominator).mul(100).where(denominator.gt(0) & complete)
    long = long.assign(anio=2024, nivel="Secundaria", grado="ultimo_ano_5_6", area=area,
                       n_estudiantes=pd.NA, n_escuelas=pd.NA, ponderado=True,
                       nivel_comparabilidad="corte_transversal")
    long["estado_cobertura"] = complete.map({True: "completo", False: "parcial"})
    return long[["anio", "nivel", "grado", "area", *id_columns, "indicador", "valor",
                 "conteo_ponderado", "n_estudiantes", "n_escuelas", "ponderado",
                 "nivel_comparabilidad", "estado_cobertura"]]


def build(output: Path = OUTPUT) -> pd.DataFrame:
    result = pd.concat([prepare_area(area) for area in AREAS], ignore_index=True)
    grain = ["anio", "area", "departamento_id", "indicador"]
    if result.duplicated(grain).any():
        raise ValueError("Duplicados inesperados en el grano analitico.")
    if not result["valor"].dropna().between(0, 100).all():
        raise ValueError("Porcentajes fuera de rango.")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output, index=False)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = build(args.output)
    print(f"filas={len(data)} territorios={data.departamento_id.nunique()} areas={data.area.nunique()}")
