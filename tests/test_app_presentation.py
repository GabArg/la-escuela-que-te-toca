import pandas as pd
import pytest

from app.components.comparables import comparison_payload, peer_card_html, peer_rows
from app.components.historia import history_series, history_summary
from app.components.perfil import format_value, learning_distribution, profile_row, signal_rows
from app.components.preview import signal_count_text, territory_preview_data
from app.components.senales import filter_signals, visible_signal_rows
from app.components.storytelling import guided_case_data, national_overage_story
from app.components.territorio import consume_pending_navigation, territory_options


@pytest.fixture(scope="module")
def profiles():
    return pd.read_parquet("data/processed/perfiles_territoriales.parquet")


@pytest.fixture(scope="module")
def signals():
    return pd.read_parquet("data/processed/senales_prioritarias_perfiles.parquet")


def test_null_formatting_is_explicit():
    assert format_value(pd.NA) == "Sin dato"
    assert format_value(float("nan")) == "Sin dato"
    assert format_value(0, "percent") == "0,0%"


def test_ratio_and_count_formatting():
    assert format_value(.1234, "percent_ratio") == "12,3%"
    assert format_value(12345, "integer") == "12.345"


def test_profile_selection_is_unique(profiles):
    row = profile_row(profiles, "70070")
    assert row.departamento_nombre == "Pocito"
    with pytest.raises(ValueError):
        profile_row(profiles, "no-existe")


def test_signal_extraction_has_at_most_three(signals):
    selected = signal_rows(signals, "70070")
    assert len(selected) == 3
    assert selected.prioridad.tolist() == [1, 2, 3]


def test_complete_learning_distribution(profiles):
    row = profile_row(profiles, "02007")
    language = learning_distribution(row, "Lengua")
    mathematics = learning_distribution(row, "Matematica")
    assert language is not None and abs(sum(language.values()) - 100) < 1e-8
    assert mathematics is not None and abs(sum(mathematics.values()) - 100) < 1e-8


def test_partial_learning_is_blocked(profiles):
    row = profile_row(profiles, "70070")
    assert learning_distribution(row, "Lengua") is not None
    assert learning_distribution(row, "Matematica") is None


def test_absent_learning_is_blocked(profiles):
    row = profile_row(profiles, "06182")
    assert learning_distribution(row, "Lengua") is None
    assert learning_distribution(row, "Matematica") is None


def test_history_selection_and_summary(profiles):
    history = pd.DataFrame({"departamento_id": ["x", "x"], "anio": [2011, 2012], "proporcion_sobreedad": [.2, pd.NA]})
    selected = history_series(history, "x", "Sobreedad")
    assert selected.anio.tolist() == [2011, 2012]
    assert pd.isna(selected.iloc[1].valor)
    summary = history_summary(profile_row(profiles, "42147"), "Repetición")
    assert summary["clasificacion"] == "Deterioro sostenido"


def test_peer_selection_max_five():
    pairs = pd.read_parquet("data/processed/pares_comparables.parquet")
    selected = peer_rows(pairs, "70070", "nacional")
    assert 1 <= len(selected) <= 5
    assert not selected.par_departamento_id.eq("70070").any()


def test_comparison_payload_uses_processed_gaps():
    pairs = pd.read_parquet("data/processed/pares_comparables.parquet")
    gaps = pd.read_parquet("data/processed/brechas_entre_pares.parquet")
    first = peer_rows(pairs, "70070", "nacional").iloc[0]
    payload = comparison_payload(gaps, "70070", first.par_departamento_id)
    assert payload is not None
    assert payload["similares"] and payload["diferencias"]
    assert "Sobreedad" in payload["brechas"]


def test_signal_filters_are_nonordinal(signals):
    filtered = filter_signals(signals, "San Juan", "Oferta", "Señal educativa")
    assert not filtered.empty
    assert filtered.provincia_nombre.eq("San Juan").all()
    assert filtered.departamento_nombre.tolist() == sorted(filtered.departamento_nombre.tolist())


def test_territory_cascade(profiles):
    options = territory_options(profiles, "La Pampa")
    assert "Trenel" in set(options.departamento_nombre)
    assert options.provincia_nombre.eq("La Pampa").all()


def test_navigation_is_deferred_until_next_rerun():
    state = {"nav_section": "Explorar", "pending_nav_section": "Comparar"}
    selected = consume_pending_navigation(state, ["Explorar", "Comparar", "Investigar", "Metodología"])
    assert selected == "Comparar"
    assert state["nav_section"] == "Comparar"
    assert "pending_nav_section" not in state


def test_map_preview_uses_existing_profile_and_signals(profiles, signals):
    preview = territory_preview_data(profiles, signals, "70070")
    assert preview["territorio"] == "Pocito"
    assert preview["provincia"] == "San Juan"
    assert preview["cantidad_senales"] == len(signals[signals.departamento_id.eq("70070")])
    assert len(preview["senales"]) <= 2


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (0, "No se activan señales prioritarias con los criterios actuales. Esto no implica ausencia de problemas."),
        (1, "1 señal para mirar"),
        (2, "2 señales para mirar"),
    ],
)
def test_map_preview_signal_count_copy(count, expected):
    assert signal_count_text(count) == expected


def test_map_preview_prioritizes_at_most_two_signals(profiles):
    territory_id = str(profiles.iloc[0].departamento_id)
    signals = pd.DataFrame(
        {
            "departamento_id": [territory_id] * 3,
            "prioridad": [3, 1, 2],
            "tipo_senal": ["Señal educativa"] * 3,
            "dimension": ["Contexto", "Trayectoria", "Oferta"],
            "senal": ["Tercera", "Primera", "Segunda"],
            "evidencia": ["c", "a", "b"],
        }
    )
    preview = territory_preview_data(profiles, signals, territory_id)
    assert [item["senal"] for item in preview["senales"]] == ["Primera", "Segunda"]
    assert preview["cantidad_senales"] == 3


def test_comparable_card_keeps_scan_hierarchy_and_cta_data():
    peer = pd.Series(
        {
            "par_departamento_nombre": "Bolívar",
            "par_provincia_nombre": "Buenos Aires",
            "calidad_comparacion": "Alta comparabilidad",
            "variables_mas_similares": "densidad_poblacional;superficie_km2;poblacion_total",
            "principales_diferencias": "porcentaje_hogares_cloaca_2022;relacion_cue_secundaria_primaria_2022",
        }
    )
    html = peer_card_html(peer)
    assert "Territorio comparable" in html
    assert "Se parece especialmente en" in html
    assert "Se diferencia más en" in html
    assert "Bolívar" in html


def test_storytelling_national_overage_uses_existing_counts():
    from app.components.data import load_national_history

    values = national_overage_story(load_national_history())
    assert values["2011"] == pytest.approx(27.4368336089)
    assert values["2025"] == pytest.approx(11.8313277519)


def test_guided_case_resolves_existing_ramón_lista_quebrachos_pair(profiles):
    pairs = pd.read_parquet("data/processed/pares_comparables.parquet")
    gaps = pd.read_parquet("data/processed/brechas_entre_pares.parquet")
    case = guided_case_data(profiles, pairs, gaps)
    assert (case["origin_name"], case["peer_name"]) == ("Ramón Lista", "Quebrachos")
    assert case["dropout_gap"] == pytest.approx(9.150448)
    assert case["origin_attendance"] == pytest.approx(76.780186)
    assert case["dropout_year"] == 2025
    assert case["dropout_period"] == 2024
    assert case["attendance_year"] == 2022
    assert case["dropout_source"] == "Relevamiento Anual 2025"
    assert case["attendance_source"] == "Censo 2022"
    assert all(case["dimensions"].values())
    assert len(case["comparisons"]) == 9
    comparison_variables = {item["variable"] for item in case["comparisons"]}
    assert {
        "porcentaje_hogares_agua_red_publica_2022",
        "porcentaje_viviendas_rancho_casilla_2022",
        "localizaciones_por_100_km2_2022",
    }.issubset(comparison_variables)
    assert {item["variable"] for item in case["comparisons"]}.issubset(case["structural_variables"])
    assert not any(
        outcome in item["variable"]
        for item in case["comparisons"]
        for outcome in ("sobreedad", "repeticion", "salidos", "asistencia", "lengua", "matematica")
    )


@pytest.mark.parametrize("territory_id", ["70070", "34063", "42147", "02007", "06861", "06182"])
def test_real_validation_cases_have_one_profile(profiles, territory_id):
    assert len(profiles[profiles.departamento_id.eq(territory_id)]) == 1


def test_radar_limits_rendered_rows_without_losing_total(signals):
    assert len(visible_signal_rows(signals, 40)) == 40
    assert len(visible_signal_rows(signals, 80)) == 80
    assert len(signals) > len(visible_signal_rows(signals, 40))
