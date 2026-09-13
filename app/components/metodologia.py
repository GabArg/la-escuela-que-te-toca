"""Síntesis metodológica orientada a lectura pública."""
from __future__ import annotations

import streamlit as st


def render_methodology() -> None:
    st.title("Metodología")
    st.write("Una guía breve para interpretar la aplicación. La documentación completa está en `docs/metodologia/` y `docs/producto/`.")
    sections = {
        "Fuentes y años": "GeoRef; Censo y Padrón 2022; Aprender Secundaria 2024; Relevamiento Anual 2025 y serie RA 2011–2025. Los años se muestran porque no constituyen una única fotografía temporal.",
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
