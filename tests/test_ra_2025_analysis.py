"""Pruebas de las transformaciones analiticas RA 2025."""

import pandas as pd
import pytest

from src.analysis.ra_2025 import (
    KEYS,
    _row_sum,
    aggregate_departments,
    build_analytical_table,
    validate_analytical_table,
)


@pytest.fixture(scope="module")
def analytical():
    return build_analytical_table()


def test_analytical_grain_and_territorial_integrity(analytical):
    validate_analytical_table(analytical)
    assert not analytical.duplicated(KEYS).any()
    assert analytical["departamento_id"].nunique() == 506


def test_special_records_are_not_distributed(analytical):
    assert analytical["departamento_id"].notna().all()
    assert not analytical.astype("string").apply(
        lambda column: column.str.casefold().isin(["enmascarado", "sin datos"])
    ).any().any()


def test_all_missing_counts_remain_missing():
    sample = pd.DataFrame({"a": [pd.NA, 2], "b": [pd.NA, 3]}, dtype="Float64")
    result = _row_sum(sample, ["a", "b"])
    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == 5


def test_counts_aggregate_and_rates_are_recomputed_not_summed():
    sample = pd.DataFrame(
        {
            "departamento_id": ["001", "001"], "provincia_id": ["01", "01"],
            "provincia_nombre": ["P", "P"], "departamento_nombre": ["D", "D"],
            "matricula_total": [100.0, 300.0], "matricula_grados_comparables": [100.0, 300.0],
            "repetidores_total": [10.0, 60.0], "sobreedad_total": [20.0, 90.0],
            "trayectoria_promovidos_total": [80.0, 210.0], "trayectoria_ultimo_total": [90.0, 280.0],
            "trayectoria_nopromo_total": [10.0, 70.0], "trayectoria_ssp_total": [1.0, 9.0],
            "trayectoria_inicial_total": [100.0, 300.0],
        }
    )
    result = aggregate_departments(sample).iloc[0]
    assert result["matricula_total"] == 400
    assert result["proporcion_repetidores_sobre_matricula"] == pytest.approx(70 / 400)
    assert result["proporcion_salidos_sin_pase_sobre_inicial"] == pytest.approx(10 / 400)


def test_no_absence_is_materialized_as_zero(analytical):
    missing = analytical["trayectoria_inicial_total"].isna()
    assert missing.sum() == 8
    assert analytical.loc[missing, "trayectoria_inicial_total"].isna().all()


def test_analytical_coverage_matches_documented_universe(analytical):
    flags = ["cobertura_matricula", "cobertura_trayectoria", "cobertura_caracteristicas"]
    assert analytical.loc[:, flags].all(axis=1).sum() == 1125
    assert (~analytical["cobertura_trayectoria"]).sum() == 8
    assert analytical.groupby("departamento_id")[flags].any().all().all()
