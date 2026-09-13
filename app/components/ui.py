"""Sistema visual pequeño y helpers de presentación sin lógica analítica."""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def load_styles() -> None:
    st.markdown(f"<style>{(ASSETS / 'styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def coverage_text(value: object) -> str:
    if pd.isna(value):
        return "Sin información de cobertura"
    labels = {"completo": "Datos completos", "parcial": "Cobertura parcial", "ausente": "Sin dato"}
    return labels.get(str(value).lower(), str(value))


def profile_sentence(signals: pd.DataFrame) -> str:
    dimensions = list(dict.fromkeys(signals.get("dimension", pd.Series(dtype=str)).dropna().astype(str)))[:3]
    if not dimensions:
        return "No hay señales prioritarias activadas con los datos disponibles."
    if len(dimensions) == 1:
        joined = dimensions[0].lower()
    else:
        joined = ", ".join(d.lower() for d in dimensions[:-1]) + f" y {dimensions[-1].lower()}"
    return f"Este territorio presenta señales para mirar en {joined}."


def metric_grid(items: Iterable[tuple[str, str, str]]) -> None:
    cards = "".join(
        f'<div class="metric-item"><div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div><div class="metric-meta">{escape(meta)}</div></div>'
        for label, value, meta in items
    )
    st.markdown(f'<div class="metric-grid">{cards}</div>', unsafe_allow_html=True)


def signal_card(dimension: object, signal: object, evidence: object, confidence: object) -> None:
    st.markdown(
        '<div class="signal-card">'
        f'<div class="signal-dimension">{escape(str(dimension))}</div><div>'
        f'<div class="signal-title">{escape(str(signal))}</div>'
        f'<div class="signal-meta">{escape(str(evidence))} · Confianza {escape(str(confidence).lower())}</div>'
        '</div></div>', unsafe_allow_html=True,
    )


def method_note(text: str) -> None:
    st.markdown(f'<div class="method-note">{escape(text)}</div>', unsafe_allow_html=True)
