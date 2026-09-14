"""Selección territorial persistente y sincronizada con el mapa."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def territory_options(profiles: pd.DataFrame, province: str) -> pd.DataFrame:
    return profiles.loc[profiles.provincia_nombre.eq(province)].sort_values("departamento_nombre")


def queue_territory(territory_id: str) -> None:
    st.session_state.pending_territory_id = str(territory_id)


def queue_navigation(section: str) -> None:
    """Agenda navegación para consumirla antes de crear su widget."""
    st.session_state.pending_nav_section = section


def queue_explore_scale(scale: str) -> None:
    st.session_state.pending_explore_scale = scale


def apply_pending_explore_scale(valid_scales: list[str]) -> str | None:
    pending = st.session_state.pop("pending_explore_scale", None)
    if pending in valid_scales:
        st.session_state.explore_scale = pending
        return pending
    return None


def consume_pending_navigation(state: dict, valid_sections: list[str]) -> str | None:
    """Consume una transición diferida sin tocar el widget en el rerun de origen."""
    pending = state.pop("pending_nav_section", None)
    if pending in valid_sections:
        state["nav_section"] = pending
        return pending
    return None


def apply_pending_navigation(valid_sections: list[str]) -> str | None:
    return consume_pending_navigation(st.session_state, valid_sections)


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
    selected = container.selectbox(
        "Departamento o unidad equivalente",
        ids,
        format_func=lambda value: labels.get(value, str(value)),
        key=territory_key,
    )
    st.session_state.territory_id = selected
    return selected
