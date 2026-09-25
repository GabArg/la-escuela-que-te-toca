"""Carga cacheada: bundle público primero, outputs locales después."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = Path(os.environ.get("PUBLIC_DATA_DIR", ROOT / "data/public"))
PROCESSED = Path(os.environ.get("PROCESSED_DATA_DIR", ROOT / "data/processed"))


class DataAvailabilityError(RuntimeError):
    """Error legible de disponibilidad, sin exponer un stacktrace al usuario."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_public(path: Path) -> None:
    manifest_path = PUBLIC / "manifest.json"
    if not manifest_path.exists():
        raise DataAvailabilityError("El bundle público no contiene manifest.json.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {item["name"]: item["sha256"] for item in manifest.get("files", [])}.get(path.name)
    if not expected or _sha256(path) != expected:
        raise DataAvailabilityError(f"Falló la verificación de integridad de {path.name}.")


def artifact_path(name: str) -> Path:
    public_path = PUBLIC / name
    if public_path.exists():
        _verify_public(public_path)
        return public_path
    local_path = PROCESSED / name
    if local_path.exists():
        return local_path
    if os.environ.get("APP_ALLOW_PIPELINE_REBUILD", "0") != "1":
        raise DataAvailabilityError(f"Falta {name} en el bundle público.")
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
        raise DataAvailabilityError(f"No se pudo reconstruir {name}. Revisá los datos de desarrollo.") from exc
    if not local_path.exists():
        raise DataAvailabilityError(f"Falta {name}. Generá o instalá el bundle público.")
    return local_path


@st.cache_data(show_spinner=False)
def load_profiles() -> pd.DataFrame:
    return _read_parquet("perfiles_territoriales.parquet")


@st.cache_data(show_spinner=False)
def load_signals() -> pd.DataFrame:
    return _read_parquet("senales_prioritarias_perfiles.parquet")


@st.cache_data(show_spinner=False)
def load_pairs() -> pd.DataFrame:
    return _read_parquet("pares_comparables.parquet")


@st.cache_data(show_spinner=False)
def load_gaps() -> pd.DataFrame:
    return _read_parquet("brechas_entre_pares.parquet")


@st.cache_data(show_spinner=False)
def load_history() -> pd.DataFrame:
    from src.analysis.ra_historico import build_indicators
    try:
        return build_indicators(_read_parquet("ra_2011_2025_long.parquet"))
    except DataAvailabilityError:
        raise
    except Exception as exc:
        raise DataAvailabilityError("No se pudo preparar la serie histórica del bundle público.") from exc


@st.cache_data(show_spinner=False)
def load_national_history() -> pd.DataFrame:
    from src.analysis.ra_historico import national_counts
    try:
        return national_counts(_read_parquet("ra_2011_2025_long.parquet"))
    except DataAvailabilityError:
        raise
    except Exception as exc:
        raise DataAvailabilityError("No se pudo preparar el agregado nacional histórico.") from exc


def _read_parquet(name: str) -> pd.DataFrame:
    try:
        return pd.read_parquet(artifact_path(name))
    except DataAvailabilityError:
        raise
    except Exception as exc:
        raise DataAvailabilityError(f"No se pudo leer {name}; verificá el bundle público.") from exc
