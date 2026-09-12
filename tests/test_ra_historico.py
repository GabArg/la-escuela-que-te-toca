"""Pruebas de comparabilidad e integridad del panel RA histórico."""

import pandas as pd
import pytest

from src.analysis.ra_historico import ADVERSE, build_indicators, classify_series
from src.ingestion.ra_historico import (
    COMPARABILITY_PATH, FAMILIES, MANIFEST_PATH, SPECIAL, VARIABLES, YEARS,
    build_long, load_raw, validate_long, verify_hashes,
)


@pytest.fixture(scope="module")
def long():
    return build_long()


def test_manifest_has_all_expected_files_and_valid_hashes():
    manifest = pd.read_csv(MANIFEST_PATH)
    assert set(manifest.anio) == set(YEARS)
    assert set(manifest.dataset) == set(FAMILIES)
    assert len(manifest) == len(YEARS) * len(FAMILIES)
    verify_hashes()


def test_all_years_and_approved_variables(long):
    validate_long(long)
    approved = {variable for family in VARIABLES.values() for variable in family}
    assert set(long.anio) == set(YEARS)
    assert set(long.variable) == approved


def test_no_non_comparable_variable_enters_long(long):
    inventory = pd.read_csv(COMPARABILITY_PATH)
    excluded = set(inventory.loc[inventory.nivel_comparabilidad.eq("No comparable"), "variable_estandar"].dropna())
    assert set(long.variable).isdisjoint(excluded)
    assert long.nivel_comparabilidad.eq("Alta").all()


def test_special_rows_never_receive_id(long):
    special = long.estado_cobertura.isin(SPECIAL)
    assert long.loc[special, "departamento_id"].isna().all()


def test_missing_values_are_preserved(long):
    assert long.valor.isna().any()
    assert long.loc[long.valor.isna(), "valor"].isna().all()


def test_no_unexpected_identified_duplicates(long):
    grain = ["anio", "departamento_id", "sector", "ambito", "variable"]
    identified = long.departamento_id.notna()
    assert not long.loc[identified].duplicated(grain).any()


def test_ids_belong_to_georef(long):
    valid = set(pd.read_parquet("data/processed/territorios_argentina.parquet").departamento_id.astype(str))
    assert set(long.departamento_id.dropna().astype(str)).issubset(valid)


def test_schema_changes_are_detectable():
    assert "campo_20" not in load_raw(2022, "matricula")
    assert "campo_20" in load_raw(2023, "matricula")
    assert "promovidos_mas_2mat_1" not in load_raw(2024, "trayectoria")
    assert "promovidos_mas_2mat_1" in load_raw(2025, "trayectoria")


def test_counts_by_year_are_coherent(long):
    coverage = long.loc[long.departamento_id.notna()].groupby("anio").departamento_id.nunique()
    assert coverage.between(485, 506).all()
    assert coverage.loc[2025] == 506


def test_rates_are_recomputed_from_counts(long):
    indicators = build_indicators(long)
    row = indicators.dropna(subset=["repitentes", "matricula_grados_comparables"]).iloc[0]
    assert row.proporcion_repitentes == pytest.approx(row.repitentes / row.matricula_grados_comparables)
    assert not any(variable.startswith("proporcion_") for variable in long.variable)


def test_classification_uses_only_documented_categories(long):
    signals = classify_series(build_indicators(long))
    allowed = {"Persistente alto", "Persistente bajo", "Mejora sostenida", "Deterioro sostenido", "Volátil", "Anomalía reciente", "Datos insuficientes"}
    assert set(signals.clasificacion).issubset(allowed)
    assert set(signals.indicador) == set(ADVERSE)
