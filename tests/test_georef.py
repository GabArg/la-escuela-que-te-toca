"""Pruebas de integridad para la base territorial de GeoRef."""

import pytest

from src.ingestion.georef import (
    build_territorial_dataframe,
    load_department_features,
    load_provinces,
)


@pytest.fixture(scope="module")
def provinces():
    return load_provinces()


@pytest.fixture(scope="module")
def territories(provinces):
    return build_territorial_dataframe(provinces, load_department_features())


def test_identifiers_are_not_null(territories):
    identifiers = territories[["provincia_id", "departamento_id", "clave_territorial"]]
    assert not identifiers.isna().any().any()
    assert not (identifiers.apply(lambda column: column.str.strip()) == "").any().any()


def test_territorial_keys_are_unique(territories):
    assert territories["clave_territorial"].is_unique


def test_department_identifiers_are_unique_nationally(territories):
    assert territories["departamento_id"].is_unique


def test_provinces_are_valid(provinces, territories):
    assert set(territories["provincia_id"]).issubset(set(provinces["provincia_id"]))


def test_every_department_has_an_associated_province(territories):
    assert territories["provincia_nombre"].notna().all()


def test_there_are_no_exact_duplicates(territories):
    assert not territories.duplicated().any()
