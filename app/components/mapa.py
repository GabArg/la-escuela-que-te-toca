"""Mapa territorial interactivo; consume solamente outputs existentes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
GEOJSON = ROOT / "data/processed/departamentos_argentina.geojson"

MAP_VARIABLES = {
    "Mapa neutro": (None, "", "descriptivo"),
    "Asistencia 15–17": ("porcentaje_asistencia_15_17_2022", "%", "acceso"),
    "Sobreedad": ("sobreedad_2025", "%", "trayectoria"),
    "Oferta relativa": ("localizaciones_por_1000_poblacion_escolar_2022", " por 1.000", "oferta"),
    "Hogares con internet": ("porcentaje_hogares_internet_2022", "%", "contexto"),
    "Lengua: satisfactorio + avanzado": ("lengua_satisfactorio_o_avanzado_2024", "%", "lengua"),
}


@st.cache_data(show_spinner=False)
def load_geojson() -> dict[str, Any]:
    if not GEOJSON.exists():
        raise FileNotFoundError("Falta el GeoJSON territorial procesado.")
    return json.loads(GEOJSON.read_text(encoding="utf-8"))


def map_data_state(row: pd.Series, kind: str, variable: str | None) -> str:
    if variable is None:
        return "disponible"
    if kind == "lengua":
        status = str(row.get("aprendizaje_lengua_cobertura", "")).lower()
        if status == "parcial": return "parcial"
        if status != "completo": return "sin dato"
    return "sin dato" if pd.isna(row.get(variable)) else "disponible"


def territory_from_selection(event: Any) -> str | None:
    if not event:
        return None
    selection = event.get("selection", {}) if isinstance(event, dict) else getattr(event, "selection", {})
    points = selection.get("points", []) if isinstance(selection, dict) else getattr(selection, "points", [])
    if not points:
        return None
    point = points[0]
    if isinstance(point, dict):
        return str(point.get("location") or (point.get("customdata") or [None])[0]) if point.get("location") or point.get("customdata") else None
    return str(getattr(point, "location", "")) or None


def _display_value(value: object, variable: str | None, suffix: str) -> str:
    if variable is None: return "Mapa neutro"
    if pd.isna(value): return "Sin dato"
    number = float(value) * (100 if variable == "sobreedad_2025" else 1)
    return f"{number:.1f}{suffix}".replace(".", ",")


def build_map(profiles: pd.DataFrame, variable_label: str, selected_id: str | None = None) -> go.Figure:
    geojson = load_geojson()
    variable, suffix, kind = MAP_VARIABLES[variable_label]
    data = profiles[["departamento_id", "departamento_nombre", "provincia_nombre"]].copy()
    data["value"] = 1.0 if variable is None else profiles[variable]
    data["state"] = profiles.apply(lambda row: map_data_state(row, kind, variable), axis=1)
    data["display"] = [_display_value(v, variable, suffix) for v in data.value]
    fig = go.Figure()
    available = data[data.state.eq("disponible")]
    colorscale = [[0, "#dce8e1"], [1, "#315c4b"]] if variable else [[0, "#ded9cf"], [1, "#ded9cf"]]
    fig.add_trace(go.Choropleth(
        geojson=geojson, featureidkey="properties.departamento_id", locations=available.departamento_id,
        z=available.value, colorscale=colorscale, showscale=variable is not None, marker_line_color="#fffdf8", marker_line_width=.35,
        customdata=available[["departamento_nombre", "provincia_nombre", "display"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]}<extra></extra>",
        colorbar={"title": suffix.strip(), "thickness": 10, "len": .55},
    ))
    for state, color, label in [("parcial", "#c79a45", "Cobertura parcial"), ("sin dato", "#eeeae2", "Sin dato")]:
        subset = data[data.state.eq(state)]
        if subset.empty: continue
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.departamento_id", locations=subset.departamento_id,
            z=[1] * len(subset), colorscale=[[0, color], [1, color]], showscale=False, name=label,
            marker_line_color="#fffdf8", marker_line_width=.35,
            customdata=subset[["departamento_nombre", "provincia_nombre", "display"]],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>" + label + "<extra></extra>",
        ))
    if selected_id:
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.departamento_id", locations=[selected_id], z=[1],
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            marker_line_color="#b66a50", marker_line_width=2.5, hoverinfo="skip",
        ))
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(height=650, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", dragmode=False)
    return fig


def render_map(profiles: pd.DataFrame, selected_id: str) -> None:
    label = st.selectbox("Colorear por", list(MAP_VARIABLES), key="map_variable")
    event = st.plotly_chart(build_map(profiles, label, selected_id), width="stretch", on_select="rerun", selection_mode="points", key="territory_map")
    clicked = territory_from_selection(event)
    if clicked and clicked != selected_id and clicked in set(profiles.departamento_id.astype(str)):
        st.session_state.pending_territory_id = clicked
        st.rerun()
    st.markdown('<div class="map-legend"><span><i class="legend-swatch" style="background:#dce8e1"></i>Dato disponible</span><span><i class="legend-swatch" style="background:#c79a45"></i>Cobertura parcial</span><span><i class="legend-swatch" style="background:#eeeae2"></i>Sin dato</span></div>', unsafe_allow_html=True)
    st.caption("Seleccioná una unidad en el mapa para sincronizar el territorio. La ausencia de dato nunca representa cero.")
