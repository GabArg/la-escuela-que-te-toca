"""Carga cacheada y reconstrucción delegada de outputs procesados."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"


class DataAvailabilityError(RuntimeError):
    """Error legible de disponibilidad, sin exponer un stacktrace al usuario."""


def _ensure(name: str) -> Path:
    path = PROCESSED / name
    if path.exists():
        return path
    try:
        if name in {"perfiles_territoriales.parquet", "senales_prioritarias_perfiles.parquet"}:
            from src.features.perfiles_territoriales import write_profiles
            write_profiles()
        elif name in {"pares_comparables.parquet", "brechas_entre_pares.parquet"}:
            from src.analysis.pares_comparables import write_engine
            write_engine()
        elif name == "ra_2011_2025_long.parquet":
            from src.ingestion.ra_historico import write_long
            write_long()
    except Exception as exc:
        raise DataAvailabilityError(
            f"No se pudo reconstruir {name}. Revisá que los datos fuente requeridos estén disponibles."
        ) from exc
    if not path.exists():
        raise DataAvailabilityError(
            f"Falta {name}. Ejecutá el pipeline documentado antes de iniciar la aplicación."
        )
    return path


@st.cache_data(show_spinner=False)
def load_profiles() -> pd.DataFrame:
    return pd.read_parquet(_ensure("perfiles_territoriales.parquet"))


@st.cache_data(show_spinner=False)
def load_signals() -> pd.DataFrame:
    return pd.read_parquet(_ensure("senales_prioritarias_perfiles.parquet"))


@st.cache_data(show_spinner=False)
def load_pairs() -> pd.DataFrame:
    return pd.read_parquet(_ensure("pares_comparables.parquet"))


@st.cache_data(show_spinner=False)
def load_gaps() -> pd.DataFrame:
    return pd.read_parquet(_ensure("brechas_entre_pares.parquet"))


@st.cache_data(show_spinner=False)
def load_history() -> pd.DataFrame:
    from src.analysis.ra_historico import build_indicators
    return build_indicators(pd.read_parquet(_ensure("ra_2011_2025_long.parquet")))
