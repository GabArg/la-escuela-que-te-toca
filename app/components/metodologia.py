"""Síntesis metodológica orientada a lectura pública."""
from __future__ import annotations

import streamlit as st


SOURCE_LINKS = [
    {
        "title": "Relevamiento Anual (RA) 2011–2025",
        "organization": "Secretaría de Educación de la Nación",
        "dataset": "Bases agregadas de Matrícula, Trayectoria y Características",
        "files": "data/raw/ra_historico/{año}/*.csv; para 2025, archivos agregados equivalentes",
        "source_url": "https://www.argentina.gob.ar/capital-humano/educacion/informacion-y-evaluacion-educativa/datos-abiertos",
        "method_url": "https://www.argentina.gob.ar/node/246606",
    },
    {
        "title": "Censo Nacional 2022",
        "organization": "INDEC",
        "dataset": "Población, hogares, vivienda y asistencia por división territorial",
        "files": "tablas provinciales Censo 2022 registradas en data/raw",
        "source_url": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165",
        "method_url": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165",
    },
    {
        "title": "Padrón Oficial de Establecimientos Educativos 2022",
        "organization": "Secretaría de Educación de la Nación",
        "dataset": "Padrón de establecimientos y localizaciones",
        "files": "data/raw/condiciones_escolaridad/padron/padron_2022.xlsx",
        "source_url": "https://www.argentina.gob.ar/node/246613",
        "method_url": "https://www.argentina.gob.ar/node/246613",
    },
    {
        "title": "Aprender Secundaria 2024",
        "organization": "Secretaría de Educación de la Nación",
        "dataset": "Resultados agregados anonimizados de Lengua y Matemática",
        "files": "data/raw/aprender/2024_secundaria_*_agregada.csv",
        "source_url": "https://www.argentina.gob.ar/educacion/evaluacion-informacion-educativa/aprender/aprender-2024/aprender-secundaria-2024",
        "method_url": "https://www.argentina.gob.ar/educacion/evaluacion-informacion-educativa/aprender/aprender-2024/aprender-secundaria-2024",
    },
    {
        "title": "GeoRef Argentina",
        "organization": "Datos Argentina",
        "dataset": "Departamentos y unidades territoriales equivalentes",
        "files": "data/processed/departamentos_argentina.geojson",
        "source_url": "https://www.argentina.gob.ar/georef/descarga-de-la-base-completa",
        "method_url": "https://www.argentina.gob.ar/georef/descarga-de-la-base-completa",
    },
]


def _render_sources() -> None:
    for source in SOURCE_LINKS:
        st.markdown(f"**{source['title']}**  ")
        st.write(f"Organismo: {source['organization']} · Dataset: {source['dataset']}")
        st.caption(f"Archivo utilizado: {source['files']}")
        st.markdown(
            f"[Abrir fuente pública]({source['source_url']}) · "
            f"[Ver metodología oficial]({source['method_url']})"
        )


def render_methodology() -> None:
    st.markdown('<span class="functional-view-marker functional-view--methodology" aria-hidden="true"></span>', unsafe_allow_html=True)
    st.title("Metodología")
    st.write("Una guía breve para interpretar la aplicación. Cada indicador conserva fuente, organismo, año, universo y límites de lectura.")
    sections = {
        "Fuentes y años": "GeoRef; Censo y Padrón 2022; Aprender Secundaria 2024; Relevamiento Anual 2025 y serie RA 2011–2025. Los años se muestran porque no constituyen una única fotografía temporal. La trayectoria nacional de sobreedad suma todas las filas publicadas del universo comparable de Educación Común, incluidas las agregadas o no territorializables, sin asignarlas a departamentos.",
        "CUE y CUE-anexo": "CUE identifica el establecimiento institucional. CUE-anexo identifica sede o anexo/localización. La app prioriza CUE-anexo para despliegue territorial y no lo interpreta como capacidad o vacantes.",
        "Matrícula y asistencia": "RA territorializa matrícula por establecimiento; el Censo observa residencia y asistencia declarada. El cociente matrícula/población es exploratorio y no se denomina tasa oficial de escolarización.",
        "Aprender": "La distribución se muestra únicamente cuando las cuatro categorías están completas. Censal describe el diseño, no participación completa. Un área parcial queda bloqueada; no se renormaliza.",
        "Pares comparables": "La similitud usa territorio, hogares y oferta, nunca resultados educativos. El orden 1–5 es técnico. Calidad y estabilidad describen la comparación, no el desempeño.",
        "Faltantes": "Sin dato no significa cero. Parcial significa que existe información insuficiente para una distribución completa; ausente significa que no hay información identificable para el territorio.",
        "Interpretación": "Las asociaciones y brechas son descriptivas. No demuestran causalidad, no evalúan gestiones y no permiten declarar territorios mejores o peores.",
    }
    for title, text in sections.items():
        with st.expander(title, expanded=title == "Fuentes y años"):
            st.write(text)
    st.subheader("Fuentes y metodología accesibles")
    st.caption("Enlaces públicos verificados y archivos utilizados por esta versión. La fecha de descarga se conserva en los inventarios del proyecto.")
    _render_sources()
