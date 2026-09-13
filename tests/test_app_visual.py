import pandas as pd

from app.components.comparables import comparison_chart
from app.components.mapa import MAP_VARIABLES, build_map, map_data_state, territory_from_selection
from app.components.perfil import profile_row
from app.components.ui import coverage_text, profile_sentence


def test_map_selection_reads_location():
    assert territory_from_selection({"selection": {"points": [{"location": "70070"}]}}) == "70070"
    assert territory_from_selection({"selection": {"points": []}}) is None


def test_map_data_states_do_not_turn_missing_into_available():
    row = pd.Series({"x": pd.NA, "aprendizaje_lengua_cobertura": "parcial"})
    assert map_data_state(row, "contexto", "x") == "sin dato"
    assert map_data_state(row, "lengua", "x") == "parcial"
    assert map_data_state(row, "descriptivo", None) == "disponible"


def test_coverage_microcopy_is_plain_language():
    assert coverage_text("parcial") == "Cobertura parcial"
    assert coverage_text("ausente") == "Sin dato"
    assert coverage_text(pd.NA) == "Sin información de cobertura"


def test_profile_sentence_uses_only_structured_dimensions():
    signals = pd.DataFrame({"dimension": ["Acceso", "Oferta", "Acceso"]})
    assert profile_sentence(signals) == "Este territorio presenta señales para mirar en acceso y oferta."


def test_map_builds_all_declared_modes():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    for label in MAP_VARIABLES:
        figure = build_map(profiles, label, "70070")
        locations = {str(value) for trace in figure.data for value in (trace.locations if trace.locations is not None else [])}
        assert "70070" in locations


def test_ab_chart_uses_observed_values_only():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    figure = comparison_chart(profile_row(profiles, "70070"), profile_row(profiles, "02007"))
    assert figure is not None
    assert len(figure.data) >= 3
