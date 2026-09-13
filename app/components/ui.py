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


def readable_evidence(value: object) -> str:
    text = str(value)
    if text == "lengua=completo; matematica=parcial":
        return "Lengua: datos completos · Matemática: cobertura parcial"
    if text == "lengua=parcial; matematica=parcial":
        return "Lengua y Matemática: cobertura parcial"
    replacements = {
        "umbral_P25=": "primer cuartil nacional ",
        "umbral_P75=": "tercer cuartil nacional ",
        "valor=": "valor ",
        "clasificacion=": "patrón ",
        "indicadores=proporcion_repitentes": "indicador: repitencia",
        "indicadores=proporcion_sobreedad": "indicador: sobreedad",
        "indicadores=proporcion_salidos_sin_pase": "indicador: salidos sin pase",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.replace(";", " · ")


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
        f'<div class="signal-meta">{escape(readable_evidence(evidence))} · Confianza {escape(str(confidence).lower())}</div>'
        '</div></div>', unsafe_allow_html=True,
    )


def method_note(text: str) -> None:
    st.markdown(f'<div class="method-note">{escape(text)}</div>', unsafe_allow_html=True)
