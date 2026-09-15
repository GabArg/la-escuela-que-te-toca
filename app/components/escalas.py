"""Portada y entradas por escala territorial."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.mapa import MAP_VARIABLES, render_map
from app.components.preview import territory_preview
from app.components.territorio import queue_explore_scale, queue_navigation
from app.components.ui import method_note


def _go(scale: str) -> None:
    queue_explore_scale(scale)
    queue_navigation("Explorar")


def render_breadcrumb(province: str | None = None, territory: str | None = None) -> None:
    labels = [("Argentina", "argentina")]
    if province:
        labels.append((province, "provincia"))
    if territory:
        labels.append((territory, "territorio"))
    columns = st.columns([max(1, len(label)) for label, _ in labels] + [12])
    for column, (label, scale) in zip(columns, labels):
        column.button(label, key=f"crumb_{scale}_{province}_{territory}", on_click=_go, args=(scale,))


def render_home() -> None:
    st.markdown('<div class="hero"><div class="eyebrow">Datos abiertos · Argentina</div>', unsafe_allow_html=True)
    st.title("La escuela que te toca")
    st.markdown(
        '<p class="hero-deck">Una lectura territorial de la educación argentina: '
        'qué señales aparecen, cómo evolucionaron y con qué lugares tiene sentido compararlas.</p>'
        '<p class="hero-tagline">Comparar mejor, para preguntar mejor.</p></div>',
        unsafe_allow_html=True,
    )
    st.subheader("¿Desde dónde querés mirar la educación?")
    st.markdown(
        '<div class="scale-list">'
        '<div><span>01</span><strong>Argentina</strong><p>Ver el panorama territorial y abrir una provincia.</p></div>'
        '<div><span>02</span><strong>Provincia</strong><p>Explorar diferencias internas sin construir rankings.</p></div>'
        '<div><span>03</span><strong>Territorio</strong><p>Entender su historia, contexto y comparables.</p></div>'
        '</div>', unsafe_allow_html=True,
    )
    cols = st.columns(3)
    cols[0].button("Mirar Argentina", type="primary", on_click=_go, args=("argentina",), use_container_width=True)
    cols[1].button("Abrir provincia", on_click=_go, args=("provincia",), use_container_width=True)
    cols[2].button("Buscar territorio", on_click=_go, args=("territorio",), use_container_width=True)
    st.caption("También podés elegir provincia y territorio desde la barra lateral.")


def _signal_summary(signals: pd.DataFrame, province: str | None = None) -> None:
    data = signals if province is None else signals[signals.provincia_nombre.eq(province)]
    counts = data.groupby("dimension", observed=True).size().sort_index()
    if counts.empty:
        st.write("No hay señales identificables para esta selección.")
        return
    st.markdown("#### Señales que orientan la investigación")
    st.caption("Cantidad de señales auditadas por dimensión. No expresa gravedad ni calidad.")
    figure = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h", marker_color="#18324a",
        text=counts.values, textposition="outside",
    ))
    figure.update_layout(height=max(230, len(counts) * 46), margin=dict(l=10, r=40, t=10, b=20),
                         xaxis_title="Señales existentes", plot_bgcolor="rgba(0,0,0,0)",
                         paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(figure, use_container_width=True)


def _map_with_preview(
    profiles: pd.DataFrame,
    signals: pd.DataFrame,
    selected_id: str,
    key: str,
) -> None:
    if key in {"argentina", "provincia"}:
        with st.container(key=f"{key}_workspace"):
            map_column, preview_column = st.columns([7, 3], gap="medium")
            with map_column:
                with st.container(key=f"{key}_map_panel"):
                    st.markdown('<div class="workspace-module-label">Exploración territorial</div>', unsafe_allow_html=True)
                    render_map(profiles, selected_id, key=f"map_{key}", height=405 if key == "argentina" else 430)
            with preview_column:
                territory_preview(profiles, signals, selected_id, key=key)
        return

    map_column, preview_column = st.columns([7, 3], gap="large")
    with map_column:
        render_map(profiles, selected_id, key=f"map_{key}")
    with preview_column:
        territory_preview(profiles, signals, selected_id, key=key)


def render_argentina(profiles: pd.DataFrame, signals: pd.DataFrame, selected_id: str) -> None:
    render_breadcrumb()
    with st.container(key="argentina_header"):
        st.markdown('<div class="eyebrow">Escala nacional</div>', unsafe_allow_html=True)
        st.title("Argentina")
        st.markdown('<p class="lede">¿Dónde aparecen diferencias territoriales que merecen una segunda mirada?</p>', unsafe_allow_html=True)
    _map_with_preview(profiles, signals, selected_id, key="argentina")
    with st.container(key="argentina_analysis"):
        signals_column, note_column = st.columns([7, 3], gap="medium")
        with signals_column:
            with st.container(key="argentina_signals"):
                st.markdown('<div class="workspace-module-label">Señales</div>', unsafe_allow_html=True)
                _signal_summary(signals)
        with note_column:
            with st.container(key="argentina_method"):
                st.markdown('<div class="workspace-module-label">Lectura</div>', unsafe_allow_html=True)
                method_note("El mapa permite detectar diferencias, no ordenar territorios. Seleccioná distintas unidades y abrí una ficha cuando quieras profundizar.")


def render_province(profiles: pd.DataFrame, signals: pd.DataFrame, province: str, selected_id: str) -> None:
    subset = profiles[profiles.provincia_nombre.eq(province)]
    with st.container(key="provincia_header"):
        st.markdown('<div class="eyebrow">Escala provincial</div>', unsafe_allow_html=True)
        st.title(province)
        st.markdown('<p class="lede">¿Qué diferencias aparecen dentro de esta provincia?</p>', unsafe_allow_html=True)
    _map_with_preview(subset, signals, selected_id, key="provincia")
    st.caption(f"{len(subset)} departamentos o unidades territoriales equivalentes según GeoRef.")
    with st.container(key="provincia_signals"):
        st.markdown('<div class="workspace-module-label">Señales</div>', unsafe_allow_html=True)
        _signal_summary(signals, province)
    render_breadcrumb(province)
