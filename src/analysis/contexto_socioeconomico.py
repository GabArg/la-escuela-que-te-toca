"""Análisis descriptivo del contexto Censo 2022 y señales educativas."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.ra_2025 import aggregate_departments

CONTEXT = "data/processed/contexto_socioeconomico_2022.parquet"
CONDITIONS = "data/processed/condiciones_escolaridad_2022.parquet"
RA = "data/processed/ra_2025_analitico.parquet"
ACCESS = "data/processed/acceso_escolar.parquet"

CONTEXT_VARS = [
    "porcentaje_hogares_internet", "porcentaje_hogares_computadora",
    "porcentaje_hogares_agua_red_publica", "porcentaje_hogares_cloaca",
    "porcentaje_viviendas_rancho_casilla", "porcentaje_asistencia_4_5",
    "porcentaje_asistencia_6_11", "porcentaje_asistencia_12_14",
    "porcentaje_asistencia_15_17",
]
OUTCOMES = ["proporcion_repetidores_sobre_matricula", "proporcion_sobreedad_sobre_matricula",
            "proporcion_salidos_sin_pase_sobre_inicial"]


def analysis_table() -> pd.DataFrame:
    context = pd.read_parquet(CONTEXT)
    conditions = pd.read_parquet(CONDITIONS)[["departamento_id", "densidad_poblacional", "poblacion_4_17",
                                              "proporcion_establecimientos_rurales", "secundarias_por_1000_adolescentes"]]
    ra = aggregate_departments(pd.read_parquet(RA))[["departamento_id"] + OUTCOMES]
    return context.merge(conditions, on="departamento_id", how="left", validate="one_to_one").merge(
        ra, on="departamento_id", how="left", validate="one_to_one")


def spearman_associations() -> pd.DataFrame:
    data = analysis_table(); rows = []
    for context in CONTEXT_VARS:
        for outcome in OUTCOMES:
            valid = data[[context, outcome]].dropna()
            rows.append({"contexto": context, "resultado": outcome, "n": len(valid),
                         "spearman": valid[context].corr(valid[outcome], method="spearman"),
                         "anio_contexto": 2022, "anio_resultado": 2025})
    return pd.DataFrame(rows)


def _rank_residual(values: pd.Series, controls: pd.DataFrame) -> np.ndarray:
    y = values.rank().to_numpy(float)
    x = np.column_stack([np.ones(len(controls))] + [controls[c].rank().to_numpy(float) for c in controls])
    return y - x @ np.linalg.lstsq(x, y, rcond=None)[0]


def partial_spearman(context: str, outcome: str) -> dict:
    """Correlación parcial exploratoria sobre rangos, no estimación causal."""
    controls = ["densidad_poblacional", "poblacion_4_17", "proporcion_establecimientos_rurales",
                "secundarias_por_1000_adolescentes"]
    data = analysis_table()[[context, outcome] + controls].replace([np.inf, -np.inf], np.nan).dropna()
    rx = _rank_residual(data[context], data[controls]); ry = _rank_residual(data[outcome], data[controls])
    return {"contexto": context, "resultado": outcome, "n": len(data),
            "spearman_parcial_exploratoria": pd.Series(rx).corr(pd.Series(ry)), "controles": ";".join(controls)}


def access_comparison() -> pd.DataFrame:
    """Compara residencia/asistencia censal con matrícula por localización RA."""
    context = pd.read_parquet(CONTEXT)
    access = pd.read_parquet(ACCESS)
    access = access.pivot(index="departamento_id", columns="grupo_edad", values="indicador_acceso").reset_index()
    access = access.rename(columns={group: f"cociente_matricula_poblacion_{group.replace('-', '_')}" for group in ["4-5", "6-11", "12-14", "15-17"]})
    return context.merge(access, on="departamento_id", how="left", validate="one_to_one")
