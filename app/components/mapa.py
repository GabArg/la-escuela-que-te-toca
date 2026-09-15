"""Mapa territorial interactivo; consume solamente outputs existentes."""
from __future__ import annotations

import json
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.data import artifact_path

MAP_VARIABLES = {
    "Mapa neutro": (None, "", "descriptivo"),
    "Asistencia 15–17": ("porcentaje_asistencia_15_17_2022", "%", "acceso"),
    "Sobreedad": ("sobreedad_2025", "%", "trayectoria"),
    "Oferta relativa": ("localizaciones_por_1000_poblacion_escolar_2022", " por 1.000", "oferta"),
    "Hogares con internet": ("porcentaje_hogares_internet_2022", "%", "contexto"),
    "Lengua: satisfactorio + avanzado": ("lengua_satisfactorio_o_avanzado_2024", "%", "lengua"),
}

ARGENTINA_CENTER = {"lat": -38.4, "lon": -64.2}
ARGENTINA_PROJECTION_SCALE = 5.5
MAP_CONFIG = {
    "displaylogo": False,
    # Plotly Geo no ofrece minZoom. El encuadre inicial funciona como mínimo:
    # se puede acercar, desplazar y volver a él, pero no alejar más el país.
    "modeBarButtonsToRemove": ["zoomOutGeo"],
}


@st.cache_data(show_spinner=False)
def load_geojson() -> dict[str, Any]:
    path = artifact_path("departamentos_argentina.geojson")
    return json.loads(path.read_text(encoding="utf-8"))


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


def queue_map_selection(state: Any, clicked: str | None, selected_id: str, valid_ids: set[str]) -> bool:
    """Encola sólo la selección; navegar requiere el CTA del preview."""
    if clicked and clicked != selected_id and clicked in valid_ids:
        state["pending_territory_id"] = clicked
        return True
    return False


def _display_value(value: object, variable: str | None, suffix: str) -> str:
    if variable is None: return "Mapa neutro"
    if pd.isna(value): return "Sin dato"
    number = float(value) * (100 if variable == "sobreedad_2025" else 1)
    return f"{number:.1f}{suffix}".replace(".", ",")


def build_map(
    profiles: pd.DataFrame,
    variable_label: str,
    selected_id: str | None = None,
    height: int = 480,
) -> go.Figure:
    geojson = load_geojson()
    variable, suffix, kind = MAP_VARIABLES[variable_label]
    data = profiles[["departamento_id", "departamento_nombre", "provincia_nombre"]].copy()
    data["value"] = 1.0 if variable is None else profiles[variable]
    data["state"] = profiles.apply(lambda row: map_data_state(row, kind, variable), axis=1)
    data["display"] = [_display_value(v, variable, suffix) for v in data.value]
    fig = go.Figure()
    available = data[data.state.eq("disponible")]
    colorscale = [[0, "#93b9d0"], [1, "#18324a"]] if variable else [[0, "#cddfe7"], [1, "#cddfe7"]]
    fig.add_trace(go.Choropleth(
        geojson=geojson, featureidkey="properties.departamento_id", locations=available.departamento_id,
        z=available.value, colorscale=colorscale, showscale=variable is not None, marker_line_color="#f7f5ee", marker_line_width=.55,
        customdata=available[["departamento_nombre", "provincia_nombre", "display"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]}<extra></extra>",
        colorbar={"title": suffix.strip(), "thickness": 10, "len": .55},
    ))
    for state, color, label in [("parcial", "#d8a94a", "Cobertura parcial"), ("sin dato", "#e8eceb", "Sin dato")]:
        subset = data[data.state.eq(state)]
        if subset.empty: continue
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.departamento_id", locations=subset.departamento_id,
            z=[1] * len(subset), colorscale=[[0, color], [1, color]], showscale=False, name=label,
            marker_line_color="#f7f5ee", marker_line_width=.55,
            customdata=subset[["departamento_nombre", "provincia_nombre", "display"]],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>" + label + "<extra></extra>",
        ))
    if selected_id:
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.departamento_id", locations=[selected_id], z=[1],
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            marker_line_color="#d8a94a", marker_line_width=3.2, hoverinfo="skip",
        ))
    is_national_view = data.provincia_nombre.nunique() > 1
    if is_national_view:
        fig.update_geos(
            center=ARGENTINA_CENTER,
            projection_scale=ARGENTINA_PROJECTION_SCALE,
            visible=False,
            bgcolor="rgba(0,0,0,0)",
        )
    else:
        # El encuadre provincial existente se conserva sin modificaciones.
        fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", dragmode=False)
    return fig


def render_map(
    profiles: pd.DataFrame,
    selected_id: str,
    key: str = "map_territory",
    height: int = 480,
) -> None:
    label = st.selectbox("Qué dimensión querés mirar", list(MAP_VARIABLES), key=f"{key}_variable")
    event = st.plotly_chart(
        build_map(profiles, label, selected_id, height=height),
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        config=MAP_CONFIG,
        key=key,
    )
    clicked = territory_from_selection(event)
    if queue_map_selection(st.session_state, clicked, selected_id, set(profiles.departamento_id.astype(str))):
        st.rerun()
    st.markdown(
        '<div class="map-footer">'
        '<div class="map-legend">'
        '<span><i class="legend-swatch" style="background:#93b9d0"></i>Dato disponible</span>'
        '<span><i class="legend-swatch" style="background:#d8a94a"></i>Cobertura parcial</span>'
        '<span><i class="legend-swatch" style="background:#e8eceb"></i>Sin dato</span>'
        '</div>'
        'Seleccioná una unidad en el mapa para sincronizar el territorio. La ausencia de dato nunca representa cero.'
        '</div>', unsafe_allow_html=True,
    )
