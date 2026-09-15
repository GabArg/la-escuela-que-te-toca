"""Explorador no ordinal de señales auditadas."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.territorio import queue_explore_scale, queue_navigation, queue_territory
from app.components.ui import signal_card


def _open_profile(territory_id: str, province: str) -> None:
    queue_territory(territory_id)
    queue_explore_scale("territorio")
    queue_navigation("Explorar")


def filter_signals(signals: pd.DataFrame, province: str | None = None, dimension: str | None = None, signal_type: str | None = None) -> pd.DataFrame:
    result = signals.copy()
    if province and province != "Todas": result = result[result.provincia_nombre.eq(province)]
    if dimension and dimension != "Todas": result = result[result.dimension.eq(dimension)]
    if signal_type and signal_type != "Todas": result = result[result.senal.eq(signal_type)]
    return result.sort_values(["provincia_nombre", "departamento_nombre", "dimension"])


def render_signals(signals: pd.DataFrame, selected_province: str) -> None:
    st.markdown('<span class="functional-view-marker functional-view--research" aria-hidden="true"></span>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Investigar</div>', unsafe_allow_html=True)
    st.title("Radar territorial de investigación")
    st.markdown('<p class="lede">Señales para decidir dónde hacer una segunda pregunta, no para ordenar territorios.</p>', unsafe_allow_html=True)
    st.subheader("¿Qué querés investigar?")
    dimensions = sorted(signals.dimension.dropna().unique())
    dimension = st.radio("Dimensión", dimensions, horizontal=True, key="radar_dimension")
    scope_options = ["Toda Argentina", selected_province]
    if st.session_state.get("radar_scope") not in scope_options:
        st.session_state.radar_scope = "Toda Argentina"
    scope = st.radio(
        "Ámbito territorial",
        scope_options,
        horizontal=True,
        key="radar_scope",
    )
    province = None if scope == "Toda Argentina" else selected_province
    filtered = filter_signals(signals, province, dimension)
    if filtered.empty:
        st.info("No hay señales para esta combinación de filtros.")
        return
    st.caption(f"{len(filtered)} señales visibles, en orden alfabético territorial; no es un orden de gravedad.")
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    for index, row in filtered.head(40).iterrows():
        st.markdown(f'<div class="signal-territory">{row.departamento_nombre}, {row.provincia_nombre}</div>', unsafe_allow_html=True)
        signal_card(row.dimension, row.senal, row.evidencia, row.nivel_confianza)
        st.button(
            "Ver territorio",
            key=f"signal_open_{row.departamento_id}_{index}",
            on_click=_open_profile,
            args=(row.departamento_id, row.provincia_nombre),
        )
    if len(filtered) > 40:
        st.caption("Se muestran las primeras 40 coincidencias para mantener una lectura clara. Ajustá los filtros para acotar.")
