from pathlib import Path

import pandas as pd
import pytest

from src.ingestion.aprender import AREAS, LEVELS, build, load_area, prepare_area


@pytest.fixture(scope="module")
def analytical(tmp_path_factory):
    return build(tmp_path_factory.mktemp("aprender") / "out.parquet")


def test_expected_year_level_and_areas(analytical):
    assert set(analytical.anio) == {2024}
    assert set(analytical.nivel) == {"Secundaria"}
    assert set(analytical.area) == set(AREAS)


def test_performance_levels(analytical):
    assert set(analytical.indicador) == set(LEVELS.values())


def test_weights_are_required_and_recorded(analytical):
    assert analytical.ponderado.eq(True).all()


def test_percentages_in_range_or_null(analytical):
    assert analytical.valor.dropna().between(0, 100).all()


def test_complete_distributions_sum_to_100(analytical):
    complete = analytical[analytical.estado_cobertura.eq("completo")]
    sums = complete.groupby(["area", "departamento_id"]).valor.sum()
    assert (sums.sub(100).abs() < 1e-8).all()


def test_partial_distributions_are_not_rebased(analytical):
    partial = analytical[analytical.estado_cobertura.eq("parcial")]
    assert partial.valor.isna().all()


def test_no_duplicate_analytical_grain(analytical):
    assert not analytical.duplicated(["anio", "area", "departamento_id", "indicador"]).any()


def test_ids_are_valid_georef(analytical):
    valid = set(pd.read_parquet("data/processed/territorios_argentina.parquet").departamento_id.astype(str))
    assert set(analytical.departamento_id.astype(str)).issubset(valid)


def test_unmatched_source_rows_never_enter_output():
    for area in AREAS:
        raw = load_area(area)
        assert raw.departamento.astype(str).str.casefold().eq("enmascarado").any()
        assert prepare_area(area).departamento_id.notna().all()


def test_raw_absence_is_preserved():
    raw = load_area("Matematica")
    assert raw[list(LEVELS.values())].isna().any().any()


def test_inventory_marks_sampled_primary_weighting():
    inventory = pd.read_csv("data/dictionaries/inventario_aprender.csv")
    row = inventory[(inventory.anio == 2024) & (inventory.nivel == "Primaria")].iloc[0]
    assert row.censal_muestral == "muestral"
    assert row.ponderador == "sí"


def test_no_low_comparability_series_is_built(analytical):
    assert set(analytical.nivel_comparabilidad) == {"corte_transversal"}


def test_raw_files_exist():
    for filename, _ in AREAS.values():
        assert (Path("data/raw/aprender") / filename).exists()
