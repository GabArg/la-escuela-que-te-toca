"""Prepara bases RA agregadas por departamento para su cruce con GeoRef.

No agrega indicadores ni construye un maestro educativo definitivo. Conserva
las métricas publicadas, normaliza encabezados y adjunta identificadores GeoRef
mediante coincidencia normalizada o una tabla puente explícita.
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data/raw/educacion_departamental"
PROCESSED_DIR = PROJECT_ROOT / "data/processed/educacion_departamental"
GEOREF_PATH = PROJECT_ROOT / "data/processed/territorios_argentina.parquet"
BRIDGE_PATH = PROJECT_ROOT / "data/dictionaries/puente_nombres_departamentos_2025.csv"
COVERAGE_PATH = PROJECT_ROOT / "data/dictionaries/cobertura_territorial_ra_2025.csv"
YEAR = 2025


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    filename: str
    source_url: str
    year: int = YEAR


DATASETS = {
    "matricula": DatasetSpec(
        key="matricula",
        filename="2025_matricula_agregada.csv",
        source_url="https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/IQDZWBqkmmvuSasr3wVDZIhwAduAVd1G1KpOSmI4mDbbV4E?e=CLjtl2",
    ),
    "trayectoria": DatasetSpec(
        key="trayectoria",
        filename="2025_trayectoria_agregada.csv",
        source_url="https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/IQDLGg-8IsrvQ7GjtoSuTg36AahBDzrs4gFKEDnNMjwAOUI?e=SiVssS",
    ),
    "caracteristicas": DatasetSpec(
        key="caracteristicas",
        filename="2025_caracteristicas_agregada.csv",
        source_url="https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/IQAR5DtMGXufQ4GWkxAbhQbWAaMz29BSWfoNPrvTA_ppkSo?e=vLzf4X",
    ),
}

REQUIRED_SOURCE_COLUMNS = ["provincia", "departamento", "sector", "ambito"]
PROVINCE_NAME_ALIASES = {
    "ciudad de buenos aires": "ciudad autonoma de buenos aires",
    "tierra del fuego": "tierra del fuego antartida e islas del atlantico sur",
}
UNIDENTIFIABLE_DEPARTMENT_LABELS = {"enmascarado", "sin datos"}


def normalize_text(value: object) -> str:
    """Normaliza un nombre para comparación, sin reemplazar el valor original."""
    ascii_value = unicodedata.normalize("NFKD", str(value)).encode(
        "ascii", "ignore"
    ).decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).strip()


def normalize_column_name(name: str) -> str:
    """Convierte encabezados a snake_case ASCII de forma determinística."""
    normalized = normalize_text(name).replace(" ", "_")
    if not normalized:
        raise ValueError(f"El encabezado no puede normalizarse: {name!r}")
    if normalized[0].isdigit():
        normalized = f"campo_{normalized}"
    return normalized


def load_raw_dataset(path: Path) -> pd.DataFrame:
    """Lee un CSV oficial separado por punto y coma y limpia blancos vacíos."""
    frame = pd.read_csv(path, sep=";", dtype="string", keep_default_na=True)
    normalized_columns = [normalize_column_name(column) for column in frame.columns]
    if len(set(normalized_columns)) != len(normalized_columns):
        raise ValueError(f"La normalización genera encabezados duplicados en {path}")
    frame.columns = normalized_columns
    missing = set(REQUIRED_SOURCE_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en {path}: {sorted(missing)}")
    return frame.apply(lambda column: column.str.strip().replace("", pd.NA))


def load_georef(path: Path = GEOREF_PATH) -> pd.DataFrame:
    columns = [
        "provincia_id",
        "provincia_nombre",
        "departamento_id",
        "departamento_nombre",
        "clave_territorial",
    ]
    georef = pd.read_parquet(path, columns=columns).astype("string")
    georef["provincia_clave_nombre"] = georef["provincia_nombre"].map(normalize_text)
    georef["departamento_clave_nombre"] = georef["departamento_nombre"].map(
        normalize_text
    )
    return georef


def load_bridge(path: Path = BRIDGE_PATH) -> pd.DataFrame:
    bridge = pd.read_csv(path, dtype="string")
    bridge["provincia_clave_fuente"] = bridge["provincia_fuente"].map(normalize_text)
    bridge["departamento_clave_fuente"] = bridge["departamento_fuente"].map(
        normalize_text
    )
    if bridge.duplicated(
        ["provincia_clave_fuente", "departamento_clave_fuente"]
    ).any():
        raise ValueError("La tabla puente contiene claves fuente duplicadas.")
    valid_statuses = {"confirmado", "pendiente"}
    if not set(bridge["estado"]).issubset(valid_statuses):
        raise ValueError("La tabla puente contiene estados no permitidos.")
    return bridge


def attach_georef_ids(
    frame: pd.DataFrame,
    georef: pd.DataFrame,
    bridge: pd.DataFrame,
) -> pd.DataFrame:
    """Asigna IDs por nombre normalizado y después por tabla puente documentada."""
    result = frame.copy()
    result["provincia_nombre_fuente"] = result.pop("provincia")
    result["departamento_nombre_fuente"] = result.pop("departamento")
    result["provincia_clave_fuente"] = result["provincia_nombre_fuente"].map(
        normalize_text
    ).replace(PROVINCE_NAME_ALIASES)
    result["departamento_clave_fuente"] = result[
        "departamento_nombre_fuente"
    ].map(normalize_text)

    georef_keys = georef.rename(
        columns={
            "provincia_clave_nombre": "provincia_clave_fuente",
            "departamento_clave_nombre": "departamento_clave_fuente",
        }
    )
    result = result.merge(
        georef_keys,
        on=["provincia_clave_fuente", "departamento_clave_fuente"],
        how="left",
        validate="many_to_one",
    )
    result["match_metodo"] = pd.Series(pd.NA, index=result.index, dtype="string")
    result.loc[result["departamento_id"].notna(), "match_metodo"] = (
        "nombre_normalizado"
    )

    bridge_lookup = bridge.loc[bridge["estado"].eq("confirmado"),
        [
            "provincia_clave_fuente",
            "departamento_clave_fuente",
            "provincia_id",
            "departamento_id",
        ]
    ].rename(
        columns={
            "provincia_id": "provincia_id_puente",
            "departamento_id": "departamento_id_puente",
        }
    )
    result = result.merge(
        bridge_lookup,
        on=["provincia_clave_fuente", "departamento_clave_fuente"],
        how="left",
        validate="many_to_one",
    )
    bridge_mask = result["departamento_id"].isna() & result[
        "departamento_id_puente"
    ].notna()
    result.loc[bridge_mask, "provincia_id"] = result.loc[
        bridge_mask, "provincia_id_puente"
    ]
    result.loc[bridge_mask, "departamento_id"] = result.loc[
        bridge_mask, "departamento_id_puente"
    ]
    result.loc[bridge_mask, "match_metodo"] = "tabla_puente_documentada"
    result = result.drop(columns=["provincia_id_puente", "departamento_id_puente"])

    pending_lookup = bridge.loc[
        bridge["estado"].eq("pendiente"),
        ["provincia_clave_fuente", "departamento_clave_fuente"],
    ].copy()
    pending_lookup["puente_pendiente"] = True
    result = result.merge(
        pending_lookup,
        on=["provincia_clave_fuente", "departamento_clave_fuente"],
        how="left",
        validate="many_to_one",
    )
    pending_mask = result["puente_pendiente"].notna()
    result.loc[pending_mask, "match_metodo"] = "puente_pendiente"
    result = result.drop(columns="puente_pendiente")

    # Completa nombres y clave oficiales para filas resueltas mediante el puente.
    official = georef[
        [
            "provincia_id",
            "provincia_nombre",
            "departamento_id",
            "departamento_nombre",
            "clave_territorial",
        ]
    ].rename(
        columns={
            "provincia_nombre": "provincia_nombre_oficial",
            "departamento_nombre": "departamento_nombre_oficial",
            "clave_territorial": "clave_territorial_oficial",
        }
    )
    result = result.merge(
        official,
        on=["provincia_id", "departamento_id"],
        how="left",
        validate="many_to_one",
    )
    for target, source in (
        ("provincia_nombre", "provincia_nombre_oficial"),
        ("departamento_nombre", "departamento_nombre_oficial"),
        ("clave_territorial", "clave_territorial_oficial"),
    ):
        result[target] = result[target].fillna(result[source])
    result = result.drop(
        columns=[
            "provincia_nombre_oficial",
            "departamento_nombre_oficial",
            "clave_territorial_oficial",
        ]
    )

    unidentified = result["departamento_id"].isna()
    allowed_special_label = result["departamento_clave_fuente"].isin(
        UNIDENTIFIABLE_DEPARTMENT_LABELS
    )
    allowed_unidentified = allowed_special_label | pending_mask
    if (unidentified & ~allowed_unidentified).any():
        values = result.loc[
            unidentified & ~allowed_unidentified,
            ["provincia_nombre_fuente", "departamento_nombre_fuente"],
        ].drop_duplicates()
        raise ValueError(f"Quedan territorios no documentados:\n{values.to_string(index=False)}")
    result.loc[unidentified & allowed_special_label, "match_metodo"] = (
        "no_identificable_en_fuente"
    )
    return result


def prepare_dataset(
    spec: DatasetSpec,
    raw_dir: Path = RAW_DIR,
    georef_path: Path = GEOREF_PATH,
    bridge_path: Path = BRIDGE_PATH,
) -> pd.DataFrame:
    """Prepara una base anual y valida grano, año y correspondencia territorial."""
    if spec.year != YEAR:
        raise ValueError(f"Año no habilitado para esta integración: {spec.year}")
    frame = load_raw_dataset(raw_dir / spec.filename)
    grain = REQUIRED_SOURCE_COLUMNS
    if frame.duplicated(grain).any():
        raise ValueError(f"Hay duplicados inesperados en el grano de {spec.key}.")

    metric_columns = [column for column in frame.columns if column not in grain]
    for column in metric_columns:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        if (frame[column].notna() & numeric.isna()).any():
            raise ValueError(f"La métrica {column} contiene valores no numéricos.")
        frame[column] = numeric.astype("Int64")

    result = attach_georef_ids(frame, load_georef(georef_path), load_bridge(bridge_path))
    result.insert(0, "anio", spec.year)
    result.insert(0, "dataset", spec.key)
    result.insert(2, "url_origen", spec.source_url)
    result.insert(3, "fecha_descarga", "2026-09-12")
    return result


def validate_prepared_dataset(frame: pd.DataFrame, expected_dataset: str) -> None:
    required = {
        "dataset",
        "anio",
        "url_origen",
        "fecha_descarga",
        "provincia_nombre_fuente",
        "departamento_nombre_fuente",
        "sector",
        "ambito",
        "provincia_id",
        "departamento_id",
        "clave_territorial",
        "match_metodo",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas preparadas: {sorted(missing)}")
    if set(frame["dataset"]) != {expected_dataset} or set(frame["anio"]) != {YEAR}:
        raise ValueError("Dataset o año inconsistente.")
    identifiable = ~frame["match_metodo"].isin(
        ["no_identificable_en_fuente", "puente_pendiente"]
    )
    if frame.loc[
        identifiable, ["provincia_id", "departamento_id", "clave_territorial"]
    ].isna().any().any():
        raise ValueError("Hay IDs nulos en territorios que deberían ser identificables.")
    grain = [
        "dataset",
        "anio",
        "provincia_nombre_fuente",
        "departamento_nombre_fuente",
        "sector",
        "ambito",
    ]
    if frame.duplicated(grain).any():
        raise ValueError("Hay duplicados inesperados en el grano preparado.")


def run_pipeline(output_dir: Path = PROCESSED_DIR) -> dict[str, pd.DataFrame]:
    """Genera salidas intermedias separadas; no crea un maestro definitivo."""
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for key, spec in DATASETS.items():
        frame = prepare_dataset(spec)
        validate_prepared_dataset(frame, key)
        frame.to_parquet(output_dir / f"{key}_{spec.year}.parquet", index=False)
        outputs[key] = frame
    coverage = build_coverage_table(outputs, load_georef(), load_bridge())
    COVERAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(COVERAGE_PATH, index=False)
    return outputs


def build_coverage_table(
    outputs: dict[str, pd.DataFrame],
    georef: pd.DataFrame,
    bridge: pd.DataFrame,
) -> pd.DataFrame:
    """Construye una matriz de cobertura sin imputar valores educativos."""
    coverage = georef[
        ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre"]
    ].copy()
    pending_ids = set(
        bridge.loc[bridge["estado"].eq("pendiente"), "departamento_id"]
    )
    for dataset, frame in outputs.items():
        direct_ids = set(
            frame.loc[frame["match_metodo"].eq("nombre_normalizado"), "departamento_id"]
            .dropna()
        )
        bridge_ids = set(
            frame.loc[
                frame["match_metodo"].eq("tabla_puente_documentada"),
                "departamento_id",
            ].dropna()
        )
        column = f"{dataset}_estado"
        coverage[column] = "no_representado"
        coverage.loc[coverage["departamento_id"].isin(direct_ids), column] = "directo"
        coverage.loc[coverage["departamento_id"].isin(bridge_ids), column] = "puente"
        coverage.loc[coverage["departamento_id"].isin(pending_ids), column] = (
            "por_verificar"
        )

    state_columns = [f"{dataset}_estado" for dataset in DATASETS]
    coverage["tipo_match"] = coverage[state_columns].apply(
        lambda row: row.iloc[0] if row.nunique() == 1 else "por_verificar", axis=1
    )
    coverage["observaciones"] = coverage["tipo_match"].map(
        {
            "directo": "Nombre RA correspondiente por normalización determinística.",
            "puente": "Equivalencia explícita confirmada en la tabla puente.",
            "por_verificar": "Variante nominal sin evidencia oficial suficiente; no se asigna ID en los datos preparados.",
            "no_representado": "Sin registro identificable; no equivale a valor cero.",
        }
    )
    ordered = [
        "provincia_id",
        "provincia_nombre",
        "departamento_id",
        "departamento_nombre",
        "matricula_estado",
        "trayectoria_estado",
        "caracteristicas_estado",
        "tipo_match",
        "observaciones",
    ]
    return coverage.loc[:, ordered]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROCESSED_DIR)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    prepared = run_pipeline(arguments.output_dir)
    for dataset, frame in prepared.items():
        matched = frame.loc[frame["departamento_id"].notna(), "departamento_id"].nunique()
        print(f"{dataset}: {len(frame)} filas; {matched} territorios con match GeoRef")
