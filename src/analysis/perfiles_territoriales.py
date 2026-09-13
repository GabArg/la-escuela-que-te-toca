"""Resumen descriptivo de perfiles integrados, sin scores ni causalidad."""
from __future__ import annotations

import pandas as pd

PATH = "data/processed/perfiles_territoriales.parquet"


def coverage_summary(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    data = pd.read_parquet(PATH) if frame is None else frame
    columns = [c for c in data if c.startswith("cobertura_") and c != "cobertura_territorio"]
    return pd.DataFrame({"dimension": columns, "territorios": [int(data[c].sum()) for c in columns],
                         "porcentaje": [float(data[c].mean() * 100) for c in columns]})


def concurrent_signals(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    data = pd.read_parquet(PATH) if frame is None else frame
    flags = [c for c in data if c.startswith("bandera_")]
    result = data[["provincia_nombre", "departamento_nombre", "departamento_id"]].copy()
    result["senales_concurrentes"] = data[flags].fillna(False).sum(axis=1)
    return result.sort_values("senales_concurrentes", ascending=False)


def contrasting_profiles(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    """Casos ilustrativos por cruces de cuantiles, no etiquetas normativas."""
    data = pd.read_parquet(PATH) if frame is None else frame
    context = data[["porcentaje_hogares_computadora_2022", "porcentaje_hogares_internet_2022"]].mean(axis=1)
    learning = data["lengua_satisfactorio_o_avanzado_2024"]
    q_context = context.quantile([.25, .75]); q_learning = learning.quantile([.25, .75])
    kind = pd.Series(pd.NA, index=data.index, dtype="string")
    kind.loc[context.le(q_context.loc[.25]) & learning.ge(q_learning.loc[.75])] = "contexto bajo relativo + aprendizaje alto relativo"
    kind.loc[context.ge(q_context.loc[.75]) & learning.le(q_learning.loc[.25])] = "contexto alto relativo + aprendizaje bajo relativo"
    result = data[["provincia_nombre", "departamento_nombre", "departamento_id"]].copy()
    result["perfil_contrastante"] = kind
    result["contexto_digital_promedio"] = context
    result["lengua_satisfactorio_o_avanzado_2024"] = learning
    return result[result["perfil_contrastante"].notna()]
