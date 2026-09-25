"""Vista previa compacta del territorio seleccionado en un mapa."""
from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from app.components.territorio import queue_explore_scale, queue_navigation
from app.components.ui import readable_evidence


def territory_preview_data(profiles: pd.DataFrame, signals: pd.DataFrame, territory_id: str) -> dict[str, object]:
    rows = profiles.loc[profiles.departamento_id.astype(str).eq(str(territory_id))]
    if rows.empty:
        raise ValueError(f"Territorio inexistente: {territory_id}")
    row = rows.iloc[0]
    selected = signals.loc[signals.departamento_id.astype(str).eq(str(territory_id))].sort_values("prioridad").head(2)
    return {
        "territorio": row.departamento_nombre,
        "provincia": row.provincia_nombre,
        "cobertura": row.calidad_total_del_perfil,
        "cantidad_senales": int(signals.departamento_id.astype(str).eq(str(territory_id)).sum()),
        "senales": selected[["tipo_senal", "dimension", "senal", "evidencia"]].to_dict("records"),
    }


def _open_profile() -> None:
    queue_explore_scale("territorio")
    queue_navigation("Explorar")


def signal_count_text(count: int) -> str:
    if count == 0:
        return (
            "No se activan señales prioritarias con los criterios actuales. "
            "Esto no implica ausencia de problemas."
        )
    return f"{count} señal para mirar" if count == 1 else f"{count} señales para mirar"


def territory_preview(profiles: pd.DataFrame, signals: pd.DataFrame, territory_id: str, key: str) -> None:
    preview = territory_preview_data(profiles, signals, territory_id)
    count_text = signal_count_text(int(preview["cantidad_senales"]))
    details = "".join(
        f'<div class="preview-signal"><span>{escape(str(item["tipo_senal"]))} · {escape(str(item["dimension"]))}</span>'
        f'<strong>{escape(str(item["senal"]))}</strong>'
        f'<small>{escape(readable_evidence(item["evidencia"], item["senal"]))}</small></div>'
        for item in preview["senales"]
    )
    with st.container(key=f"territory_preview_{key}"):
        st.markdown(
            f'<section class="territory-preview"><div class="eyebrow">Territorio</div>'
            f'<h3>{escape(str(preview["territorio"]))}</h3><p class="preview-province">{escape(str(preview["provincia"]))}</p>'
            f'<div class="preview-summary"><p><span>Cobertura documental</span>'
            f'<strong>{escape(str(preview["cobertura"]))}</strong></p>'
            f'<p class="preview-count">{escape(count_text)}</p></div>{details}</section>',
            unsafe_allow_html=True,
        )
        st.button(
            "Ver ficha territorial →",
            key=f"preview_open_{key}_{territory_id}",
            type="primary",
            on_click=_open_profile,
        )
