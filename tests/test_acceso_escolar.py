"""Pruebas del cruce exploratorio de acceso escolar."""

import pandas as pd
import pytest

from src.ingestion.acceso_escolar import AGE_GROUPS, build_access_dataset, load_ra_age, validate_access


@pytest.fixture(scope="module")
def access():
    return build_access_dataset()


def test_valid_year_groups_and_ids(access):
    validate_access(access)
    assert set(access.anio) == {2022}
    assert set(access.grupo_edad.astype(str)) == set(AGE_GROUPS)
    valid = set(pd.read_parquet("data/processed/territorios_argentina.parquet").departamento_id.astype(str))
    assert set(access.departamento_id.dropna().astype(str)).issubset(valid)


def test_counts_are_non_negative(access):
    assert (access.poblacion.dropna() >= 0).all()
    assert (access.matricula.dropna() >= 0).all()


def test_missing_is_preserved_and_not_zero_filled(access):
    only_population = access.cobertura_dato.eq("solo_poblacion")
    assert only_population.sum() == 88
    assert access.loc[only_population, "matricula"].isna().all()


def test_masked_rows_never_receive_id():
    raw = load_ra_age()
    masked = raw.departamento_nombre_fuente.str.casefold().eq("enmascarado")
    assert raw.loc[masked, "departamento_id"].isna().all()


def test_no_division_by_zero(access):
    zero = access.poblacion.eq(0)
    assert access.loc[zero, "indicador_acceso"].isna().all()


def test_out_of_range_ratios_are_flagged(access):
    assert access.indicador_fuera_rango.equals(access.indicador_acceso.gt(1))
    assert access.indicador_fuera_rango.any()


def test_reference_year_difference_is_explicit(access):
    assert access.observaciones.str.contains("matrícula por localización y población por residencia").all()
    assert access.tipo_indicador.str.startswith("cociente exploratorio").all()


def test_no_unexpected_duplicates(access):
    assert not access.duplicated(["anio", "departamento_id", "grupo_edad"]).any()


def test_territorial_coverage(access):
    assert access.departamento_id.nunique() == 527
    assert access.loc[access.cobertura_dato.eq("poblacion_y_matricula"), "departamento_id"].nunique() == 505
    assert access.loc[access.cobertura_dato.eq("solo_poblacion"), "departamento_id"].nunique() == 22
