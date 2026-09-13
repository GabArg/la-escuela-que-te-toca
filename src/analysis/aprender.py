"""Analisis descriptivo de Aprender 2024, sin inferencia causal."""
from __future__ import annotations

import numpy as np
import pandas as pd
from src.analysis.ra_2025 import aggregate_departments

APRENDER = "data/processed/aprender_analitico.parquet"
RA = "data/processed/ra_2025_analitico.parquet"
CONTEXT = "data/processed/contexto_socioeconomico_2022.parquet"
CONDITIONS = "data/processed/condiciones_escolaridad_2022.parquet"


def performance_wide() -> pd.DataFrame:
    data = pd.read_parquet(APRENDER)
    return data.pivot(index=["departamento_id", "provincia_nombre", "departamento_nombre"],
                      columns=["area", "indicador"], values="valor").reset_index()


def analysis_table() -> pd.DataFrame:
    learn = performance_wide()
    learn.columns = [c if isinstance(c, str) else "_".join(str(x) for x in c if x) for c in learn.columns]
    context = pd.read_parquet(CONTEXT)
    context_cols = [c for c in ["departamento_id", "porcentaje_hogares_internet", "porcentaje_hogares_computadora",
                                "porcentaje_hogares_agua_red_publica", "porcentaje_hogares_cloaca",
                                "porcentaje_asistencia_15_17"] if c in context.columns]
    conditions = pd.read_parquet(CONDITIONS)
    condition_cols = [c for c in ["departamento_id", "densidad_poblacional", "proporcion_establecimientos_rurales",
                                  "secundarias_por_1000_adolescentes", "relacion_secundaria_primaria"] if c in conditions.columns]
    result = learn.merge(context[context_cols], on="departamento_id", how="left", validate="one_to_one")
    result = result.merge(conditions[condition_cols], on="departamento_id", how="left", validate="one_to_one")
    ra = aggregate_departments(pd.read_parquet(RA))
    ra_cols = [c for c in ["departamento_id", "proporcion_repitentes_sobre_matricula",
                           "proporcion_sobreedad_sobre_matricula", "proporcion_salidos_sin_pase_sobre_inicial",
                           "proporcion_promovidos_sobre_ultimo_dia"] if c in ra.columns]
    return result.merge(ra[ra_cols], on="departamento_id", how="left", validate="one_to_one")


def spearman_associations() -> pd.DataFrame:
    data = analysis_table()
    outcomes = ["Lengua_satisfactorio", "Matematica_satisfactorio"]
    contexts = [c for c in ["porcentaje_hogares_internet", "porcentaje_hogares_computadora",
                            "porcentaje_hogares_agua_red_publica", "porcentaje_hogares_cloaca",
                            "porcentaje_asistencia_15_17", "densidad_poblacional",
                            "proporcion_establecimientos_rurales", "secundarias_por_1000_adolescentes",
                            "relacion_secundaria_primaria", "proporcion_repitentes_sobre_matricula",
                            "proporcion_sobreedad_sobre_matricula", "proporcion_salidos_sin_pase_sobre_inicial",
                            "proporcion_promovidos_sobre_ultimo_dia"] if c in data]
    rows = []
    for outcome in outcomes:
        for context in contexts:
            valid = data[[outcome, context]].replace([np.inf, -np.inf], np.nan).dropna()
            rows.append({"aprendizaje": outcome, "contexto": context, "n": len(valid),
                         "spearman": valid[outcome].corr(valid[context], method="spearman") if len(valid) >= 3 else np.nan,
                         "anio_aprendizaje": 2024})
    return pd.DataFrame(rows)


def comparable_pairs(max_distance: float = 0.55, min_gap: float = 10.0) -> pd.DataFrame:
    """Pares exploratorios por distancia estandarizada solo en estructura."""
    data = analysis_table()
    features = [c for c in ["densidad_poblacional", "proporcion_establecimientos_rurales",
                            "secundarias_por_1000_adolescentes", "porcentaje_hogares_internet",
                            "porcentaje_hogares_computadora", "porcentaje_asistencia_15_17"] if c in data]
    outcome = "Matematica_satisfactorio"
    valid = data[["departamento_id", "provincia_nombre", "departamento_nombre", outcome] + features].dropna()
    z = (valid[features] - valid[features].mean()) / valid[features].std(ddof=0).replace(0, np.nan)
    rows = []
    values = valid.reset_index(drop=True)
    z = z.reset_index(drop=True)
    for i in range(len(values)):
        distances = ((z - z.iloc[i]) ** 2).mean(axis=1).pow(0.5)
        for j in distances[(distances <= max_distance) & (distances.index > i)].index:
            gap = abs(values.loc[i, outcome] - values.loc[j, outcome])
            if gap >= min_gap:
                rows.append({"departamento_a": values.loc[i, "departamento_id"], "departamento_b": values.loc[j, "departamento_id"],
                             "distancia_estructural": distances[j], "brecha_matematica_satisfactorio_pp": gap})
    return pd.DataFrame(rows).sort_values("brecha_matematica_satisfactorio_pp", ascending=False) if rows else pd.DataFrame()
