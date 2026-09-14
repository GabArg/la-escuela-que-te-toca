"""Vista histórica basada en transformaciones ya auditadas."""
from __future__ import annotations

from html import escape
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.perfil import format_value, profile_row
from app.components.ui import metric_grid, method_note

HISTORY_OPTIONS = {
    "Sobreedad": ("proporcion_sobreedad", "sobreedad_2025"),
    "Repetición": ("proporcion_repitentes", "repeticion_2025"),
    "Salidos sin pase": ("proporcion_salidos_sin_pase", "salidos_sin_pase_2025"),
}


def history_series(history: pd.DataFrame, territory_id: str, indicator: str) -> pd.DataFrame:
    metric = HISTORY_OPTIONS[indicator][0]
    columns = ["anio", metric]
    result = history.loc[history.departamento_id.eq(territory_id), columns].sort_values("anio").rename(columns={metric: "valor"})
    return result


def history_summary(row: pd.Series, indicator: str) -> dict[str, object]:
    metric, current = HISTORY_OPTIONS[indicator]
    return {
        "valor_2025": row.get(current),
        "mediana_historica": row.get(f"{metric}_mediana_historica"),
        "clasificacion": row.get(f"{metric}_clasificacion_historica"),
        "n_anios": row.get(f"{metric}_n_anios_historicos"),
    }


def render_history(profiles: pd.DataFrame, history: pd.DataFrame, territory_id: str, embedded: bool = False) -> None:
    row = profile_row(profiles, territory_id)
    if embedded:
        st.subheader("¿Cómo llegó hasta acá?")
        st.caption("Evolución territorial: una variable por vez.")
    else:
        st.title("¿Cómo llegó hasta acá?")
        st.caption(f"{row.departamento_nombre}, {row.provincia_nombre}")
    indicator = st.selectbox("Indicador", list(HISTORY_OPTIONS), key="history_indicator")
    series = history_series(history, territory_id, indicator)
    summary = history_summary(row, indicator)
    classification = summary["clasificacion"] if pd.notna(summary["clasificacion"]) else "Sin clasificación"
    metric_grid([
        ("Valor 2025", format_value(summary["valor_2025"], "percent_ratio"), "Relevamiento Anual"),
        ("Mediana histórica", format_value(summary["mediana_historica"], "percent_ratio"), f'{summary["n_anios"]} años observados'),
    ])
    st.markdown(f'<div class="metric-item" style="max-width:360px"><div class="metric-label">Patrón histórico</div>'
                f'<div class="metric-value-text">{escape(classification)}</div>'
                f'<div class="metric-meta">Clasificación descriptiva auditada</div></div>', unsafe_allow_html=True)
    if series.empty or series.valor.notna().sum() == 0:
        st.info("No hay serie histórica identificable para este territorio e indicador.")
        return
    figure = go.Figure(go.Scatter(x=series.anio, y=series.valor * 100, mode="lines+markers", connectgaps=False, line_color="#315c4b"))
    if pd.notna(summary["mediana_historica"]):
        figure.add_hline(y=float(summary["mediana_historica"]) * 100, line_dash="dot", line_color="#66516f", annotation_text="Mediana histórica")
    figure.add_vrect(x0=2020, x1=2022, fillcolor="#C79A45", opacity=.22, line_width=0,
                     annotation_text="Interpretar con cautela", annotation_position="top right")
    figure.update_layout(height=430, xaxis_title="Año", yaxis_title="Porcentaje", margin=dict(l=20, r=20, t=35, b=20),
                         plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                         xaxis=dict(gridcolor="#ede9e0"), yaxis=dict(gridcolor="#ede9e0"))
    st.plotly_chart(figure, use_container_width=True)
    method_note("Serie descriptiva RA 2011–2025. El período 2020–2022 requiere cautela metodológica; el gráfico no atribuye causas.")
