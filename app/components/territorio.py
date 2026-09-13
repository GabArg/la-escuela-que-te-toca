"""Selección territorial persistente y sincronizada con el mapa."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def territory_options(profiles: pd.DataFrame, province: str) -> pd.DataFrame:
    return profiles.loc[profiles.provincia_nombre.eq(province)].sort_values("departamento_nombre")


def queue_territory(territory_id: str) -> None:
    st.session_state.pending_territory_id = str(territory_id)


def apply_pending_territory(profiles: pd.DataFrame) -> str:
    pending = st.session_state.pop("pending_territory_id", None)
    valid = set(profiles.departamento_id.astype(str))
    if pending is not None and str(pending) in valid:
        row = profiles.loc[profiles.departamento_id.astype(str).eq(str(pending))].iloc[0]
        st.session_state.territory_id = str(pending)
        st.session_state.province_sidebar = row.provincia_nombre
        st.session_state.territory_sidebar = str(pending)
    return str(st.session_state.get("territory_id", ""))


def render_selector(profiles: pd.DataFrame, location: str = "sidebar") -> str:
    container = st.sidebar if location == "sidebar" else st
    provinces = sorted(profiles.provincia_nombre.dropna().unique())
    current_id = str(st.session_state.get("territory_id", ""))
    current = profiles.loc[profiles.departamento_id.astype(str).eq(current_id)]
    default_province = current.iloc[0].provincia_nombre if not current.empty else provinces[0]
    province_key = f"province_{location}"
    territory_key = f"territory_{location}"
    if st.session_state.get(province_key) not in provinces:
        st.session_state[province_key] = default_province
    province = container.selectbox("Provincia", provinces, key=province_key)
    available = territory_options(profiles, province)
    ids = available.departamento_id.astype(str).tolist()
    if st.session_state.get(territory_key) not in ids:
        st.session_state[territory_key] = current_id if current_id in ids else ids[0]
    labels = available.assign(departamento_id=available.departamento_id.astype(str)).set_index("departamento_id").departamento_nombre.to_dict()
    selected = container.selectbox("Departamento o unidad equivalente", ids, format_func=lambda value: labels[value], key=territory_key)
    st.session_state.territory_id = selected
    return selected
