"""Punto de entrada de la aplicación Streamlit."""

import streamlit as st


st.set_page_config(page_title="La escuela que te toca", layout="wide")

st.title("La escuela que te toca")
st.write(
    "Aplicación de análisis territorial de la educación argentina "
    "basada en datos abiertos oficiales."
)
st.info("Proyecto en etapa inicial. Próximamente se incorporarán análisis interactivos.")

# TODO: definir navegación, fuentes validadas, indicadores y componentes de la app.

