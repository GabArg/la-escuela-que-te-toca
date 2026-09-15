"""Presentación del motor de pares y contraste posterior."""
from __future__ import annotations

from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.perfil import format_value, profile_row
from app.components.ui import metric_grid, method_note

RESULT_LABELS = {
    "brecha_asistencia_15_17_pp": "Asistencia 15–17",
    "brecha_sobreedad_pp": "Sobreedad",
    "brecha_repeticion_pp": "Repetición",
    "brecha_salidos_sin_pase_pp": "Salidos sin pase",
    "brecha_lengua_satisfactorio_avanzado_pp": "Lengua: satisfactorio + avanzado",
    "brecha_matematica_satisfactorio_avanzado_pp": "Matemática: satisfactorio + avanzado",
}


def peer_rows(pairs: pd.DataFrame, territory_id: str, comparison_type: str = "nacional", limit: int = 5) -> pd.DataFrame:
    return pairs.loc[pairs.departamento_id.eq(territory_id) & pairs.tipo_comparacion.eq(comparison_type)].sort_values("ranking_similitud_interno").head(limit)


def comparison_payload(gaps: pd.DataFrame, territory_id: str, peer_id: str, comparison_type: str = "nacional") -> dict[str, object] | None:
    rows = gaps.loc[gaps.departamento_id.eq(territory_id) & gaps.par_departamento_id.eq(peer_id) & gaps.tipo_comparacion.eq(comparison_type)]
    if rows.empty:
        return None
    row = rows.iloc[0]
    return {
        "similares": str(row.variables_mas_similares).split(";"),
        "diferencias": str(row.principales_diferencias).split(";"),
        "distancia": row.distancia,
        "calidad": row.calidad_comparacion,
        "estabilidad": row.estabilidad_origen,
        "brechas": {label: row[column] for column, label in RESULT_LABELS.items()},
    }


def _readable(variable: str) -> str:
    labels = {
        "poblacion_total": "población total", "superficie_km2": "superficie",
        "densidad_poblacional": "densidad", "porcentaje_hogares_internet_2022": "internet",
        "porcentaje_hogares_computadora_2022": "computadora",
        "porcentaje_hogares_agua_red_publica_2022": "agua de red",
        "porcentaje_hogares_cloaca_2022": "cloaca",
        "porcentaje_viviendas_rancho_casilla_2022": "vivienda rancho/casilla",
        "proporcion_cue_rurales_2022": "ruralidad de la oferta",
        "relacion_cue_secundaria_primaria_2022": "relación secundaria/primaria",
        "localizaciones_por_1000_poblacion_escolar_2022": "localizaciones por población escolar",
        "localizaciones_por_100_km2_2022": "localizaciones por superficie",
    }
    return labels.get(variable, variable.replace("_", " "))


def comparison_chart(row: pd.Series, peer: pd.Series) -> go.Figure | None:
    specs = [
        ("Asistencia 15–17", "porcentaje_asistencia_15_17_2022", 1),
        ("Sobreedad", "sobreedad_2025", 100),
        ("Repetición", "repeticion_2025", 100),
        ("Salidos sin pase", "salidos_sin_pase_2025", 100),
        ("Lengua", "lengua_satisfactorio_o_avanzado_2024", 1),
    ]
    rows = [(label, float(row.get(var)) * factor, float(peer.get(var)) * factor)
            for label, var, factor in specs if pd.notna(row.get(var)) and pd.notna(peer.get(var))]
    if not rows:
        return None
    fig = go.Figure()
    for label, left, right in rows:
        fig.add_trace(go.Scatter(x=[left, right], y=[label, label], mode="lines", line={"color": "#cdd8dc", "width": 2}, hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=[x[1] for x in rows], y=[x[0] for x in rows], mode="markers+text",
        name=str(row.departamento_nombre),
        text=[f"{x[1]:.1f}".replace(".", ",") for x in rows], textposition="top center", textfont={"size": 10, "color": "#18324a"},
        marker={"color": "#18324a", "size": 12},
    ))
    fig.add_trace(go.Scatter(
        x=[x[2] for x in rows], y=[x[0] for x in rows], mode="markers+text",
        name=str(peer.departamento_nombre),
        text=[f"{x[2]:.1f}".replace(".", ",") for x in rows], textposition="bottom center", textfont={"size": 10, "color": "#d8a94a"},
        marker={"color": "#d8a94a", "size": 12, "symbol": "diamond"},
    ))
    fig.update_layout(
        height=max(300, len(rows) * 75 + 80), margin=dict(l=20, r=20, t=30, b=50),
        xaxis_title="Porcentaje", legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#e3eaec", gridwidth=1), yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def _choose_peer(peer_id: str, territory_id: str) -> None:
    st.session_state[f"peer_choice_{territory_id}"] = peer_id


def peer_card_html(peer: pd.Series) -> str:
    similar = " · ".join(_readable(v) for v in str(peer.variables_mas_similares).split(";"))
    different = " · ".join(_readable(v) for v in str(peer.principales_diferencias).split(";"))
    return (
        '<article class="peer-card"><div class="peer-index">Territorio comparable</div>'
        f'<h3>{escape(str(peer.par_departamento_nombre))}</h3>'
        f'<div class="peer-meta">{escape(str(peer.par_provincia_nombre))} · '
        f'{escape(str(peer.calidad_comparacion))}</div>'
        '<div class="peer-similarity"><span>Se parece especialmente en</span>'
        f'<strong>{escape(similar)}</strong></div>'
        '<p class="peer-difference"><span>Se diferencia más en:</span> '
        f'{escape(different)}</p></article>'
    )


def render_comparables(profiles: pd.DataFrame, pairs: pd.DataFrame, gaps: pd.DataFrame, territory_id: str, embedded: bool = False) -> None:
    row = profile_row(profiles, territory_id)
    st.markdown('<span class="functional-view-marker functional-view--compare" aria-hidden="true"></span>', unsafe_allow_html=True)
    if embedded:
        st.subheader("¿Con qué territorios tiene sentido compararlo?")
    else:
        st.markdown('<div class="eyebrow">Comparación estructural</div>', unsafe_allow_html=True)
        st.title("¿Con qué territorios tiene sentido compararlo?")
    st.caption(f"{row.departamento_nombre}, {row.provincia_nombre}")
    method_note("La similitud usa población, contexto y oferta; no usa resultados educativos. Similitud estructural no implica equivalencia institucional.")
    label = st.radio(
        "Alcance", ["Nacionales", "Dentro de la provincia"],
        horizontal=True, key=f"peer_scope_{territory_id}",
    )
    comparison_type = "nacional" if label == "Nacionales" else "provincial"
    peers = peer_rows(pairs, territory_id, comparison_type)
    if peers.empty:
        st.info("No se encontraron pares elegibles con cobertura suficiente. Esto no describe el desempeño del territorio.")
        return
    for _, peer in peers.iterrows():
        st.markdown(peer_card_html(peer), unsafe_allow_html=True)
        st.button(
            f"Contrastar con {peer.par_departamento_nombre} →",
            key=f"choose_{territory_id}_{peer.par_departamento_id}_{comparison_type}",
            on_click=_choose_peer, args=(peer.par_departamento_id, territory_id),
        )
    labels = peers.set_index("par_departamento_id").apply(lambda r: f"{r.par_departamento_nombre} · {r.par_provincia_nombre}", axis=1).to_dict()
    choice_key = f"peer_choice_{territory_id}"
    if st.session_state.get(choice_key) not in labels:
        st.session_state[choice_key] = next(iter(labels))
    peer_id = st.session_state[choice_key]
    payload = comparison_payload(gaps, territory_id, peer_id, comparison_type)
    peer_profile = profile_row(profiles, peer_id)
    st.markdown('<div class="chapter-break"><span>Contraste</span></div>', unsafe_allow_html=True)
    st.subheader(f"{row.departamento_nombre} ↔ {peer_profile.departamento_nombre}")
    st.markdown('<p class="lede">Si estos territorios se parecen estructuralmente, ¿qué diferencias educativas aparecen?</p>', unsafe_allow_html=True)
    if payload is None:
        st.info("No hay contraste procesado para este par.")
        return
    st.markdown("#### Por qué son comparables")
    st.write("**Condiciones más similares:** " + ", ".join(_readable(v) for v in payload["similares"]))
    st.write("**Diferencias estructurales principales:** " + ", ".join(_readable(v) for v in payload["diferencias"]))
    st.markdown("#### Dónde cambian los resultados")
    st.caption("Asistencia: Censo 2022 · Trayectoria: RA 2025 · Aprendizaje: Aprender 2024. Las brechas absolutas no indican ganador ni explican causas.")
    figure = comparison_chart(row, peer_profile)
    if figure is not None:
        st.plotly_chart(figure, use_container_width=True)
    metric_grid([(result, format_value(value, "number") + " pp" if pd.notna(value) else "Sin comparación", "Brecha absoluta procesada") for result, value in payload["brechas"].items()])
    method_note("Pregunta para investigar: ¿qué factores no observados podrían acompañar estas diferencias? La comparación no identifica causas ni evalúa gestiones.")
