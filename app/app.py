"""Orquestador del MVP Streamlit de La escuela que te toca."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.components.comparables import render_comparables
from app.components.data import (
    DataAvailabilityError,
    load_gaps,
    load_history,
    load_pairs,
    load_profiles,
    load_signals,
)
from app.components.historia import render_history
from app.components.metodologia import render_methodology
from app.components.perfil import profile_row, render_profile
from app.components.senales import render_signals
from app.components.territorio import render_selector

SECTIONS = ["Inicio", "Perfil territorial", "Historia", "Comparables", "Dónde mirar", "Metodología"]


def _navigate(section: str) -> None:
    st.session_state.nav_section = section


def _style() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 4rem;}
        h1, h2, h3 {letter-spacing: -0.02em;}
        [data-testid="stMetric"] {background: #f5f3ef; padding: .8rem; border-radius: .35rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home(profiles) -> None:
    st.title("La escuela que te toca")
    st.subheader("Una mirada territorial a las desigualdades educativas de la Argentina.")
    st.write(
        "La app integra datos públicos de educación, territorio y contexto para ayudar a detectar diferencias, "
        "compararlas con territorios semejantes y formular preguntas de investigación."
    )
    st.markdown("**Detectar → Entender → Contextualizar → Comparar → Investigar**")
    st.divider()
    territory_id = st.session_state.territory_id
    row = profile_row(profiles, territory_id)
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"### {row.departamento_nombre}")
        st.write(row.provincia_nombre)
        st.caption(f"Cobertura documental: {row.calidad_total_del_perfil}. No mide calidad educativa.")
    with cols[1]:
        st.button("Explorar territorio", type="primary", width="stretch", on_click=_navigate, args=("Perfil territorial",))
    st.info("Este MVP no ofrece un score ni un ranking. Cada dimensión conserva su fuente, año y limitación.")
    st.caption("El mapa territorial interactivo queda preparado para una iteración posterior; en este MVP se prioriza una selección accesible y estable.")


def main() -> None:
    st.set_page_config(page_title="La escuela que te toca", layout="wide")
    _style()
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

    st.sidebar.title("La escuela que te toca")
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
        else:
            render_methodology()
    except DataAvailabilityError as exc:
        st.error(str(exc))
    except (KeyError, ValueError) as exc:
        st.error("No pudimos presentar esta vista con los datos disponibles. Probá otro territorio o revisá los pipelines procesados.")


if __name__ == "__main__":
    main()
