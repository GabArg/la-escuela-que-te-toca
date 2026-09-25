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
    if signals.empty:
        return "No hay señales prioritarias activadas con los datos disponibles."
    educational = signals.loc[
        signals.get("tipo_senal", pd.Series(index=signals.index, dtype=str)).eq("Señal educativa"),
        "dimension",
    ].dropna().astype(str).drop_duplicates().tolist()
    documentary = signals.get("tipo_senal", pd.Series(index=signals.index, dtype=str)).eq(
        "Advertencia de cobertura / calidad documental"
    ).any()
    parts = []
    if educational:
        joined = educational[0].lower() if len(educational) == 1 else ", ".join(
            item.lower() for item in educational[:-1]
        ) + f" y {educational[-1].lower()}"
        parts.append(f"señales educativas para mirar en {joined}")
    if documentary:
        parts.append("advertencias de cobertura o calidad documental")
    return "Este territorio presenta " + " y ".join(parts) + "."


QUARTILE_SIGNAL_LABELS = {
    "Asistencia 15–17 relativamente baja": ("Asistencia 15–17", "%"),
    "Baja oferta relativa de localizaciones": (
        "Localizaciones por cada 1.000 personas en edad escolar",
        "",
    ),
    "Rancho/casilla relativamente alto": ("Rancho/casilla", "%"),
}


def _number_text(value: object) -> str:
    return f"{float(value):.1f}".replace(".", ",")


def _quartile_evidence(text: str, signal: object | None) -> str | None:
    fields = {}
    for piece in text.split(";"):
        key, separator, raw_value = piece.strip().partition("=")
        if separator:
            fields[key] = raw_value.strip()
    threshold_key = next((key for key in ("umbral_P25", "umbral_P75") if key in fields), None)
    if "valor" not in fields or threshold_key is None:
        return None
    try:
        observed = _number_text(fields["valor"])
        threshold = _number_text(fields[threshold_key])
    except (TypeError, ValueError):
        return None
    label, suffix = QUARTILE_SIGNAL_LABELS.get(str(signal), ("Valor territorial", ""))
    direction = "más bajos" if threshold_key == "umbral_P25" else "más altos"
    return (
        f"{label}: {observed}{suffix}\n"
        f"Referencia: el umbral del 25% de territorios con valores {direction} es {threshold}{suffix}"
    )


def readable_evidence(value: object, signal: object | None = None) -> str:
    text = str(value)
    if text == "lengua=completo; matematica=parcial":
        return "Lengua: datos completos · Matemática: cobertura parcial"
    if text == "lengua=parcial; matematica=parcial":
        return "Lengua y Matemática: cobertura parcial"
    quartile_text = _quartile_evidence(text, signal)
    if quartile_text is not None:
        return quartile_text
    replacements = {
        "valor=": "valor ",
        "clasificacion=": "patrón ",
        "indicadores=proporcion_repitentes": "indicador: repitencia",
        "indicadores=proporcion_sobreedad": "indicador: sobreedad",
        "indicadores=proporcion_salidos_sin_pase": "indicador: salidos sin pase",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    pieces = []
    for piece in text.split(";"):
        words = piece.strip().split()
        if words:
            try:
                words[-1] = _number_text(words[-1])
            except ValueError:
                pass
        pieces.append(" ".join(words))
    return " · ".join(pieces)


def metric_grid(items: Iterable[tuple[str, str, str]]) -> None:
    cards = "".join(
        f'<div class="metric-item"><div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div><div class="metric-meta">{escape(meta)}</div></div>'
        for label, value, meta in items
    )
    st.markdown(f'<div class="metric-grid">{cards}</div>', unsafe_allow_html=True)


def signal_card(
    dimension: object,
    signal: object,
    evidence: object,
    confidence: object,
    signal_type: object | None = None,
) -> None:
    dim_slug = str(dimension).lower().replace(" ", "-")
    conf_slug = str(confidence).lower()
    conf_class = "confidence-media" if conf_slug == "media" else ""
    st.markdown(
        f'<div class="signal-card signal-dim-{escape(dim_slug)} {conf_class}">'
        f'<div class="signal-dimension">{escape(str(dimension))}</div><div>'
        + (f'<div class="signal-kind">{escape(str(signal_type))}</div>' if signal_type else '') +
        f'<div class="signal-title">{escape(str(signal))}'
        f'<span class="confidence-chip">Confianza de la evidencia: {escape(conf_slug)}</span></div>'
        f'<div class="signal-meta">{escape(readable_evidence(evidence, signal))}</div>'
        '</div></div>', unsafe_allow_html=True,
    )


def method_note(text: str) -> None:
    st.markdown(f'<div class="method-note">{escape(text)}</div>', unsafe_allow_html=True)
