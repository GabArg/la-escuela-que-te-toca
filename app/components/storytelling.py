"""Apertura editorial basada exclusivamente en artefactos auditados."""
from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from app.components.territorio import queue_explore_scale, queue_navigation
from app.components.mapa import load_geojson
from app.components.story_visuals import national_trajectory_svg, territory_mesh_svg, territory_silhouette_svg

GUIDED_ORIGIN_ID = "34063"
GUIDED_PEER_ID = "86140"

STRUCTURAL_STORY_VARIABLES = [
    ("Se parecen en estas dimensiones", "superficie_km2", "Superficie", "km²", 0),
    ("Se parecen en estas dimensiones", "densidad_poblacional", "Densidad", "hab./km²", 1),
    ("Se parecen en estas dimensiones", "porcentaje_hogares_internet_2022", "Hogares con internet", "%", 1),
    ("Se parecen en estas dimensiones", "proporcion_cue_rurales_2022", "Oferta rural", "%", 1),
    ("Se parecen en estas dimensiones", "relacion_cue_secundaria_primaria_2022", "Relación secundaria/primaria", "", 2),
    ("Se parecen en estas dimensiones", "localizaciones_por_1000_poblacion_escolar_2022", "Localizaciones por población escolar", "por 1.000", 1),
    ("También difieren en estas otras", "porcentaje_hogares_agua_red_publica_2022", "Hogares con agua de red", "%", 1),
    ("También difieren en estas otras", "porcentaje_viviendas_rancho_casilla_2022", "Viviendas rancho/casilla", "%", 1),
    ("También difieren en estas otras", "localizaciones_por_100_km2_2022", "Localizaciones por superficie", "por 100 km²", 1),
]


def _go(scale: str) -> None:
    queue_explore_scale(scale)
    queue_navigation("Explorar")


def _open_guided_profile() -> None:
    from app.components.territorio import queue_territory
    queue_territory(GUIDED_ORIGIN_ID)
    queue_explore_scale("territorio")
    queue_navigation("Explorar")


def _open_guided_comparison() -> None:
    from app.components.territorio import queue_territory
    queue_territory(GUIDED_ORIGIN_ID)
    st.session_state[f"peer_choice_{GUIDED_ORIGIN_ID}"] = GUIDED_PEER_ID
    queue_navigation("Comparar")


def national_overage_story(national_history: pd.DataFrame) -> dict[str, float]:
    """Lee el agregado de todas las filas RA publicadas del universo comparable."""
    values: dict[str, float] = {}
    for year in (2011, 2025):
        rows = national_history.loc[national_history.anio.eq(year)]
        if len(rows) != 1:
            raise ValueError(f"No hay un único agregado nacional comparable para {year}.")
        denominator = rows.iloc[0].matricula_grados_comparables
        if pd.isna(denominator) or denominator <= 0:
            raise ValueError(f"No hay denominador nacional comparable para {year}.")
        values[str(year)] = float(rows.iloc[0].sobreedad / denominator * 100)
    return values


def guided_case_data(profiles: pd.DataFrame, pairs: pd.DataFrame, gaps: pd.DataFrame) -> dict[str, object]:
    """Resuelve el caso Ramón Lista → Quebrachos sin recrear cálculos analíticos."""
    profile_rows = profiles.loc[profiles.departamento_id.astype(str).isin([GUIDED_ORIGIN_ID, GUIDED_PEER_ID])]
    if set(profile_rows.departamento_id.astype(str)) != {GUIDED_ORIGIN_ID, GUIDED_PEER_ID}:
        raise ValueError("El bundle no contiene ambos territorios del caso guiado.")
    pair_rows = pairs.loc[
        pairs.departamento_id.astype(str).eq(GUIDED_ORIGIN_ID)
        & pairs.par_departamento_id.astype(str).eq(GUIDED_PEER_ID)
        & pairs.tipo_comparacion.eq("nacional")
    ]
    gap_rows = gaps.loc[
        gaps.departamento_id.astype(str).eq(GUIDED_ORIGIN_ID)
        & gaps.par_departamento_id.astype(str).eq(GUIDED_PEER_ID)
        & gaps.tipo_comparacion.eq("nacional")
    ]
    if pair_rows.empty or gap_rows.empty:
        raise ValueError("Ramón Lista y Quebrachos no forman un par nacional disponible en el bundle.")
    pair, gap = pair_rows.iloc[0], gap_rows.iloc[0]
    origin = profile_rows.loc[profile_rows.departamento_id.astype(str).eq(GUIDED_ORIGIN_ID)].iloc[0]
    peer = profile_rows.loc[profile_rows.departamento_id.astype(str).eq(GUIDED_PEER_ID)].iloc[0]
    variables = set(str(pair.variables_usadas).split(";"))
    dimensions = {
        "Territorio": bool(variables & {"poblacion_total", "superficie_km2", "densidad_poblacional"}),
        "Contexto": any(variable.startswith("porcentaje_hogares_") or "viviendas" in variable for variable in variables),
        "Oferta": any("cue_" in variable or "localizaciones_" in variable for variable in variables),
    }
    comparisons = []
    for group, variable, label, unit, digits in STRUCTURAL_STORY_VARIABLES:
        if variable not in variables:
            raise ValueError(f"La variable narrativa {variable} no interviene en el par auditado.")
        origin_value, peer_value = float(origin[variable]), float(peer[variable])
        if variable == "proporcion_cue_rurales_2022":
            origin_value, peer_value = origin_value * 100, peer_value * 100
        comparisons.append({
            "group": group,
            "variable": variable,
            "label": label,
            "unit": unit,
            "digits": digits,
            "origin_value": origin_value,
            "peer_value": peer_value,
        })
    return {
        "origin_name": origin.departamento_nombre,
        "origin_province": origin.provincia_nombre,
        "peer_name": peer.departamento_nombre,
        "peer_province": peer.provincia_nombre,
        "distance": float(pair.distancia),
        "quality": pair.calidad_comparacion,
        "coverage": float(pair.cobertura_comparacion),
        "dimensions": dimensions,
        "structural_variables": variables,
        "comparisons": comparisons,
        "origin_dropout": float(origin.salidos_sin_pase_2025) * 100,
        "peer_dropout": float(peer.salidos_sin_pase_2025) * 100,
        "dropout_gap": float(gap.brecha_salidos_sin_pase_pp),
        "dropout_year": 2025,
        "dropout_period": 2024,
        "dropout_source": "Relevamiento Anual 2025",
        "origin_attendance": float(origin.porcentaje_asistencia_15_17_2022),
        "attendance_year": 2022,
        "attendance_source": "Censo 2022",
    }


def _number(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def render_story_intro() -> None:
    visual = territory_mesh_svg(load_geojson(), (GUIDED_ORIGIN_ID, GUIDED_PEER_ID), connect=True, css_class="story-cover-map")
    with st.container(key="story_intro"):
        st.markdown(
            '<section class="story-cover"><div class="story-cover-title">'
            '<p class="story-kicker">Datos abiertos · Argentina</p><h1>La escuela<br>que te toca</h1></div>'
            f'<div class="story-cover-visual">{visual}<span>529 unidades · una trama territorial</span></div>'
            '<p class="story-thesis">Mismo país.<br>Territorios parecidos.<br>'
            '<em>Trayectorias que no siempre se parecen.</em></p>'
            '<div class="story-cover-copy"><p class="story-deck">Una exploración territorial de la educación argentina '
            'para detectar dónde mirar, entender cómo cambió, comparar con lugares estructuralmente similares y '
            'transformar diferencias en preguntas investigables.</p>'
            '<p class="story-brand">Comparar mejor, para preguntar mejor.</p></div></section>',
            unsafe_allow_html=True,
        )
        primary, secondary, _ = st.columns([1.15, 1.15, 2.7])
        primary.button("Explorar Argentina", key="story_intro_argentina", type="primary", on_click=_go, args=("argentina",), use_container_width=True)
        secondary.button("Elegir provincia y territorio", key="story_intro_territorio", on_click=_go, args=("provincia",), use_container_width=True)


def render_average_story(profiles: pd.DataFrame, national_history: pd.DataFrame) -> None:
    overage = national_overage_story(national_history)
    mesh = territory_mesh_svg(load_geojson(), css_class="story-count-map")
    trajectory = national_trajectory_svg(national_history)
    st.markdown(
        '<section class="story-section story-averages"><p class="story-number">02</p>'
        '<h2>Lo que un promedio no muestra</h2>'
        '<article class="average-scene average-time"><p class="scene-label">Una trayectoria nacional</p>'
        f'<strong>{_number(overage["2011"])}% <i>→</i> {_number(overage["2025"])}%</strong>{trajectory}'
        '<div class="trajectory-years"><span>2011</span><span>2025</span></div>'
        '<p>En el universo comparable publicado, la sobreedad cayó fuertemente entre 2011 y 2025. '
        'El agregado nacional no describe por igual '
        'la trayectoria de todos los territorios.</p><small>Relevamiento Anual · 2011–2025</small></article>'
        '<article class="average-scene average-territories"><div class="territory-count">'
        f'<strong>{len(profiles)}</strong><span>territorios</span><p>Las diferencias internas de una provincia pueden '
        f'quedar ocultas detrás de un promedio.</p></div><div class="territory-count-visual">{mesh}'
        '<small>529 departamentos y unidades equivalentes</small></div></article>'
        '<article class="average-scene average-pairs"><div class="pair-orbit" aria-hidden="true">'
        '<i></i><span></span><i></i><b>Territorio · Contexto · Oferta</b></div>'
        '<div><p class="scene-label">Pares comparables</p><strong>Parecidos en estructura.<br>'
        '<em>No necesariamente en resultados.</em></strong>'
        '<p>Territorios con condiciones estructurales similares pueden mostrar resultados educativos diferentes.</p></div></article>'
        '</section>', unsafe_allow_html=True,
    )


def render_guided_case(case: dict[str, object]) -> None:
    origin_dropout = float(case["origin_dropout"])
    peer_dropout = float(case["peer_dropout"])
    axis_max = max(origin_dropout, peer_dropout) * 1.18
    origin_position = origin_dropout / axis_max * 100
    peer_position = peer_dropout / axis_max * 100
    origin_name = escape(str(case["origin_name"]))
    origin_province = escape(str(case["origin_province"]))
    peer_name = escape(str(case["peer_name"]))
    peer_province = escape(str(case["peer_province"]))
    geojson = load_geojson()
    origin_shape = territory_silhouette_svg(geojson, GUIDED_ORIGIN_ID, str(case["origin_name"]), "case-shape case-shape-origin")
    peer_shape = territory_silhouette_svg(geojson, GUIDED_PEER_ID, str(case["peer_name"]), "case-shape case-shape-peer")
    comparison_rows = []
    current_group = None
    for comparison in case["comparisons"]:
        if comparison["group"] != current_group:
            current_group = comparison["group"]
            comparison_rows.append(f'<h3>{escape(str(current_group))}</h3>')
        left = float(comparison["origin_value"])
        right = float(comparison["peer_value"])
        axis_max = max(left, right) * 1.12
        left_position = max(3.0, left / axis_max * 100)
        right_position = max(3.0, right / axis_max * 100)
        digits = int(comparison["digits"])
        unit = escape(str(comparison["unit"]))
        comparison_rows.append(
            f'<div class="case-micro" data-variable="{escape(str(comparison["variable"]))}">'
            f'<div class="case-micro-head"><strong>{escape(str(comparison["label"]))}</strong>'
            f'<span>{_number(left, digits)} {unit} / {_number(right, digits)} {unit}</span></div>'
            '<div class="case-micro-axis">'
            f'<i class="origin-dot" style="left:{left_position:.2f}%"></i>'
            f'<i class="peer-dot" style="left:{right_position:.2f}%"></i></div></div>'
        )
    micro_comparisons = "".join(comparison_rows)
    st.markdown(
        '<section class="story-section story-case"><p class="story-number">03</p>'
        '<h2>Un caso para entender la idea</h2><p class="story-question">¿Por qué tiene sentido compararlos?</p>'
        '<div class="case-portraits">'
        f'<div class="case-territory">{origin_shape}<strong>{origin_name}</strong><span>{origin_province}</span></div>'
        '<div class="case-link"><i></i><span>estructuralmente<br>comparables</span><i></i></div>'
        f'<div class="case-territory">{peer_shape}<strong>{peer_name}</strong><span>{peer_province}</span></div></div>'
        f'<p class="story-pair-meta">{escape(str(case["quality"]))} · cobertura estructural completa</p>'
        f'<div class="case-evidence"><div class="case-evidence-key"><span><i></i>{origin_name}</span>'
        f'<span><i></i>{peer_name}</span><p>Cada comparación usa su propia escala y parte de cero.</p></div>'
        f'<div class="case-micros">{micro_comparisons}</div></div>'
        '<p class="story-method">La comparación utiliza características estructurales. '
        'Los resultados educativos no intervienen en la selección de pares. '
        'La similitud estructural no implica equivalencia total.</p></section>'
        '<section class="story-section story-contrast"><p class="story-number">04</p>'
        '<h2>Y, sin embargo,<br>aparecen diferencias.</h2>'
        f'<div class="contrast-shapes" aria-hidden="true">{origin_shape}{peer_shape}</div>'
        f'<p class="story-gap"><strong>{_number(float(case["dropout_gap"]), 2)}<small>pp</small></strong>'
        '<span>de diferencia en salidos sin pase</span></p>'
        f'<div class="story-dumbbell" role="img" aria-label="Comparación de salidos sin pase entre {origin_name} y {peer_name}">'
        f'<div class="dumbbell-axis"><i style="left:{peer_position:.2f}%"></i><i style="left:{origin_position:.2f}%"></i></div>'
        f'<div class="dumbbell-labels"><span><b>{peer_name}</b><strong>{_number(peer_dropout, 2)}%</strong></span>'
        f'<span><b>{origin_name}</b><strong>{_number(origin_dropout, 2)}%</strong></span></div></div>'
        f'<p class="story-source">Salidos sin pase · ciclo lectivo {case["dropout_period"]} · informado en {case["dropout_source"]}</p>'
        f'<div class="story-context"><strong>{_number(float(case["origin_attendance"]), 1)}%</strong>'
        f'<p>Asistencia entre 15 y 17 años<br><span>{origin_name} · Fuente: {case["attendance_source"]}</span></p></div>'
        '<div class="story-caution"><p>“Salidos sin pase” no equivale automáticamente a abandono escolar.</p>'
        '<p>La diferencia observada es descriptiva y no implica causalidad.</p></div></section>',
        unsafe_allow_html=True,
    )
    primary, secondary, _ = st.columns([1.2, 1.5, 2.3])
    primary.button("Abrir Ramón Lista", key="story_case_profile", on_click=_open_guided_profile, use_container_width=True)
    secondary.button("Ver contraste con Quebrachos", key="story_case_compare", on_click=_open_guided_comparison, use_container_width=True)


def render_core_question() -> None:
    st.markdown(
        '<section class="story-core"><span class="story-number">05</span><p>¿Qué explica esa diferencia?</p>'
        '<h2>Estos datos no bastan para explicar la diferencia.<br>'
        '<em>Sí ayudan a decidir qué investigar.</em></h2>'
        '<small>La herramienta no clasifica territorios como mejores o peores. Detecta contrastes, muestra '
        'contexto y ayuda a formular preguntas de investigación.</small></section>', unsafe_allow_html=True,
    )


def render_explore_cta() -> None:
    with st.container(key="story_explore"):
        st.markdown(
            '<section class="story-explore"><p class="story-number">06 · Tres escalas</p>'
            '<h2>Ahora te toca mirar.</h2><p class="story-explore-deck">Elegí desde dónde empezar.</p>'
            '<div class="story-paths">'
            '<div><span>01</span><strong>Argentina</strong><b>529 territorios</b><p>Mirar el panorama nacional</p></div>'
            '<div><span>02</span><strong>Provincia</strong><b>Diferencias que el promedio puede ocultar</b></div>'
            '<div><span>03</span><strong>Territorio</strong><b>Historia, contexto y comparables</b></div>'
            '</div></section>', unsafe_allow_html=True,
        )
        columns = st.columns(3)
        for column, label, key_suffix, scale in zip(
            columns,
            ["Explorar el país →", "Elegir provincia →", "Elegir territorio →"],
            ["argentina", "provincia", "territorio"],
            ["argentina", "provincia", "provincia"],
        ):
            column.button(
                label,
                key=f"story_explore_{key_suffix}",
                on_click=_go,
                args=(scale,),
                use_container_width=True,
            )


def render_storytelling_home(
    profiles: pd.DataFrame,
    pairs: pd.DataFrame,
    gaps: pd.DataFrame,
    history: pd.DataFrame,
    national_history: pd.DataFrame,
) -> None:
    case = guided_case_data(profiles, pairs, gaps)
    render_story_intro()
    render_average_story(profiles, national_history)
    render_guided_case(case)
    render_core_question()
    render_explore_cta()
