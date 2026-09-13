"""Motor transparente de pares territoriales comparables.

La similitud usa exclusivamente estructura territorial, contexto del hogar y
oferta. Los resultados educativos se agregan solo despues de fijar vecinos.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "data/processed/perfiles_territoriales.parquet"
PAIRS_PATH = ROOT / "data/processed/pares_comparables.parquet"
GAPS_PATH = ROOT / "data/processed/brechas_entre_pares.parquet"
SENSITIVITY_PATH = ROOT / "data/processed/sensibilidad_pares.parquet"
MIN_SHARED = 9
MIN_PER_DIMENSION = 2
TOP_K = 5


@dataclass(frozen=True)
class VariableSpec:
    variable: str
    dimension: str
    transform: str


BASE_SPECS = [
    VariableSpec("poblacion_total", "territorio", "log1p"),
    VariableSpec("superficie_km2", "territorio", "log1p"),
    VariableSpec("densidad_poblacional", "territorio", "log1p"),
    VariableSpec("porcentaje_hogares_internet_2022", "contexto", "identidad"),
    VariableSpec("porcentaje_hogares_computadora_2022", "contexto", "identidad"),
    VariableSpec("porcentaje_hogares_agua_red_publica_2022", "contexto", "identidad"),
    VariableSpec("porcentaje_hogares_cloaca_2022", "contexto", "identidad"),
    VariableSpec("porcentaje_viviendas_rancho_casilla_2022", "contexto", "log1p"),
    VariableSpec("proporcion_cue_rurales_2022", "oferta", "identidad"),
    VariableSpec("relacion_cue_secundaria_primaria_2022", "oferta", "identidad"),
    VariableSpec("localizaciones_por_1000_poblacion_escolar_2022", "oferta", "log1p"),
    VariableSpec("localizaciones_por_100_km2_2022", "oferta", "log1p"),
]

EDUCATIONAL_RESULTS = [
    "porcentaje_asistencia_15_17_2022", "sobreedad_2025", "repeticion_2025",
    "salidos_sin_pase_2025", "promocion_2025", "no_promocion_2025",
    "lengua_satisfactorio_o_avanzado_2024",
    "matematica_satisfactorio_o_avanzado_2024",
]

SENSITIVITY_SPECS = {
    "base": BASE_SPECS,
    "sin_conectividad": [s for s in BASE_SPECS if s.variable not in {
        "porcentaje_hogares_internet_2022", "porcentaje_hogares_computadora_2022"}],
    "sin_oferta": [s for s in BASE_SPECS if s.dimension != "oferta"],
    "solo_territorio_contexto": [s for s in BASE_SPECS if s.dimension in {"territorio", "contexto"}],
}


def dimension_weights(specs: list[VariableSpec]) -> dict[str, float]:
    dimensions = sorted({spec.dimension for spec in specs})
    return {dimension: 1 / len(dimensions) for dimension in dimensions}


def variable_weights(specs: list[VariableSpec]) -> dict[str, float]:
    dimensions = dimension_weights(specs)
    counts = pd.Series([spec.dimension for spec in specs]).value_counts()
    return {spec.variable: dimensions[spec.dimension] / counts[spec.dimension] for spec in specs}


def robust_matrix(profiles: pd.DataFrame, specs: list[VariableSpec]) -> pd.DataFrame:
    """Transforma, centra por mediana/IQR y acota a [-5, 5]."""
    result = pd.DataFrame(index=profiles.index)
    for spec in specs:
        values = profiles[spec.variable].astype(float)
        transformed = np.log1p(values) if spec.transform == "log1p" else values
        median = transformed.median()
        iqr = transformed.quantile(.75) - transformed.quantile(.25)
        if not np.isfinite(iqr) or iqr <= 0:
            raise ValueError(f"IQR no valido para {spec.variable}")
        result[spec.variable] = ((transformed - median) / iqr).clip(-5, 5)
    return result


def _eligible_pair(raw: pd.DataFrame, matrix: pd.DataFrame, i: int, j: int, specs: list[VariableSpec]) -> tuple[bool, list[str]]:
    shared = [s.variable for s in specs if pd.notna(matrix.at[i, s.variable]) and pd.notna(matrix.at[j, s.variable])]
    minimum = min(MIN_SHARED, len(specs))
    if len(shared) < minimum:
        return False, shared
    for dimension in {s.dimension for s in specs}:
        dimension_vars = [s.variable for s in specs if s.dimension == dimension]
        if len(set(shared).intersection(dimension_vars)) < min(MIN_PER_DIMENSION, len(dimension_vars)):
            return False, shared
    # Restricciones amplias previenen comparaciones extremas sin exigir provincia.
    population = raw.loc[[i, j], "poblacion_total"]
    if population.isna().any() or population.max() / population.min() > 10:
        return False, shared
    rural = raw.loc[[i, j], "proporcion_cue_rurales_2022"]
    if rural.notna().all() and abs(rural.iloc[0] - rural.iloc[1]) > .50:
        return False, shared
    return True, shared


def _distance(matrix: pd.DataFrame, i: int, j: int, shared: list[str], specs: list[VariableSpec]) -> tuple[float, pd.Series]:
    weights = pd.Series(variable_weights(specs)).loc[shared]
    weights = weights / weights.sum()
    contributions = (matrix.loc[i, shared] - matrix.loc[j, shared]).abs() / 10
    return float((contributions * weights).sum()), contributions


def neighbor_table(profiles: pd.DataFrame, specs: list[VariableSpec], comparison_type: str = "nacional") -> pd.DataFrame:
    matrix = robust_matrix(profiles, specs)
    values = matrix.to_numpy(float)
    present = np.isfinite(values)
    weights_array = np.array([variable_weights(specs)[s.variable] for s in specs])
    population = profiles["poblacion_total"].to_numpy(float)
    rural = profiles["proporcion_cue_rurales_2022"].to_numpy(float)
    province = profiles["provincia_id"].astype(str).to_numpy()
    dimension_indices = {
        dimension: np.array([index for index, spec in enumerate(specs) if spec.dimension == dimension])
        for dimension in {spec.dimension for spec in specs}
    }
    rows = []
    for i in profiles.index:
        shared_mask = present & present[i]
        eligible = shared_mask.sum(axis=1) >= min(MIN_SHARED, len(specs))
        for indices in dimension_indices.values():
            eligible &= shared_mask[:, indices].sum(axis=1) >= min(MIN_PER_DIMENSION, len(indices))
        pop_min = np.minimum(population, population[i])
        pop_max = np.maximum(population, population[i])
        eligible &= np.isfinite(population) & np.isfinite(population[i]) & (pop_max / pop_min <= 10)
        rural_difference = np.abs(rural - rural[i])
        eligible &= (~np.isfinite(rural_difference)) | (rural_difference <= .50)
        eligible[i] = False
        if comparison_type == "provincial":
            eligible &= province == province[i]
        differences = np.abs(values - values[i]) / 10
        weighted = np.where(shared_mask, differences * weights_array, 0)
        used_weight = np.where(shared_mask, weights_array, 0).sum(axis=1)
        distances = weighted.sum(axis=1) / used_weight
        distances[~eligible] = np.inf
        candidate_indices = np.flatnonzero(np.isfinite(distances))
        candidate_indices = sorted(candidate_indices, key=lambda j: (distances[j], str(profiles.at[j, "departamento_id"])))[:TOP_K]
        for rank, j in enumerate(candidate_indices, start=1):
            shared_indices = np.flatnonzero(shared_mask[j])
            shared = [specs[k].variable for k in shared_indices]
            contributions = pd.Series(differences[j, shared_indices], index=shared)
            ordered = contributions.sort_values()
            similar = ordered.head(min(3, len(ordered))).index.tolist()
            different = ordered.tail(min(3, len(ordered))).sort_values(ascending=False).index.tolist()
            rows.append({
                "departamento_id": profiles.at[i, "departamento_id"],
                "departamento_nombre": profiles.at[i, "departamento_nombre"],
                "provincia_nombre": profiles.at[i, "provincia_nombre"],
                "par_departamento_id": profiles.at[j, "departamento_id"],
                "par_departamento_nombre": profiles.at[j, "departamento_nombre"],
                "par_provincia_nombre": profiles.at[j, "provincia_nombre"],
                "ranking_similitud_interno": rank,
                "distancia": float(distances[j]),
                "variables_usadas": ";".join(shared),
                "variables_mas_similares": ";".join(similar),
                "principales_diferencias": ";".join(different),
                "n_variables_usadas": len(shared),
                "cobertura_comparacion": len(shared) / len(specs),
                "tipo_comparacion": comparison_type,
            })
    return pd.DataFrame(rows)


def sensitivity(profiles: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    base_sets = base[base.tipo_comparacion.eq("nacional")].groupby("departamento_id").par_departamento_id.agg(set)
    rows = []
    for name, specs in SENSITIVITY_SPECS.items():
        neighbors = base[base.tipo_comparacion.eq("nacional")] if name == "base" else neighbor_table(profiles, specs, "nacional")
        sets = neighbors.groupby("departamento_id").par_departamento_id.agg(set)
        common = base[base.tipo_comparacion.eq("nacional")][["departamento_id", "par_departamento_id", "distancia"]].merge(
            neighbors[["departamento_id", "par_departamento_id", "distancia"]],
            on=["departamento_id", "par_departamento_id"], suffixes=("_base", "_alternativa"),
        )
        distance_correlation = common.distancia_base.corr(common.distancia_alternativa, method="spearman") if len(common) >= 3 else np.nan
        for territory, reference in base_sets.items():
            alternate = sets.get(territory, set())
            overlap = len(reference.intersection(alternate)) / TOP_K
            rows.append({"departamento_id": territory, "especificacion": name,
                         "vecinos_base_presentes": len(reference.intersection(alternate)),
                         "proporcion_estable_top5": overlap,
                         "correlacion_spearman_distancias_comunes": distance_correlation,
                         "n_pares_distancia_comun": len(common)})
    return pd.DataFrame(rows)


def add_quality(pairs: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    result = pairs.copy()
    # sin_oferta y solo_territorio_contexto son deliberadamente equivalentes;
    # se reportan ambos, pero no se ponderan dos veces en la calidad.
    stable = stability[stability.especificacion.isin(["sin_conectividad", "sin_oferta"])].groupby("departamento_id").proporcion_estable_top5.mean()
    result["estabilidad_origen"] = result.departamento_id.map(stable)
    national = result[result.tipo_comparacion.eq("nacional")]
    q25, q75 = national.distancia.quantile([.25, .75])
    high = result.distancia.le(q25) & result.cobertura_comparacion.eq(1) & result.estabilidad_origen.ge(.60)
    medium = result.distancia.le(q75) & result.cobertura_comparacion.ge(.80) & result.estabilidad_origen.ge(.40)
    result["calidad_comparacion"] = np.select([high, medium], ["Alta comparabilidad", "Comparabilidad media"], default="Comparabilidad baja")
    return result


def educational_gaps(pairs: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
    """Adjunta resultados despues de construir y congelar los pares."""
    outcomes = {
        "sobreedad_2025": "brecha_sobreedad_pp",
        "repeticion_2025": "brecha_repeticion_pp",
        "salidos_sin_pase_2025": "brecha_salidos_sin_pase_pp",
        "porcentaje_asistencia_15_17_2022": "brecha_asistencia_15_17_pp",
        "lengua_satisfactorio_o_avanzado_2024": "brecha_lengua_satisfactorio_avanzado_pp",
        "matematica_satisfactorio_o_avanzado_2024": "brecha_matematica_satisfactorio_avanzado_pp",
    }
    lookup = profiles.set_index("departamento_id")
    result = pairs.copy()
    for source, target in outcomes.items():
        left = result.departamento_id.map(lookup[source])
        right = result.par_departamento_id.map(lookup[source])
        factor = 100 if source in {"sobreedad_2025", "repeticion_2025", "salidos_sin_pase_2025"} else 1
        result[target] = (left - right).abs() * factor
    return result


def build_engine() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    profiles = pd.read_parquet(PROFILE_PATH).reset_index(drop=True)
    if set(EDUCATIONAL_RESULTS).intersection(spec.variable for spec in BASE_SPECS):
        raise ValueError("Una variable educativa entro a la matriz de similitud.")
    national = neighbor_table(profiles, BASE_SPECS, "nacional")
    provincial = neighbor_table(profiles, BASE_SPECS, "provincial")
    raw_pairs = pd.concat([national, provincial], ignore_index=True)
    audit = sensitivity(profiles, raw_pairs)
    pairs = add_quality(raw_pairs, audit)
    gaps = educational_gaps(pairs, profiles)
    return pairs, gaps, audit


def validate(pairs: pd.DataFrame, gaps: pd.DataFrame) -> None:
    if pairs.departamento_id.eq(pairs.par_departamento_id).any():
        raise ValueError("Un territorio no puede ser su propio par.")
    grain = ["departamento_id", "par_departamento_id", "tipo_comparacion"]
    if pairs.duplicated(grain).any() or pairs.distancia.lt(0).any():
        raise ValueError("Pares duplicados o distancia negativa.")
    if pairs.groupby(["departamento_id", "tipo_comparacion"]).size().gt(TOP_K).any():
        raise ValueError("Se excedio el maximo de vecinos.")
    learning = gaps[gaps.brecha_matematica_satisfactorio_avanzado_pp.notna()]
    if not learning.departamento_id.isin(pairs.departamento_id).all():
        raise ValueError("Brechas calculadas fuera del conjunto de pares.")


def write_engine() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pairs, gaps, audit = build_engine()
    validate(pairs, gaps)
    PAIRS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pairs.to_parquet(PAIRS_PATH, index=False)
    gaps.to_parquet(GAPS_PATH, index=False)
    audit.to_parquet(SENSITIVITY_PATH, index=False)
    return pairs, gaps, audit


if __name__ == "__main__":
    pairs, gaps, audit = write_engine()
    print(f"pares={len(pairs)} territorios={pairs.departamento_id.nunique()} brechas={len(gaps)}")
