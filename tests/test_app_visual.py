import pandas as pd

from app.components.comparables import comparison_chart
from app.components.mapa import (
    ARGENTINA_CENTER,
    ARGENTINA_PROJECTION_SCALE,
    MAP_VARIABLES,
    build_map,
    map_data_state,
    queue_map_selection,
    territory_from_selection,
)
from app.components.perfil import profile_row
from app.components.ui import coverage_text, profile_sentence


def test_map_selection_reads_location():
    assert territory_from_selection({"selection": {"points": [{"location": "70070"}]}}) == "70070"
    assert territory_from_selection({"selection": {"points": []}}) is None


def test_map_selection_updates_territory_without_navigation():
    state = {"nav_section": "Explorar", "explore_scale": "argentina"}
    changed = queue_map_selection(state, "06028", "70070", {"06028", "70070"})
    assert changed is True
    assert state["pending_territory_id"] == "06028"
    assert "pending_nav_section" not in state
    assert state["explore_scale"] == "argentina"


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


def test_all_national_map_modes_share_the_same_initial_argentina_viewport():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    assert ARGENTINA_PROJECTION_SCALE == 5.5
    for label in MAP_VARIABLES:
        figure = build_map(profiles, label, "70070")
        assert figure.layout.geo.fitbounds is None
        assert figure.layout.geo.center.lat == ARGENTINA_CENTER["lat"]
        assert figure.layout.geo.center.lon == ARGENTINA_CENTER["lon"]
        assert figure.layout.geo.projection.scale == ARGENTINA_PROJECTION_SCALE


def test_province_map_keeps_location_fitbounds_for_varied_provinces():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    province_names = [
        "Buenos Aires", "Tierra del Fuego, Antártida e Islas del Atlántico Sur",
        "Jujuy", "Tucumán", "Santa Cruz", "Ciudad Autónoma de Buenos Aires",
    ]
    for province_name in province_names:
        province = profiles.loc[profiles.provincia_nombre.eq(province_name)]
        assert not province.empty
        selected_id = str(province.iloc[-1].departamento_id)
        figure = build_map(province, "Mapa neutro", selected_id)
        assert figure.layout.geo.fitbounds == "locations"
        selected_trace = figure.data[-1]
        assert list(selected_trace.locations) == [selected_id]


def test_ab_chart_uses_observed_values_only():
    profiles = pd.read_parquet("data/processed/perfiles_territoriales.parquet")
    figure = comparison_chart(profile_row(profiles, "70070"), profile_row(profiles, "02007"))
    assert figure is not None
    assert len(figure.data) >= 3
