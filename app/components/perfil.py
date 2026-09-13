"""Funciones de presentación del perfil territorial."""
from __future__ import annotations

import math
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.ui import coverage_text, metric_grid, profile_sentence, signal_card


def is_missing(value: Any) -> bool:
    try:
        if bool(pd.isna(value)):
            return True
        return isinstance(value, (int, float)) and not math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def format_value(value: Any, kind: str = "number", decimals: int = 1) -> str:
    if is_missing(value):
        return "Sin dato"
    number = float(value)
    if kind == "percent_ratio":
        number *= 100
        suffix = "%"
    elif kind == "percent":
        suffix = "%"
    elif kind == "integer":
        return f"{number:,.0f}".replace(",", ".")
    else:
        suffix = ""
    return f"{number:.{decimals}f}{suffix}".replace(".", ",")


def profile_row(profiles: pd.DataFrame, territory_id: str) -> pd.Series:
    rows = profiles.loc[profiles.departamento_id.eq(territory_id)]
    if len(rows) != 1:
        raise ValueError("El territorio seleccionado no tiene un perfil único.")
    return rows.iloc[0]


def signal_rows(signals: pd.DataFrame, territory_id: str, limit: int = 3) -> pd.DataFrame:
    return signals.loc[signals.departamento_id.eq(territory_id)].sort_values("prioridad").head(limit)


def learning_distribution(row: pd.Series, area: str) -> dict[str, float] | None:
    prefix = area.lower()
    if row.get(f"aprendizaje_{prefix}_cobertura") != "completo":
        return None
    columns = {
        "Por debajo del básico": f"{prefix}_por_debajo_del_basico_2024",
        "Básico": f"{prefix}_basico_2024",
        "Satisfactorio": f"{prefix}_satisfactorio_2024",
        "Avanzado": f"{prefix}_avanzado_2024",
    }
    values = {label: row.get(column) for label, column in columns.items()}
    return None if any(is_missing(value) for value in values.values()) else {key: float(value) for key, value in values.items()}


def reference_plot(label: str, value: Any, provincial: Any, national: Any, suffix: str = "") -> go.Figure | None:
    observed = [("Territorio", value), ("Mediana provincial", provincial), ("Mediana nacional", national)]
    observed = [(name, float(number)) for name, number in observed if not is_missing(number)]
    if not observed:
        return None
    figure = go.Figure(go.Scatter(x=[v for _, v in observed], y=[label] * len(observed), mode="markers+text",
                                  text=[name for name, _ in observed], textposition="top center",
                                  marker={"size": [13] + [9] * (len(observed) - 1), "color": ["#3E5C76"] + ["#9B8C7A"] * (len(observed) - 1)}))
    figure.update_layout(height=150, margin=dict(l=10, r=10, t=35, b=20), xaxis_title=suffix, showlegend=False)
    figure.update_yaxes(visible=False)
    return figure


def _metric(row: pd.Series, label: str, variable: str, kind: str, year: int, source: str) -> None:
    value = row.get(variable)
    st.markdown(f"**{label}**  \n{format_value(value, kind)}")
    st.caption(f"{year} · {source}")


def render_profile(profiles: pd.DataFrame, signals: pd.DataFrame, territory_id: str) -> None:
    row = profile_row(profiles, territory_id)
    selected = signal_rows(signals, territory_id)
    st.markdown(
        f'<div class="territory-header"><div class="eyebrow">{row.provincia_nombre}</div>'
        f'<h1>{row.departamento_nombre}</h1><p>Departamento o unidad territorial equivalente</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<span class="coverage-chip">{coverage_text(row.calidad_total_del_perfil)}</span>', unsafe_allow_html=True)
    st.markdown(f'<p class="lede">{profile_sentence(selected)}</p>', unsafe_allow_html=True)
    st.caption("Fuentes principales: Censo y Padrón 2022 · Aprender 2024 · Relevamiento Anual 2025")

    st.subheader("Qué merece mirar")
    if selected.empty:
        st.write("No hay señales prioritarias activadas con los datos disponibles.")
    else:
        for _, signal in selected.iterrows():
            signal_card(signal.dimension, signal.senal, signal.evidencia, signal.nivel_confianza)

    st.subheader("Acceso y asistencia")
    metric_grid([(f"Asistencia {age.replace('_', '–')}", format_value(row.get(f"porcentaje_asistencia_{age}_2022"), "percent"), "2022 · Censo") for age in ["4_5", "6_11", "12_14", "15_17"]])
    with st.expander("Comparar asistencia 15–17 con medianas"):
        variable = "porcentaje_asistencia_15_17_2022"
        figure = reference_plot("Asistencia 15–17", row.get(variable), row.get(f"{variable}__mediana_provincial"), row.get(f"{variable}__mediana_nacional"), "Porcentaje")
        if figure is not None: st.plotly_chart(figure, width="stretch")

    st.subheader("Trayectoria")
    metric_grid([(label, format_value(row.get(variable), "percent_ratio"), "2025 · Relevamiento Anual") for label, variable in zip(["Sobreedad", "Repetición", "Salidos sin pase"], ["sobreedad_2025", "repeticion_2025", "salidos_sin_pase_2025"])])
    with st.expander("Comparar sobreedad con medianas"):
        variable = "sobreedad_2025"
        values = [row.get(variable), row.get(f"{variable}__mediana_provincial"), row.get(f"{variable}__mediana_nacional")]
        values = [value * 100 if not is_missing(value) else value for value in values]
        figure = reference_plot("Sobreedad", *values, "Porcentaje")
        if figure is not None: st.plotly_chart(figure, width="stretch")

    st.subheader("Oferta")
    definitions = [
        ("Localizaciones", "localizaciones_total_2022", "integer"),
        ("CUE con secundaria", "establecimientos_cue_secundaria_2022", "integer"),
        ("Localizaciones por 1.000", "localizaciones_por_1000_poblacion_escolar_2022", "number"),
        ("CUE rurales", "proporcion_cue_rurales_2022", "percent_ratio"),
    ]
    metric_grid([(label, format_value(row.get(variable), kind), "2022 · Padrón oficial") for label, variable, kind in definitions])

    st.subheader("Contexto")
    st.caption("Estas variables ayudan a contextualizar el territorio. No implican causalidad sobre los resultados educativos.")
    context = [("Densidad", "densidad_poblacional", "number", "hab./km²"),
               ("Internet", "porcentaje_hogares_internet_2022", "percent", ""),
               ("Computadora", "porcentaje_hogares_computadora_2022", "percent", ""),
               ("Rancho/casilla", "porcentaje_viviendas_rancho_casilla_2022", "percent", "")]
    metric_grid([(label, format_value(row.get(variable), kind) + (f" {unit}" if unit else ""), "2022 · Censo") for label, variable, kind, unit in context])
    with st.expander("Ver agua y saneamiento"):
        cols = st.columns(2)
        with cols[0]: _metric(row, "Agua de red", "porcentaje_hogares_agua_red_publica_2022", "percent", 2022, "Censo")
        with cols[1]: _metric(row, "Cloaca", "porcentaje_hogares_cloaca_2022", "percent", 2022, "Censo")

    st.subheader("Aprendizaje")
    for area in ["Lengua", "Matematica"]:
        title = "Matemática" if area == "Matematica" else area
        st.markdown(f"**{title} · Aprender Secundaria 2024**")
        status = row.get(f"aprendizaje_{area.lower()}_cobertura")
        distribution = learning_distribution(row, area)
        if distribution is None:
            if status == "parcial":
                st.warning("Información parcial: no se presenta una distribución completa para evitar una lectura engañosa.")
            else:
                st.info("Sin información identificable.")
            continue
        figure = go.Figure(go.Bar(x=list(distribution.values()), y=list(distribution), orientation="h", marker_color=["#9b8f83", "#c79a45", "#668b78", "#315c4b"]))
        figure.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=20), xaxis_title="Porcentaje", showlegend=False)
        st.plotly_chart(figure, width="stretch")
        combined = distribution["Satisfactorio"] + distribution["Avanzado"]
        st.caption(f"Satisfactorio + avanzado: {format_value(combined, 'percent')}. Suma transparente de categorías oficiales.")
