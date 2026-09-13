"""Presentación del motor de pares y contraste posterior."""
from __future__ import annotations

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
        fig.add_trace(go.Scatter(x=[left, right], y=[label, label], mode="lines", line={"color": "#d8d2c7", "width": 3}, hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[x[1] for x in rows], y=[x[0] for x in rows], mode="markers", name=str(row.departamento_nombre), marker={"color": "#315c4b", "size": 11}))
    fig.add_trace(go.Scatter(x=[x[2] for x in rows], y=[x[0] for x in rows], mode="markers", name=str(peer.departamento_nombre), marker={"color": "#b66a50", "size": 11, "symbol": "diamond"}))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=30), xaxis_title="Porcentaje", legend_orientation="h")
    return fig


def render_comparables(profiles: pd.DataFrame, pairs: pd.DataFrame, gaps: pd.DataFrame, territory_id: str) -> None:
    row = profile_row(profiles, territory_id)
    st.title("¿Con quién tiene sentido compararlo?")
    st.caption(f"{row.departamento_nombre}, {row.provincia_nombre}")
    method_note("Similar significa estructuralmente similar, no educativamente similar. Los resultados no intervienen en la selección de pares.")
    label = st.radio("Universo", ["Nacionales", "Dentro de la provincia"], horizontal=True)
    comparison_type = "nacional" if label == "Nacionales" else "provincial"
    peers = peer_rows(pairs, territory_id, comparison_type)
    if peers.empty:
        st.warning("No se encontraron pares elegibles con cobertura suficiente para esta especificación.")
        return
    for _, peer in peers.iterrows():
        with st.expander(f"{peer.par_departamento_nombre} · {peer.par_provincia_nombre} — {peer.calidad_comparacion}"):
            st.write("**Similares en:** " + ", ".join(_readable(v) for v in str(peer.variables_mas_similares).split(";")))
            st.write("**Difieren más en:** " + ", ".join(_readable(v) for v in str(peer.principales_diferencias).split(";")))
            st.caption(f"Estabilidad del conjunto de vecinos: {format_value(peer.estabilidad_origen * 100, 'percent')}")
            with st.popover("Ver detalle metodológico"):
                st.write(f"Distancia estructural: {peer.distancia:.4f}")
                st.write(f"Variables compartidas: {peer.n_variables_usadas}")
    labels = peers.set_index("par_departamento_id").apply(lambda r: f"{r.par_departamento_nombre} · {r.par_provincia_nombre}", axis=1).to_dict()
    peer_id = st.selectbox("Elegir un par para contrastar", list(labels), format_func=lambda value: labels[value])
    payload = comparison_payload(gaps, territory_id, peer_id, comparison_type)
    peer_profile = profile_row(profiles, peer_id)
    st.subheader(f"{row.departamento_nombre} vs. {peer_profile.departamento_nombre}")
    if payload is None:
        st.info("No hay contraste procesado para este par.")
        return
    st.markdown("#### Por qué son comparables")
    cols = st.columns(2)
    cols[0].write("**Condiciones más similares**\n\n" + "\n".join(f"- {_readable(v)}" for v in payload["similares"]))
    cols[1].write("**Diferencias estructurales principales**\n\n" + "\n".join(f"- {_readable(v)}" for v in payload["diferencias"]))
    st.markdown("#### Dónde cambian los resultados")
    st.caption("Asistencia: Censo 2022 · Trayectoria: RA 2025 · Aprendizaje: Aprender 2024. Las brechas absolutas no indican ganador ni explican causas.")
    figure = comparison_chart(row, peer_profile)
    if figure is not None:
        st.plotly_chart(figure, width="stretch")
    metric_grid([(result, format_value(value, "number") + " pp" if pd.notna(value) else "Sin comparación", "Brecha absoluta procesada") for result, value in payload["brechas"].items()])
