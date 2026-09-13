"""Selección territorial persistente."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def territory_options(profiles: pd.DataFrame, province: str) -> pd.DataFrame:
    return profiles.loc[profiles.provincia_nombre.eq(province)].sort_values("departamento_nombre")


def render_selector(profiles: pd.DataFrame, location: str = "sidebar") -> str:
    container = st.sidebar if location == "sidebar" else st
    provinces = sorted(profiles.provincia_nombre.dropna().unique())
    current_id = st.session_state.get("territory_id")
    current = profiles.loc[profiles.departamento_id.eq(current_id)]
    default_province = current.iloc[0].provincia_nombre if not current.empty else provinces[0]
    province = container.selectbox("Provincia", provinces, index=provinces.index(default_province), key=f"province_{location}")
    available = territory_options(profiles, province)
    ids = available.departamento_id.tolist()
    default_id = current_id if current_id in ids else ids[0]
    labels = available.set_index("departamento_id").departamento_nombre.to_dict()
    selected = container.selectbox(
        "Departamento o unidad equivalente", ids, index=ids.index(default_id),
        format_func=lambda value: labels[value], key=f"territory_{location}",
    )
    st.session_state["territory_id"] = selected
    return selected
