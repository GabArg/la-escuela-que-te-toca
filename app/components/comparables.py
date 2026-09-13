"""Presentación del motor de pares y contraste posterior."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.perfil import format_value, profile_row

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


def render_comparables(profiles: pd.DataFrame, pairs: pd.DataFrame, gaps: pd.DataFrame, territory_id: str) -> None:
    row = profile_row(profiles, territory_id)
    st.title("¿Con quién tiene sentido compararlo?")
    st.caption(f"{row.departamento_nombre}, {row.provincia_nombre}")
    st.info("Estos territorios son similares por sus condiciones estructurales, no por sus resultados educativos.")
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
            st.caption(f"Detalle técnico — distancia estructural: {peer.distancia:.4f}; variables compartidas: {peer.n_variables_usadas}")
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
    st.caption("Brechas absolutas en puntos porcentuales. No indican ganador ni explican causas.")
    result_columns = st.columns(3)
    for index, (result, value) in enumerate(payload["brechas"].items()):
        result_columns[index % 3].metric(result, format_value(value, "number") + " pp" if pd.notna(value) else "Sin comparación")
