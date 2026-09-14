import math

import pandas as pd
from streamlit.testing.v1 import AppTest

from app.components.mapa import MAP_VARIABLES, build_map
from app.components.perfil import format_value
from app.components.ui import readable_evidence


def test_fundamental_counts_are_unchanged():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    signals = pd.read_parquet("data/processed/senales_prioritarias_perfiles.parquet")
    pairs = pd.read_parquet("data/processed/pares_comparables.parquet")
    assert len(profiles) == profiles.departamento_id.nunique() == 529
    assert len(signals) == 751
    assert len(pairs) == 4975


def test_map_renders_529_unique_units_without_zero_imputation():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    for label in MAP_VARIABLES:
        figure = build_map(profiles, label)
        locations = {str(location) for trace in figure.data for location in ([] if trace.locations is None else trace.locations)}
        assert locations == set(profiles.departamento_id.astype(str))


def test_non_finite_values_are_never_exposed():
    assert format_value(math.inf) == "Sin dato"
    assert format_value(-math.inf) == "Sin dato"
    assert format_value(float("nan")) == "Sin dato"


def test_signal_evidence_removes_internal_tokens():
    text = readable_evidence("valor=80.4680; umbral_P25=83.3540")
    assert "P25" not in text and "valor=" not in text
    assert "primer cuartil nacional" in text


def test_all_views_render_without_exceptions():
    cases = [
        ("Explorar", "home"),
        ("Explorar", "argentina"),
        ("Explorar", "provincia"),
        ("Explorar", "territorio"),
        ("Comparar", None),
        ("Investigar", None),
        ("Metodología", None),
    ]
    for section, scale in cases:
        app = AppTest.from_file("app/app.py", default_timeout=40)
        app.session_state["territory_id"] = "70070"
        app.session_state["nav_section"] = section
        if scale:
            app.session_state["explore_scale"] = scale
        app.run()
        assert not app.exception
        assert not app.error


def test_cross_province_state_transition_is_tolerant():
    app = AppTest.from_file("app/app.py", default_timeout=40)
    app.run()
    app.selectbox(key="province_sidebar").select("Formosa").run()
    app.selectbox(key="territory_sidebar").select_index(8).run()
    assert app.session_state["territory_id"] == "34063"
    assert not app.exception
    assert not app.error
