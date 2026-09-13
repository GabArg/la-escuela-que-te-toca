import pandas as pd
import pytest

from app.components.comparables import comparison_payload, peer_rows
from app.components.historia import history_series, history_summary
from app.components.perfil import format_value, learning_distribution, profile_row, signal_rows
from app.components.senales import filter_signals
from app.components.territorio import territory_options


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
    filtered = filter_signals(signals, "San Juan", "Oferta", "Baja oferta relativa de localizaciones")
    assert not filtered.empty
    assert filtered.provincia_nombre.eq("San Juan").all()
    assert filtered.departamento_nombre.tolist() == sorted(filtered.departamento_nombre.tolist())


def test_territory_cascade(profiles):
    options = territory_options(profiles, "La Pampa")
    assert "Trenel" in set(options.departamento_nombre)
    assert options.provincia_nombre.eq("La Pampa").all()


@pytest.mark.parametrize("territory_id", ["70070", "34063", "42147", "02007", "06861", "06182"])
def test_real_validation_cases_have_one_profile(profiles, territory_id):
    assert len(profiles[profiles.departamento_id.eq(territory_id)]) == 1
