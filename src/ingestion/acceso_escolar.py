"""Integra matrícula RA 2022 por edad con población residente Censo 2022.

El cociente resultante no es una tasa oficial de escolarización: matrícula se
asigna por localización educativa y población por residencia habitual.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.ingestion.educacion_departamental import normalize_column_name, normalize_text
from src.ingestion.ra_historico import attach_territory, load_bridge, load_georef


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw/acceso_escolar"
CENSUS_DIR = RAW_DIR / "indec_censo2022"
OUTPUT_PATH = ROOT / "data/processed/acceso_escolar.parquet"
YEAR = 2022
AGE_GROUPS = {"4-5": (4, 5), "6-11": (6, 11), "12-14": (12, 14), "15-17": (15, 17)}
PROVINCES = {
    "caba": "Ciudad Autónoma de Buenos Aires", "bsas": "Buenos Aires",
    "catamarca": "Catamarca", "chaco": "Chaco", "chubut": "Chubut",
    "cordoba": "Córdoba", "corrientes": "Corrientes", "entrerios": "Entre Ríos",
    "formosa": "Formosa", "jujuy": "Jujuy", "lapampa": "La Pampa",
    "larioja": "La Rioja", "mendoza": "Mendoza", "misiones": "Misiones",
    "neuquen": "Neuquén", "rionegro": "Río Negro", "salta": "Salta",
    "sanjuan": "San Juan", "sanluis": "San Luis", "santacruz": "Santa Cruz",
    "santafe": "Santa Fe", "santiago": "Santiago del Estero",
    "tdf": "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
    "tucuman": "Tucumán",
}


def load_ra_age(path: Path = RAW_DIR / "2022_matricula_edad.csv") -> pd.DataFrame:
    frame = pd.read_csv(path, sep=";", dtype="string", keep_default_na=True)
    frame.columns = [normalize_column_name(column) for column in frame]
    frame = frame.apply(lambda column: column.str.strip().replace("", pd.NA))
    return attach_territory(frame, YEAR, load_georef(), load_bridge())


def transform_ra_age(frame: pd.DataFrame) -> pd.DataFrame:
    pieces = []
    identity = ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "tipo_match"]
    for label, (start, end) in AGE_GROUPS.items():
        columns = [f"campo_{age}anos" for age in range(start, end + 1)]
        values = frame[columns].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
        piece = frame[identity].copy()
        piece["grupo_edad"] = label
        piece["matricula"] = values.astype("Float64")
        pieces.append(piece)
    long = pd.concat(pieces, ignore_index=True)
    keys = identity[:4] + ["grupo_edad"]
    # Solo las unidades identificadas pueden agregarse territorialmente.
    identified = long.loc[long["departamento_id"].notna()]
    return identified.groupby(keys, dropna=False, observed=True)["matricula"].sum(min_count=1).reset_index()


def _province_from_filename(path: Path) -> str:
    match = re.match(r"c2022_([^_]+)_est_c4", path.name)
    if not match or match.group(1) not in PROVINCES:
        raise ValueError(f"Jurisdicción no reconocida en {path.name}")
    return PROVINCES[match.group(1)]


def load_census_age(census_dir: Path = CENSUS_DIR) -> pd.DataFrame:
    rows = []
    files = sorted(census_dir.glob("c2022_*_est_c4_*.xlsx"))
    if len(files) != 24:
        raise ValueError(f"Se esperaban 24 cuadros jurisdiccionales y se hallaron {len(files)}")
    for path in files:
        province = _province_from_filename(path)
        workbook = pd.ExcelFile(path)
        # Las dos primeras hojas son carátula/índice y la tercera es total provincial.
        for sheet in workbook.sheet_names[3:]:
            raw = pd.read_excel(path, sheet_name=sheet, header=None)
            title = str(raw.iloc[1, 0])
            match = re.search(r",\s*(?:departamento|partido|Comuna)\s+(.+?)\.\s*Total", title, flags=re.I)
            if not match:
                raise ValueError(f"No se pudo extraer la unidad territorial: {title}")
            department = match.group(1).strip()
            if province == "Ciudad Autónoma de Buenos Aires":
                department = f"Comuna {department}"
            for age, population in raw.iloc[:, :2].itertuples(index=False, name=None):
                age_text = str(age).strip()
                if age_text.isdigit() and 4 <= int(age_text) <= 17:
                    rows.append({"provincia_fuente": province, "departamento_fuente": department,
                                 "edad": int(age_text), "poblacion": pd.to_numeric(population, errors="coerce")})
    return pd.DataFrame(rows)


def match_census_to_georef(frame: pd.DataFrame) -> pd.DataFrame:
    georef = load_georef()
    result = frame.copy()
    result["provincia_key"] = result["provincia_fuente"].map(normalize_text)
    result["departamento_key"] = result["departamento_fuente"].map(normalize_text)
    lookup = georef[["provincia_key", "departamento_key", "provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre"]]
    result = result.merge(lookup, on=["provincia_key", "departamento_key"], how="left", validate="many_to_one")
    result["tipo_match_poblacion"] = result["departamento_id"].notna().map({True: "directo", False: "por_verificar"})
    return result


def aggregate_census_groups(frame: pd.DataFrame) -> pd.DataFrame:
    matched = match_census_to_georef(frame)
    matched["grupo_edad"] = pd.cut(matched["edad"], bins=[3, 5, 11, 14, 17], labels=list(AGE_GROUPS), ordered=True)
    keys = ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "grupo_edad"]
    identified = matched.loc[matched["departamento_id"].notna()]
    return identified.groupby(keys, observed=True)["poblacion"].sum(min_count=1).reset_index()


def build_access_dataset() -> pd.DataFrame:
    enrollment = transform_ra_age(load_ra_age())
    population = aggregate_census_groups(load_census_age())
    keys = ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "grupo_edad"]
    result = population.merge(enrollment, on=keys, how="outer", validate="one_to_one", indicator=True)
    result.insert(0, "anio", YEAR)
    result["cobertura_dato"] = result.pop("_merge").map({"both": "poblacion_y_matricula", "left_only": "solo_poblacion", "right_only": "solo_matricula"}).astype("string")
    denominator = result["poblacion"].where(result["poblacion"].gt(0))
    result["indicador_acceso"] = result["matricula"].div(denominator).astype("Float64")
    result["indicador_fuera_rango"] = result["indicador_acceso"].gt(1)
    result["tipo_indicador"] = "cociente exploratorio matrícula RA / población residente Censo 2022"
    result["observaciones"] = "No es tasa oficial de escolarización; matrícula por localización y población por residencia."
    return result.sort_values(["provincia_id", "departamento_id", "grupo_edad"]).reset_index(drop=True)


def validate_access(frame: pd.DataFrame) -> None:
    if set(frame["anio"]) != {YEAR}:
        raise ValueError("Año inesperado")
    if not set(frame["grupo_edad"].astype(str)).issubset(AGE_GROUPS):
        raise ValueError("Grupo de edad inválido")
    if (frame[["poblacion", "matricula"]].dropna() < 0).any().any():
        raise ValueError("Conteos negativos")
    if frame.duplicated(["anio", "departamento_id", "grupo_edad"]).any():
        raise ValueError("Duplicados en el grano analítico")
    zero = frame["poblacion"].eq(0)
    if frame.loc[zero, "indicador_acceso"].notna().any():
        raise ValueError("División por cero")


def write_access(path: Path = OUTPUT_PATH) -> pd.DataFrame:
    frame = build_access_dataset()
    validate_access(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


if __name__ == "__main__":
    output = write_access()
    print(output["cobertura_dato"].value_counts().to_string())
    print(f"Territorios: {output.departamento_id.nunique()} | filas: {len(output)}")
