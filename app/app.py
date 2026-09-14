"""Recorrido editorial de La escuela que te toca."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
# Streamlit ejecuta este archivo con ``app/`` al comienzo de ``sys.path``.
# Sin priorizar la raíz, ``import app`` puede resolver a ``app/app.py`` en vez
# del paquete ``app``. La ruta se deriva de este archivo y funciona igual en
# desarrollo local y en el checkout de Streamlit Community Cloud.
root_path = str(ROOT)
if root_path in sys.path:
    sys.path.remove(root_path)
sys.path.insert(0, root_path)

from app.components.comparables import render_comparables
from app.components.data import DataAvailabilityError, load_gaps, load_history, load_pairs, load_profiles, load_signals
from app.components.escalas import render_argentina, render_province
from app.components.metodologia import render_methodology
from app.components.perfil import render_profile
from app.components.senales import render_signals
from app.components.storytelling import render_storytelling_home
from app.components.territorio import (
    apply_pending_explore_scale,
    apply_pending_navigation,
    apply_pending_territory,
    queue_explore_scale,
    queue_navigation,
    render_selector,
)
from app.components.ui import load_styles

SECTIONS = ["Explorar", "Comparar", "Investigar", "Metodología"]
EXPLORE_SCALES = ["home", "argentina", "provincia", "territorio"]


def _open_territory() -> None:
    queue_explore_scale("territorio")
    queue_navigation("Explorar")


def render_main_navigation() -> str:
    selected = st.radio(
        "Recorrido principal", SECTIONS, key="nav_section",
        label_visibility="collapsed", horizontal=True,
    )
    return selected or "Explorar"


def main() -> None:
    st.set_page_config(page_title="La escuela que te toca", page_icon="▰", layout="wide")
    load_styles()
    try:
        profiles, signals = load_profiles(), load_signals()
    except DataAvailabilityError as exc:
        st.error(str(exc)); st.stop()
    if "territory_id" not in st.session_state:
        st.session_state.territory_id = profiles.sort_values(["provincia_nombre", "departamento_nombre"]).iloc[0].departamento_id
    apply_pending_navigation(SECTIONS)
    apply_pending_explore_scale(EXPLORE_SCALES)
    if st.session_state.get("nav_section") not in SECTIONS:
        st.session_state.nav_section = "Explorar"
    if st.session_state.get("explore_scale") not in EXPLORE_SCALES:
        st.session_state.explore_scale = "home"
    apply_pending_territory(profiles)

    is_story_home = (
        st.session_state.get("nav_section") == "Explorar"
        and st.session_state.get("explore_scale") == "home"
    )
    if is_story_home:
        st.markdown(
            '<style data-story-shell>'
            '[data-testid="stSidebar"], [data-testid="collapsedControl"], header[data-testid="stHeader"] {display:none !important;}'
            '[data-testid="stAppViewContainer"] {overflow-x:clip;}'
            '.block-container {max-width:min(1540px, 96vw) !important; padding-top:0 !important;}'
            '</style>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown('<div class="brand-lockup"><span>LA ESCUELA</span><strong>que te toca</strong></div>', unsafe_allow_html=True)
    territory_id = render_selector(profiles)
    current = profiles.loc[profiles.departamento_id.eq(territory_id)].iloc[0]
    st.sidebar.button("Abrir ficha territorial", type="primary", on_click=_open_territory, use_container_width=True)
    st.sidebar.caption("Datos abiertos oficiales · Sin rankings · Lectura no causal")

    section = "Explorar" if is_story_home else render_main_navigation()
    try:
        if section == "Explorar":
            scale = st.session_state.explore_scale
            if scale == "home":
                render_storytelling_home(profiles, load_pairs(), load_gaps(), load_history())
            elif scale == "argentina":
                render_argentina(profiles, signals, territory_id)
            elif scale == "provincia":
                render_province(profiles, signals, current.provincia_nombre, territory_id)
            else:
                render_profile(profiles, signals, territory_id, history=load_history(), show_breadcrumb=True)
        elif section == "Comparar":
            render_comparables(profiles, load_pairs(), load_gaps(), territory_id)
        elif section == "Investigar":
            render_signals(signals, current.provincia_nombre)
        else:
            render_methodology()
    except DataAvailabilityError as exc:
        st.error(str(exc))
    except (KeyError, ValueError) as exc:
        st.error("No pudimos presentar esta vista con los datos disponibles. Elegí otro territorio o revisá el bundle público.")


if __name__ == "__main__":
    main()
