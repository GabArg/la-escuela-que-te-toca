"""Explorador no ordinal de señales auditadas."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.ui import signal_card


def _open_profile(territory_id: str, province: str) -> None:
    st.session_state.territory_id = territory_id
    st.session_state.province_sidebar = province
    st.session_state.territory_sidebar = territory_id
    st.session_state.nav_section = "Perfil territorial"


def filter_signals(signals: pd.DataFrame, province: str | None = None, dimension: str | None = None, signal_type: str | None = None) -> pd.DataFrame:
    result = signals.copy()
    if province and province != "Todas": result = result[result.provincia_nombre.eq(province)]
    if dimension and dimension != "Todas": result = result[result.dimension.eq(dimension)]
    if signal_type and signal_type != "Todas": result = result[result.senal.eq(signal_type)]
    return result.sort_values(["provincia_nombre", "departamento_nombre", "dimension"])


def render_signals(signals: pd.DataFrame) -> None:
    st.title("Dónde mirar")
    st.write("Señales para orientar la mirada investigativa. No están ordenadas por gravedad y no forman un score.")
    cols = st.columns(3)
    province = cols[0].selectbox("Provincia", ["Todas", *sorted(signals.provincia_nombre.unique())], key="signals_province")
    dimension = cols[1].selectbox("Dimensión", ["Todas", *sorted(signals.dimension.unique())], key="signals_dimension")
    signal_type = cols[2].selectbox("Tipo de señal", ["Todas", *sorted(signals.senal.unique())], key="signals_type")
    filtered = filter_signals(signals, province, dimension, signal_type)
    if filtered.empty:
        st.info("No hay señales para esta combinación de filtros.")
        return
    st.caption(f"{len(filtered)} señales visibles, en orden alfabético territorial; no es un orden de gravedad.")
    options = filtered.drop_duplicates("departamento_id").set_index("departamento_id").apply(lambda r: f"{r.departamento_nombre} · {r.provincia_nombre}", axis=1).to_dict()
    selected = st.selectbox("Abrir un perfil", list(options), format_func=lambda value: options[value])
    selected_row = filtered.loc[filtered.departamento_id.eq(selected)].iloc[0]
    st.button("Ver perfil territorial", on_click=_open_profile, args=(selected, selected_row.provincia_nombre))
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    for _, row in filtered.head(40).iterrows():
        st.markdown(f'<div class="signal-territory">{row.departamento_nombre}, {row.provincia_nombre}</div>', unsafe_allow_html=True)
        signal_card(row.dimension, row.senal, row.evidencia, row.nivel_confianza)
    if len(filtered) > 40:
        st.caption("Se muestran las primeras 40 coincidencias para mantener una lectura clara. Ajustá los filtros para acotar.")
