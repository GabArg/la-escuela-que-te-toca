"""Construccion y analisis reproducible de la base departamental RA 2025.

Las funciones conservan los faltantes, excluyen del nivel departamental las
filas sin identificador y recalculan proporciones desde sus numeradores y
denominadores. Ninguna proporcion publicada aqui es una tasa oficial: el
nombre explicita siempre el cociente utilizado.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data/processed/educacion_departamental"
OUTPUT_PATH = PROJECT_ROOT / "data/processed/ra_2025_analitico.parquet"
COVERAGE_PATH = PROJECT_ROOT / "data/dictionaries/cobertura_territorial_ra_2025.csv"
VARIABLES_PATH = PROJECT_ROOT / "data/dictionaries/variables_ra_2025.csv"

KEYS = ["departamento_id", "sector", "ambito"]
GRADES = [str(i) for i in range(1, 13)] + ["1314", "20"]
ENROLMENT_COMPONENTS = (
    ["lactantes", "deambulantes"]
    + [f"s{i}" for i in range(2, 6)]
    + [f"campo_{g}" for g in GRADES]
    + ["snu"]
)
COMPARABLE_ENROLMENT = [f"campo_{g}" for g in GRADES]
REPEATERS = [f"r_{g}" for g in GRADES]
OVERAGE = [f"s_{g}" for g in GRADES if g != "20"]
TRAJECTORY_PREFIXES = [
    "inicial", "entrados", "scp", "ssp", "ultimo", "promovidos",
    "promovidos_ex", "promovidos_mas_2mat", "nopromo", "regulares", "otros",
]


def _row_sum(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Suma conteos disponibles sin transformar una fila totalmente nula en cero."""
    available = [column for column in columns if column in frame]
    if not available:
        return pd.Series(pd.NA, index=frame.index, dtype="Float64")
    return frame[available].sum(axis=1, min_count=1).astype("Float64")


def _ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator.div(denominator.where(denominator.gt(0)))
    return result.replace([np.inf, -np.inf], np.nan).astype("Float64")


def _identified(frame: pd.DataFrame) -> pd.DataFrame:
    """Retiene solo unidades identificables; Enmascarado/Sin datos quedan fuera."""
    return frame.loc[frame["departamento_id"].notna()].copy()


def prepare_matricula(frame: pd.DataFrame) -> pd.DataFrame:
    frame = _identified(frame)
    result = frame[KEYS + ["provincia_id", "provincia_nombre", "departamento_nombre"]].copy()
    result["matricula_total"] = _row_sum(frame, ENROLMENT_COMPONENTS)
    result["matricula_grados_comparables"] = _row_sum(frame, COMPARABLE_ENROLMENT)
    result["repetidores_total"] = _row_sum(frame, REPEATERS)
    result["sobreedad_total"] = _row_sum(frame, OVERAGE)
    result["proporcion_repetidores_sobre_matricula"] = _ratio(
        result["repetidores_total"], result["matricula_grados_comparables"]
    )
    result["proporcion_sobreedad_sobre_matricula"] = _ratio(
        result["sobreedad_total"], result["matricula_grados_comparables"]
    )
    return result


def prepare_trayectoria(frame: pd.DataFrame) -> pd.DataFrame:
    frame = _identified(frame)
    result = frame[KEYS].copy()
    for prefix in TRAJECTORY_PREFIXES:
        result[f"trayectoria_{prefix}_total"] = _row_sum(
            frame, [f"{prefix}_{grade}" for grade in GRADES]
        )
    result["primaria_egresados"] = frame["primaria_egresados"].astype("Float64")
    result["secundaria_egresados"] = frame["secundaria_egresados"].astype("Float64")
    result["proporcion_promovidos_sobre_ultimo"] = _ratio(
        result["trayectoria_promovidos_total"], result["trayectoria_ultimo_total"]
    )
    result["proporcion_no_promovidos_sobre_ultimo"] = _ratio(
        result["trayectoria_nopromo_total"], result["trayectoria_ultimo_total"]
    )
    result["proporcion_salidos_sin_pase_sobre_inicial"] = _ratio(
        result["trayectoria_ssp_total"], result["trayectoria_inicial_total"]
    )
    return result


def prepare_caracteristicas(frame: pd.DataFrame) -> pd.DataFrame:
    frame = _identified(frame)
    result = frame[KEYS].copy()
    result["localizaciones"] = frame["localizacion"].astype("Float64")
    return result


def build_analytical_table(input_dir: Path = INPUT_DIR) -> pd.DataFrame:
    """Une las tres fuentes en su grano departamento-sector-ambito."""
    matricula = prepare_matricula(pd.read_parquet(input_dir / "matricula_2025.parquet"))
    trayectoria = prepare_trayectoria(pd.read_parquet(input_dir / "trayectoria_2025.parquet"))
    caracteristicas = prepare_caracteristicas(
        pd.read_parquet(input_dir / "caracteristicas_2025.parquet")
    )
    result = matricula.merge(trayectoria, on=KEYS, how="outer", validate="one_to_one")
    result = result.merge(caracteristicas, on=KEYS, how="outer", validate="one_to_one")
    result.insert(0, "anio", 2025)
    result["cobertura_matricula"] = result["matricula_total"].notna()
    result["cobertura_trayectoria"] = result["trayectoria_inicial_total"].notna()
    result["cobertura_caracteristicas"] = result["localizaciones"].notna()
    return result.sort_values(KEYS, kind="stable").reset_index(drop=True)


COUNT_COLUMNS = [
    "matricula_total", "matricula_grados_comparables", "repetidores_total",
    "sobreedad_total", "localizaciones", "primaria_egresados",
    "secundaria_egresados",
] + [f"trayectoria_{prefix}_total" for prefix in TRAJECTORY_PREFIXES]


def aggregate_departments(analytical: pd.DataFrame) -> pd.DataFrame:
    """Agrega conteos y recalcula cocientes; nunca suma ni promedia tasas."""
    identity = ["departamento_id", "provincia_id", "provincia_nombre", "departamento_nombre"]
    available = [column for column in COUNT_COLUMNS if column in analytical]
    grouped = analytical.groupby(identity, observed=True, dropna=False)[available].sum(min_count=1).reset_index()
    grouped["proporcion_repetidores_sobre_matricula"] = _ratio(
        grouped["repetidores_total"], grouped["matricula_grados_comparables"]
    )
    grouped["proporcion_sobreedad_sobre_matricula"] = _ratio(
        grouped["sobreedad_total"], grouped["matricula_grados_comparables"]
    )
    grouped["proporcion_promovidos_sobre_ultimo"] = _ratio(
        grouped["trayectoria_promovidos_total"], grouped["trayectoria_ultimo_total"]
    )
    grouped["proporcion_no_promovidos_sobre_ultimo"] = _ratio(
        grouped["trayectoria_nopromo_total"], grouped["trayectoria_ultimo_total"]
    )
    grouped["proporcion_salidos_sin_pase_sobre_inicial"] = _ratio(
        grouped["trayectoria_ssp_total"], grouped["trayectoria_inicial_total"]
    )
    return grouped


def add_structural_shares(analytical: pd.DataFrame, departments: pd.DataFrame) -> pd.DataFrame:
    """Calcula composicion rural y estatal desde conteos observados."""
    rural = analytical.loc[analytical["ambito"].str.casefold().eq("rural")].groupby(
        "departamento_id")["matricula_total"].sum(min_count=1)
    estatal = analytical.loc[analytical["sector"].str.casefold().eq("estatal")].groupby(
        "departamento_id")["matricula_total"].sum(min_count=1)
    result = departments.copy()
    result["proporcion_matricula_rural"] = _ratio(
        result["departamento_id"].map(rural), result["matricula_total"]
    )
    result["proporcion_matricula_estatal"] = _ratio(
        result["departamento_id"].map(estatal), result["matricula_total"]
    )
    return result


def validate_analytical_table(frame: pd.DataFrame) -> None:
    if frame[KEYS].isna().any().any():
        raise ValueError("La tabla analitica contiene claves territoriales nulas.")
    if frame.duplicated(KEYS).any():
        raise ValueError("La tabla analitica contiene duplicados en su grano.")
    if not set(frame["anio"]) == {2025}:
        raise ValueError("La tabla contiene anos diferentes de 2025.")
    rate_columns = [column for column in frame if column.startswith("proporcion_")]
    for column in rate_columns:
        observed = frame[column].dropna()
        if not observed.between(0, 1).all():
            raise ValueError(f"El cociente {column} esta fuera de [0, 1].")


def write_analytical_table(output_path: Path = OUTPUT_PATH) -> pd.DataFrame:
    frame = build_analytical_table()
    validate_analytical_table(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(output_path, index=False)
    return frame


def _variable_metadata(dataset: str, variable: str) -> dict[str, str]:
    """Clasifica el esquema sin adjudicar definiciones no documentadas."""
    keys = {
        "dataset": "Nombre interno de la base", "anio": "Ano del relevamiento",
        "url_origen": "URL de origen", "fecha_descarga": "Fecha de descarga",
        "sector": "Sector de gestion", "ambito": "Ambito urbano o rural",
        "provincia_nombre_fuente": "Provincia informada por la fuente",
        "departamento_nombre_fuente": "Departamento informado por la fuente",
        "provincia_clave_fuente": "Nombre normalizado para correspondencia",
        "departamento_clave_fuente": "Nombre normalizado para correspondencia",
        "provincia_id": "Identificador GeoRef de provincia",
        "provincia_nombre": "Nombre oficial GeoRef de provincia",
        "departamento_id": "Identificador nacional GeoRef de departamento o equivalente",
        "departamento_nombre": "Nombre GeoRef de departamento o equivalente",
        "clave_territorial": "Clave interna provincia-departamento",
        "match_metodo": "Metodo documentado de correspondencia territorial",
    }
    description = keys.get(variable, "definicion por verificar")
    unit = "no aplica" if variable in keys else "definicion por verificar"
    kind = "no aplica" if variable in keys else "definicion por verificar"
    dimension = "Trazabilidad" if variable in keys else "por verificar"
    level = "no aplica"
    notes = "No usar sustantivamente hasta confirmar la definicion oficial."

    if dataset == "matricula":
        if variable in ENROLMENT_COMPONENTS:
            description = "Matricula total en la categoria indicada por el nombre del campo"
            unit, kind, dimension = "estudiantes", "aditiva", "Acceso"
            notes = "Conteo agregado; la correspondencia exacta categoria-nivel debe consultarse en el diccionario oficial."
        elif variable.startswith("v_"):
            description = "Matricula de varones en la categoria indicada"
            unit, kind, dimension = "estudiantes", "aditiva", "Acceso; Equidad"
        elif variable in REPEATERS:
            description = "Estudiantes repitentes en el ano/categoria indicada"
            unit, kind, dimension = "estudiantes", "aditiva", "Permanencia; Trayectoria"
        elif variable in OVERAGE:
            description = "Estudiantes con sobreedad en el ano/categoria indicada"
            unit, kind, dimension = "estudiantes", "aditiva", "Trayectoria; Equidad"
        elif variable.startswith(("sec", "multi_")):
            description = "Secciones en la categoria indicada"
            unit, kind, dimension = "secciones", "aditiva", "Acceso"
    elif dataset == "trayectoria":
        base = variable[2:] if variable.startswith("m_") else variable
        labels = {
            "inicial_": "Matricula inicial", "entrados_": "Entrados durante el ano",
            "scp_": "Salidos con pase", "ssp_": "Salidos sin pase",
            "ultimo_": "Matricula al ultimo dia de clase",
            "promovidos_mas_2mat_": "Promovidos con mas de dos materias",
            "promovidos_ex_": "Promovidos en examen", "promovidos_": "Promovidos",
            "nopromo_": "No promovidos", "regulares_": "Regulares",
            "otros_": "Otros",
        }
        for prefix, label in labels.items():
            if base.startswith(prefix):
                description = ("Mujeres: " if variable.startswith("m_") else "") + label + " en el ano/categoria indicada"
                unit, kind, dimension = "estudiantes", "aditiva", "Permanencia; Trayectoria"
                break
        if variable in {"primaria_egresados", "primaria_m_egresados", "secundaria_egresados", "secundaria_m_egresados"}:
            description = "Egresados de " + ("primaria" if "primaria" in variable else "secundaria") + (", mujeres" if "_m_" in variable else "")
            unit, kind, dimension = "estudiantes", "aditiva", "Trayectoria"
    elif dataset == "caracteristicas" and variable == "localizacion":
        description = "Cantidad de localizaciones educativas"
        unit, kind, dimension = "localizaciones", "aditiva", "Acceso; Equidad"
    if description != "definicion por verificar" and variable not in keys:
        notes = "Definicion basada en el diccionario oficial RA 2025; conservar el grano sector-ambito."
    return {
        "descripcion": description, "unidad": unit, "aditiva_o_tasa": kind,
        "nivel_educativo": level, "sector": "desagregada por sector",
        "ambito": "desagregada por ambito", "posible_dimension_proyecto": dimension,
        "observaciones_metodologicas": notes,
    }


def write_variable_inventory(path: Path = VARIABLES_PATH) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for dataset in ("matricula", "trayectoria", "caracteristicas"):
        frame = pd.read_parquet(INPUT_DIR / f"{dataset}_2025.parquet")
        for variable, dtype in frame.dtypes.items():
            rows.append({"variable": variable, "dataset": dataset, "tipo": str(dtype), **_variable_metadata(dataset, variable)})
    inventory = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(path, index=False, encoding="utf-8")
    return inventory


if __name__ == "__main__":
    written = write_analytical_table()
    inventory = write_variable_inventory()
    print(f"Filas: {len(written)} | departamentos: {written.departamento_id.nunique()}")
    print(f"Variables inventariadas: {len(inventory)}")
    print(f"Salida: {OUTPUT_PATH}")
