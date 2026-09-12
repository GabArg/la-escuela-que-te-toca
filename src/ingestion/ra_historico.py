"""Pipeline reproducible para las bases RA departamentales 2011--2025.

Solo publica conteos con columnas y definiciones estables en todo el periodo.
No hace matching difuso, no completa ausencias y no asigna ID a Enmascarado o
Sin datos. Las tasas se calculan posteriormente desde conteos comparables.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from src.ingestion.educacion_departamental import normalize_column_name, normalize_text


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "data/raw/ra_historico"
GEOREF_PATH = ROOT / "data/processed/territorios_argentina.parquet"
BRIDGE_PATH = ROOT / "data/dictionaries/puente_nombres_departamentos_historico.csv"
BRIDGE_2025_PATH = ROOT / "data/dictionaries/puente_nombres_departamentos_2025.csv"
MANIFEST_PATH = ROOT / "data/dictionaries/fuentes_ra_historico.csv"
COMPARABILITY_PATH = ROOT / "data/dictionaries/comparabilidad_ra_2011_2025.csv"
OUTPUT_PATH = ROOT / "data/processed/ra_2011_2025_long.parquet"
DICTIONARY_URL = "https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/ETNQUApUc51BiLJLGAWuKtkB3PDw1t4QJZCX9d61_6D8-Q?e=hEkxgc"
YEARS = tuple(range(2011, 2026))
FAMILIES = ("matricula", "trayectoria", "caracteristicas")
SPECIAL = {"enmascarado", "sin datos"}
PROVINCE_ALIASES = {
    "ciudad de buenos aires": "ciudad autonoma de buenos aires",
    "tierra del fuego": "tierra del fuego antartida e islas del atlantico sur",
}

GRADES = [str(i) for i in range(1, 13)] + ["1314"]
VARIABLES = {
    "matricula": {
        "matricula_total": ["lactantes", "deambulantes", "s2", "s3", "s4", "s5"]
        + [f"campo_{g}" for g in GRADES] + ["snu"],
        "matricula_grados_comparables": [f"campo_{g}" for g in GRADES],
        "repitentes": [f"r_{g}" for g in GRADES],
        "sobreedad": [f"s_{g}" for g in GRADES],
    },
    "trayectoria": {
        "matricula_inicial": [f"inicial_{g}" for g in GRADES],
        "matricula_ultimo_dia": [f"ultimo_{g}" for g in GRADES],
        "salidos_con_pase": [f"scp_{g}" for g in GRADES],
        "salidos_sin_pase": [f"ssp_{g}" for g in GRADES],
        "promovidos": [f"promovidos_{g}" for g in GRADES],
        "no_promovidos": [f"nopromo_{g}" for g in GRADES],
        "egresados_primaria": ["primaria_egresados"],
        "egresados_secundaria": ["secundaria_egresados"],
    },
    "caracteristicas": {"localizaciones": ["localizacion"]},
}
DESCRIPTIONS = {
    "matricula_total": "Matrícula en categorías comunes a todos los años",
    "matricula_grados_comparables": "Matrícula en años de estudio con repitencia y sobreedad comparables",
    "repitentes": "Estudiantes repitentes en categorías comunes",
    "sobreedad": "Estudiantes con sobreedad en categorías comunes",
    "matricula_inicial": "Matrícula inicial en categorías comunes",
    "matricula_ultimo_dia": "Matrícula al último día de clase en categorías comunes",
    "salidos_con_pase": "Salidos con pase en categorías comunes",
    "salidos_sin_pase": "Salidos sin pase en categorías comunes",
    "promovidos": "Promovidos en categorías comunes",
    "no_promovidos": "No promovidos en categorías comunes",
    "egresados_primaria": "Egresados de primaria",
    "egresados_secundaria": "Egresados de secundaria",
    "localizaciones": "Cantidad de localizaciones educativas",
}


def load_raw(year: int, dataset: str, raw_root: Path = RAW_ROOT) -> pd.DataFrame:
    path = raw_root / str(year) / f"{dataset}.csv"
    frame = pd.read_csv(path, sep=";", dtype="string", keep_default_na=True)
    columns = [normalize_column_name(column) for column in frame.columns]
    if len(columns) != len(set(columns)):
        raise ValueError(f"Columnas duplicadas tras normalizar: {path}")
    frame.columns = columns
    missing = {"provincia", "departamento", "sector", "ambito"} - set(frame)
    if missing:
        raise ValueError(f"Faltan columnas territoriales en {path}: {sorted(missing)}")
    return frame.apply(lambda column: column.str.strip().replace("", pd.NA))


def load_georef(path: Path = GEOREF_PATH) -> pd.DataFrame:
    frame = pd.read_parquet(path).astype("string")
    frame["provincia_key"] = frame["provincia_nombre"].map(normalize_text)
    frame["departamento_key"] = frame["departamento_nombre"].map(normalize_text)
    return frame


def load_bridge(path: Path = BRIDGE_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["anio", "provincia", "nombre_ra", "departamento_id", "estado"])
    bridge = pd.read_csv(path, dtype="string")
    bridge["provincia_key"] = bridge["provincia"].map(normalize_text).replace(PROVINCE_ALIASES)
    bridge["departamento_key"] = bridge["nombre_ra"].map(normalize_text)
    return bridge


def attach_territory(frame: pd.DataFrame, year: int, georef: pd.DataFrame, bridge: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["provincia_nombre_fuente"] = result.pop("provincia")
    result["departamento_nombre_fuente"] = result.pop("departamento")
    result["provincia_key"] = result["provincia_nombre_fuente"].map(normalize_text).replace(PROVINCE_ALIASES)
    result["departamento_key"] = result["departamento_nombre_fuente"].map(normalize_text)
    lookup = georef[["provincia_key", "departamento_key", "provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre"]]
    result = result.merge(lookup, on=["provincia_key", "departamento_key"], how="left", validate="many_to_one")
    result["tipo_match"] = pd.Series(pd.NA, index=result.index, dtype="string")
    result.loc[result["departamento_id"].notna(), "tipo_match"] = "directo"
    confirmed = bridge.loc[(bridge["anio"].astype("Int64").eq(year)) & bridge["estado"].eq("confirmado")]
    if not confirmed.empty:
        b = confirmed[["provincia_key", "departamento_key", "departamento_id"]].rename(columns={"departamento_id": "bridge_id"})
        result = result.merge(b, on=["provincia_key", "departamento_key"], how="left", validate="many_to_one")
        mask = result["departamento_id"].isna() & result["bridge_id"].notna()
        official = georef.set_index("departamento_id")
        result.loc[mask, "departamento_id"] = result.loc[mask, "bridge_id"]
        for column in ["provincia_id", "provincia_nombre", "departamento_nombre"]:
            result.loc[mask, column] = result.loc[mask, "bridge_id"].map(official[column])
        result.loc[mask, "tipo_match"] = "puente"
        result = result.drop(columns="bridge_id")
    special = result["departamento_key"].isin(SPECIAL)
    result.loc[special, "tipo_match"] = result.loc[special, "departamento_key"]
    result.loc[special, ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre"]] = pd.NA
    result.loc[result["tipo_match"].isna(), "tipo_match"] = "por_verificar"
    return result


def _sum_preserving_null(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    absent = set(columns) - set(frame)
    if absent:
        raise ValueError(f"Cambio de esquema: faltan {sorted(absent)}")
    numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
    return numeric.sum(axis=1, min_count=1).astype("Float64")


def transform_family(frame: pd.DataFrame, year: int, dataset: str) -> pd.DataFrame:
    identity = ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "sector", "ambito", "tipo_match"]
    pieces = []
    for standard, source_columns in VARIABLES[dataset].items():
        piece = frame[identity].copy()
        piece.insert(0, "anio", year)
        piece["variable"] = standard
        piece["valor"] = _sum_preserving_null(frame, source_columns)
        piece["nivel_comparabilidad"] = "Alta"
        piece["estado_cobertura"] = frame["tipo_match"].replace({"directo": "observado", "puente": "observado"})
        pieces.append(piece)
    return pd.concat(pieces, ignore_index=True)


def build_long(raw_root: Path = RAW_ROOT) -> pd.DataFrame:
    georef, bridge = load_georef(), load_bridge()
    pieces = []
    for year in YEARS:
        for dataset in FAMILIES:
            attached = attach_territory(load_raw(year, dataset, raw_root), year, georef, bridge)
            pieces.append(transform_family(attached, year, dataset))
    result = pd.concat(pieces, ignore_index=True)
    result["valor"] = result["valor"].astype("Float64")
    return result


def validate_long(frame: pd.DataFrame) -> None:
    if set(frame["anio"].unique()) != set(YEARS):
        raise ValueError("La salida no contiene todos los años esperados.")
    if not set(frame["variable"]).issubset({v for family in VARIABLES.values() for v in family}):
        raise ValueError("Ingresó una variable no aprobada.")
    grain = ["anio", "departamento_id", "sector", "ambito", "variable"]
    identified = frame["departamento_id"].notna()
    if frame.loc[identified].duplicated(grain).any():
        raise ValueError("Duplicados inesperados en el grano longitudinal.")
    special = frame["estado_cobertura"].isin(SPECIAL)
    if frame.loc[special, "departamento_id"].notna().any():
        raise ValueError("Un registro especial recibió ID.")
    if (frame["valor"].dropna() < 0).any():
        raise ValueError("Hay conteos negativos.")


def write_long(path: Path = OUTPUT_PATH) -> pd.DataFrame:
    frame = build_long()
    validate_long(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


def verify_hashes(manifest_path: Path = MANIFEST_PATH) -> None:
    manifest = pd.read_csv(manifest_path, dtype="string")
    for row in manifest.itertuples(index=False):
        digest = hashlib.sha256((ROOT / row.archivo_local).read_bytes()).hexdigest()
        if digest != row.sha256:
            raise ValueError(f"Hash inválido: {row.archivo_local}")


def enrich_source_inventory(manifest_path: Path = MANIFEST_PATH) -> pd.DataFrame:
    """Añade perfil estructural verificable al manifiesto de descargas."""
    manifest = pd.read_csv(manifest_path, dtype="string")
    profiles = []
    for row in manifest.itertuples(index=False):
        frame = pd.read_csv(ROOT / row.archivo_local, sep=";", dtype="string")
        department_column = "departamento" if "departamento" in frame else "Departamento"
        profiles.append({
            "anio": int(row.anio), "dataset": row.dataset,
            "filas": len(frame), "columnas": len(frame.columns),
            "granularidad": "provincia-departamento-sector-ámbito",
            "sectores_publicados": ";".join(sorted(frame["sector"].dropna().str.strip().unique())),
            "ambitos_publicados": ";".join(sorted(frame["ambito"].dropna().str.strip().unique())),
            "identificador_territorial_fuente": "nombres de provincia y departamento; sin códigos",
            "filas_enmascarado": int(frame[department_column].str.strip().eq("Enmascarado").sum()),
            "filas_sin_datos": int(frame[department_column].str.strip().eq("Sin datos").sum()),
            "diccionario": "Diccionario de bases RA anonimizadas.xlsx (común)",
            "url_diccionario": DICTIONARY_URL,
        })
    profile = pd.DataFrame(profiles)
    extra = [column for column in profile if column not in {"anio", "dataset"}]
    manifest = manifest.drop(columns=[column for column in extra if column in manifest], errors="ignore")
    manifest["anio"] = manifest["anio"].astype(int)
    result = manifest.merge(profile, on=["anio", "dataset"], validate="one_to_one")
    result.to_csv(manifest_path, index=False, encoding="utf-8")
    return result


def write_bridge_audit(path: Path = BRIDGE_PATH) -> pd.DataFrame:
    """Documenta no-coincidencias; solo hereda puentes ya auditados en 2025."""
    georef = load_georef()
    prior = pd.read_csv(BRIDGE_2025_PATH, dtype="string")
    prior["provincia_key"] = prior["provincia_fuente"].map(normalize_text).replace(PROVINCE_ALIASES)
    prior["departamento_key"] = prior["departamento_fuente"].map(normalize_text)
    prior = prior.rename(columns={"departamento_id": "candidate_id"})
    rows = []
    for year in YEARS:
        raw = load_raw(year, "matricula")
        raw["provincia_key"] = raw["provincia"].map(normalize_text).replace(PROVINCE_ALIASES)
        raw["departamento_key"] = raw["departamento"].map(normalize_text)
        direct = raw.merge(georef[["provincia_key", "departamento_key", "departamento_id"]], on=["provincia_key", "departamento_key"], how="left")
        missing = direct.loc[direct["departamento_id"].isna() & ~direct["departamento_key"].isin(SPECIAL), ["provincia", "departamento", "provincia_key", "departamento_key"]].drop_duplicates()
        missing = missing.merge(prior, on=["provincia_key", "departamento_key"], how="left", suffixes=("", "_prior"))
        for item in missing.itertuples(index=False):
            inherited = pd.notna(item.estado)
            rows.append({
                "anio": year, "provincia": item.provincia,
                "nombre_ra": item.departamento,
                "nombre_georef": item.departamento_nombre_georef if inherited else pd.NA,
                "departamento_id": item.candidate_id if inherited else pd.NA,
                "tipo_equivalencia": item.tipo_diferencia if inherited else "por verificar",
                "estado": item.estado if inherited else "pendiente",
                "evidencia": item.evidencia if inherited else "Sin equivalencia oficial documentada; no se asigna ID.",
                "observaciones": "Heredado de auditoría 2025" if inherited else "Diferencia histórica o unidad territorial no equivalente a GeoRef actual.",
            })
    bridge = pd.DataFrame(rows).sort_values(["anio", "provincia", "nombre_ra"])
    bridge.to_csv(path, index=False, encoding="utf-8")
    return bridge


def write_comparability_inventory(path: Path = COMPARABILITY_PATH) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        for dataset, mapping in VARIABLES.items():
            for standard, origins in mapping.items():
                rows.append({
                    "anio": year, "dataset": dataset,
                    "variable_origen": "+".join(origins), "variable_estandar": standard,
                    "descripcion": DESCRIPTIONS[standard], "unidad": "conteo",
                    "comparable": "sí", "nivel_comparabilidad": "Alta",
                    "motivo": "Mismas columnas componentes y mismo grano en los 15 archivos; definición común en el diccionario oficial.",
                    "observaciones": "No incorporar la categoría _20 añadida desde 2023; conservar sector y ámbito.",
                })
        raw_m = load_raw(year, "matricula")
        for variable in ["campo_20", "r_20"]:
            if variable in raw_m:
                rows.append({"anio": year, "dataset": "matricula", "variable_origen": variable,
                    "variable_estandar": "", "descripcion": "Categoría 20 añadida al esquema",
                    "unidad": "conteo", "comparable": "no", "nivel_comparabilidad": "No comparable",
                    "motivo": "No existe en 2011–2022.", "observaciones": "Excluida de la serie completa."})
        for variable in ["s_lactantes", "s_deambulantes", "s_s2", "s_s3", "s_s4", "s_s5"]:
            rows.append({"anio": year, "dataset": "matricula", "variable_origen": variable,
                "variable_estandar": "", "descripcion": "Sobreedad en categorías de inicial",
                "unidad": "conteo", "comparable": "no", "nivel_comparabilidad": "No comparable",
                "motivo": "Definición ambigua/inconsistente en el diccionario disponible.", "observaciones": "No se usa sustantivamente."})
        raw_c = load_raw(year, "caracteristicas")
        for variable in raw_c.columns:
            if variable not in {"provincia", "departamento", "sector", "ambito", "localizacion"}:
                rows.append({"anio": year, "dataset": "caracteristicas", "variable_origen": variable,
                    "variable_estandar": "", "descripcion": "Característica de localización",
                    "unidad": "por verificar", "comparable": "no", "nivel_comparabilidad": "No comparable",
                    "motivo": "Unidad agregada ambigua y cambios de esquema/nombre.", "observaciones": "Excluida hasta contar con definición anual inequívoca."})
        for standard, numerator, denominator in [
            ("proporcion_repitentes", "repitentes", "matricula_grados_comparables"),
            ("proporcion_sobreedad", "sobreedad", "matricula_grados_comparables"),
            ("proporcion_salidos_sin_pase", "salidos_sin_pase", "matricula_inicial"),
        ]:
            rows.append({"anio": year, "dataset": "derivada", "variable_origen": f"{numerator}/{denominator}",
                "variable_estandar": standard, "descripcion": "Cociente exploratorio recalculado desde conteos comparables",
                "unidad": "proporción", "comparable": "sí con advertencia", "nivel_comparabilidad": "Media",
                "motivo": "Fórmula estable, pero no es tasa oficial y su interpretación atraviesa discontinuidades administrativas potenciales.",
                "observaciones": "No se almacena en el parquet largo; se recalcula. Cautela especial en 2020–2022."})
    inventory = pd.DataFrame(rows).sort_values(["anio", "dataset", "nivel_comparabilidad", "variable_origen"])
    inventory.to_csv(path, index=False, encoding="utf-8")
    return inventory


if __name__ == "__main__":
    verify_hashes()
    enrich_source_inventory()
    if not BRIDGE_PATH.exists():
        write_bridge_audit()
    write_comparability_inventory()
    output = write_long()
    print(f"Filas: {len(output):,}; años: {output.anio.nunique()}; variables: {output.variable.nunique()}")
