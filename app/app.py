"""Orquestador de la experiencia Streamlit de La escuela que te toca."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.components.comparables import render_comparables
from app.components.data import DataAvailabilityError, load_gaps, load_history, load_pairs, load_profiles, load_signals
from app.components.historia import render_history
from app.components.mapa import render_map
from app.components.metodologia import render_methodology
from app.components.perfil import profile_row, render_profile
from app.components.senales import render_signals
from app.components.territorio import apply_pending_territory, render_selector
from app.components.ui import load_styles, method_note

SECTIONS = ["Inicio", "Perfil territorial", "Historia", "Comparables", "Dónde mirar", "Metodología"]


def _navigate(section: str) -> None:
    st.session_state.nav_section = section


def render_home(profiles) -> None:
    st.markdown('<div class="eyebrow">Datos abiertos · Argentina</div>', unsafe_allow_html=True)
    st.title("La escuela que te toca")
    st.markdown('<p class="lede">Una mirada territorial a las desigualdades educativas de la Argentina.</p>', unsafe_allow_html=True)
    st.write("Elegí un territorio para explorar su trayectoria, contexto y aprendizaje, y compararlo con lugares de condiciones similares.")
    st.markdown('<div class="journey">Detectar → Entender → Contextualizar → Comparar → Investigar</div>', unsafe_allow_html=True)
    territory_id = st.session_state.territory_id
    row = profile_row(profiles, territory_id)
    st.markdown(f"### Territorio seleccionado: {row.departamento_nombre}")
    st.caption(f"{row.provincia_nombre} · Cobertura documental: {row.calidad_total_del_perfil}. No mide calidad educativa.")
    st.button("Explorar territorio", type="primary", on_click=_navigate, args=("Perfil territorial",))
    render_map(profiles, territory_id)
    method_note("No se construyen scores ni rankings. Cada dimensión conserva su fuente, año, cobertura y limitaciones.")


def main() -> None:
    st.set_page_config(page_title="La escuela que te toca", page_icon="▰", layout="wide")
    load_styles()
    try:
        profiles = load_profiles()
        signals = load_signals()
    except DataAvailabilityError as exc:
        st.error(str(exc))
        st.stop()
    if "territory_id" not in st.session_state:
        st.session_state.territory_id = profiles.sort_values(["provincia_nombre", "departamento_nombre"]).iloc[0].departamento_id
    if "nav_section" not in st.session_state:
        st.session_state.nav_section = "Inicio"
    apply_pending_territory(profiles)

    st.sidebar.markdown('<div class="eyebrow">La escuela que te toca</div>', unsafe_allow_html=True)
    render_selector(profiles)
    section = st.sidebar.radio("Recorrido", SECTIONS, key="nav_section")
    st.sidebar.caption("Datos abiertos oficiales · Lectura exploratoria, no causal")

    try:
        if section == "Inicio":
            render_home(profiles)
        elif section == "Perfil territorial":
            render_profile(profiles, signals, st.session_state.territory_id)
        elif section == "Historia":
            render_history(profiles, load_history(), st.session_state.territory_id)
        elif section == "Comparables":
            render_comparables(profiles, load_pairs(), load_gaps(), st.session_state.territory_id)
        elif section == "Dónde mirar":
            render_signals(signals)
        elif section == "Metodología":
            render_methodology()
    except DataAvailabilityError as exc:
        st.error(str(exc))


if __name__ == "__main__":
    main()
