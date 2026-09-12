"""Ingestión reproducible de provincias y departamentos desde GeoRef Argentina.

Los archivos de ``data/raw`` se leen sin modificarlos. La salida tabular conserva
los identificadores oficiales como texto y la salida geoespacial conserva las
geometrías originales, sin simplificación.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROVINCES_PATH = PROJECT_ROOT / "data/raw/georef/provincias.json"
DEFAULT_DEPARTMENTS_PATH = PROJECT_ROOT / "data/raw/georef/departamentos.geojson"
DEFAULT_PARQUET_PATH = PROJECT_ROOT / "data/processed/territorios_argentina.parquet"
DEFAULT_GEOJSON_PATH = PROJECT_ROOT / "data/processed/departamentos_argentina.geojson"
PROVINCES_URL = "https://apis.datos.gob.ar/georef/api/provincias.json"
DEPARTMENTS_URL = "https://apis.datos.gob.ar/georef/api/departamentos.geojson"

OUTPUT_COLUMNS = [
    "provincia_id",
    "provincia_nombre",
    "departamento_id",
    "departamento_nombre",
    "clave_territorial",
]


def download_file_without_overwrite(url: str, destination: Path) -> None:
    """Descarga bytes oficiales de forma atómica y nunca sobrescribe un raw."""
    if destination.exists():
        raise FileExistsError(f"El archivo raw ya existe y no se sobrescribirá: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp"
    )
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "la-escuela-que-te-toca/0.1 (datos abiertos)",
                "Accept": "application/json, application/geo+json",
            },
        )
        with os.fdopen(descriptor, "wb") as temporary, urlopen(request) as response:
            shutil.copyfileobj(response, temporary)
        os.replace(temporary_name, destination)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def download_sources(
    provinces_path: Path = DEFAULT_PROVINCES_PATH,
    departments_path: Path = DEFAULT_DEPARTMENTS_PATH,
) -> None:
    """Descarga los dos recursos oficiales necesarios, sin modificar raw previos."""
    existing = [path for path in (provinces_path, departments_path) if path.exists()]
    if existing:
        paths = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Hay archivos raw existentes; no se sobrescribirán: {paths}")
    download_file_without_overwrite(PROVINCES_URL, provinces_path)
    download_file_without_overwrite(DEPARTMENTS_URL, departments_path)


def _read_json(path: Path) -> dict[str, Any]:
    """Lee un archivo JSON sin alterarlo y valida que la raíz sea un objeto."""
    with path.open(encoding="utf-8") as source:
        payload = json.load(source)
    if not isinstance(payload, dict):
        raise ValueError(f"Se esperaba un objeto JSON en {path}")
    return payload


def load_provinces(path: Path = DEFAULT_PROVINCES_PATH) -> pd.DataFrame:
    """Carga provincias y normaliza los campos oficiales ``id`` y ``nombre``."""
    payload = _read_json(path)
    records = payload.get("provincias")
    if not isinstance(records, list):
        raise ValueError("El JSON de provincias no contiene una lista 'provincias'.")

    provinces = pd.DataFrame(records)
    required = {"id", "nombre"}
    missing = required.difference(provinces.columns)
    if missing:
        raise ValueError(f"Faltan campos de provincias: {sorted(missing)}")

    return provinces.loc[:, ["id", "nombre"]].rename(
        columns={"id": "provincia_id", "nombre": "provincia_nombre"}
    ).astype({"provincia_id": "string", "provincia_nombre": "string"})


def load_department_features(
    path: Path = DEFAULT_DEPARTMENTS_PATH,
) -> list[dict[str, Any]]:
    """Carga las entidades GeoJSON de departamentos sin cambiar geometrías."""
    payload = _read_json(path)
    if payload.get("type") != "FeatureCollection":
        raise ValueError("El archivo de departamentos no es un FeatureCollection.")
    features = payload.get("features")
    if not isinstance(features, list):
        raise ValueError("El GeoJSON de departamentos no contiene 'features'.")
    return features


def build_territorial_dataframe(
    provinces: pd.DataFrame,
    department_features: list[dict[str, Any]],
) -> pd.DataFrame:
    """Construye la tabla maestra y ejecuta validaciones de integridad."""
    records: list[dict[str, Any]] = []
    for feature in department_features:
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise ValueError("Un departamento no contiene propiedades válidas.")
        province = properties.get("provincia")
        if not isinstance(province, dict):
            raise ValueError("Un departamento no contiene una provincia asociada.")
        records.append(
            {
                "provincia_id": province.get("id"),
                "departamento_id": properties.get("id"),
                "departamento_nombre": properties.get("nombre"),
            }
        )

    departments = pd.DataFrame(records).astype(
        {
            "provincia_id": "string",
            "departamento_id": "string",
            "departamento_nombre": "string",
        }
    )
    territories = departments.merge(
        provinces,
        on="provincia_id",
        how="left",
        validate="many_to_one",
    )
    territories["clave_territorial"] = (
        territories["provincia_id"] + "-" + territories["departamento_id"]
    )
    territories = territories.loc[:, OUTPUT_COLUMNS].sort_values(
        ["provincia_id", "departamento_id"], ignore_index=True
    )
    validate_territories(provinces, territories)
    return territories


def validate_territories(
    provinces: pd.DataFrame, territories: pd.DataFrame
) -> None:
    """Valida identificadores, asociaciones y unicidad territorial."""
    identifier_columns = ["provincia_id", "departamento_id", "clave_territorial"]
    if territories[identifier_columns].isna().any().any():
        raise ValueError("Hay identificadores territoriales nulos.")
    if (territories[identifier_columns].apply(lambda column: column.str.strip()) == "").any().any():
        raise ValueError("Hay identificadores territoriales vacíos.")
    if provinces["provincia_id"].isna().any() or provinces["provincia_id"].duplicated().any():
        raise ValueError("Los identificadores de provincia deben ser no nulos y únicos.")
    if territories["departamento_id"].duplicated().any():
        raise ValueError("Hay identificadores de departamento duplicados.")
    if territories["clave_territorial"].duplicated().any():
        raise ValueError("Hay claves territoriales duplicadas.")
    if territories.duplicated().any():
        raise ValueError("Hay filas territoriales exactamente duplicadas.")

    valid_provinces = set(provinces["provincia_id"])
    associated_provinces = set(territories["provincia_id"])
    if not associated_provinces.issubset(valid_provinces):
        invalid = sorted(associated_provinces.difference(valid_provinces))
        raise ValueError(f"Hay departamentos asociados a provincias inválidas: {invalid}")
    if territories["provincia_nombre"].isna().any():
        raise ValueError("Hay departamentos sin provincia asociada.")


def build_department_geojson(
    department_features: list[dict[str, Any]], territories: pd.DataFrame
) -> dict[str, Any]:
    """Genera GeoJSON con propiedades normalizadas y geometrías sin simplificar."""
    by_department = {
        row["departamento_id"]: row for row in territories.to_dict("records")
    }
    normalized_features = []
    for feature in department_features:
        department_id = str(feature["properties"]["id"])
        properties = by_department[department_id]
        normalized_features.append(
            {
                "type": "Feature",
                "properties": {column: properties[column] for column in OUTPUT_COLUMNS},
                "geometry": feature.get("geometry"),
            }
        )
    return {"type": "FeatureCollection", "features": normalized_features}


def run_pipeline(
    provinces_path: Path = DEFAULT_PROVINCES_PATH,
    departments_path: Path = DEFAULT_DEPARTMENTS_PATH,
    parquet_path: Path = DEFAULT_PARQUET_PATH,
    geojson_path: Path = DEFAULT_GEOJSON_PATH,
) -> pd.DataFrame:
    """Ejecuta la ingestión completa y escribe las dos salidas procesadas."""
    provinces = load_provinces(provinces_path)
    department_features = load_department_features(departments_path)
    territories = build_territorial_dataframe(provinces, department_features)
    department_geojson = build_department_geojson(department_features, territories)

    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    geojson_path.parent.mkdir(parents=True, exist_ok=True)
    territories.to_parquet(parquet_path, index=False)
    with geojson_path.open("w", encoding="utf-8") as destination:
        json.dump(department_geojson, destination, ensure_ascii=False, separators=(",", ":"))

    return territories


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provinces", type=Path, default=DEFAULT_PROVINCES_PATH)
    parser.add_argument("--departments", type=Path, default=DEFAULT_DEPARTMENTS_PATH)
    parser.add_argument("--parquet-output", type=Path, default=DEFAULT_PARQUET_PATH)
    parser.add_argument("--geojson-output", type=Path, default=DEFAULT_GEOJSON_PATH)
    parser.add_argument(
        "--download",
        action="store_true",
        help="Descarga las fuentes oficiales; falla si algún destino raw ya existe.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.download:
        download_sources(arguments.provinces, arguments.departments)
    result = run_pipeline(
        provinces_path=arguments.provinces,
        departments_path=arguments.departments,
        parquet_path=arguments.parquet_output,
        geojson_path=arguments.geojson_output,
    )
    print(f"Base territorial generada: {len(result)} departamentos.")
