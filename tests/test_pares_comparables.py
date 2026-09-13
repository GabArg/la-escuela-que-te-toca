import numpy as np
import pandas as pd
import pytest

from src.analysis.pares_comparables import (
    BASE_SPECS,
    EDUCATIONAL_RESULTS,
    MIN_SHARED,
    TOP_K,
    add_quality,
    build_engine,
    dimension_weights,
    neighbor_table,
    robust_matrix,
    validate,
    variable_weights,
)


@pytest.fixture(scope="module")
def profiles():
    return pd.read_parquet("data/processed/perfiles_territoriales.parquet").reset_index(drop=True)


@pytest.fixture(scope="module")
def engine():
    return build_engine()


def test_no_educational_result_in_similarity():
    variables = {spec.variable for spec in BASE_SPECS}
    assert not variables.intersection(EDUCATIONAL_RESULTS)
    assert not any(token in variable for variable in variables for token in ["sobreedad", "repet", "promoc", "salidos", "lengua", "matematica", "bandera", "clasificacion"])


def test_no_self_neighbor(engine):
    pairs, _, _ = engine
    assert not pairs.departamento_id.eq(pairs.par_departamento_id).any()


def test_no_improper_duplicates(engine):
    pairs, _, _ = engine
    assert not pairs.duplicated(["departamento_id", "par_departamento_id", "tipo_comparacion"]).any()


def test_distance_nonnegative_and_bounded(engine):
    pairs, _, _ = engine
    assert pairs.distancia.between(0, 1).all()


def test_top_five_maximum(engine):
    pairs, _, _ = engine
    assert pairs.groupby(["departamento_id", "tipo_comparacion"]).size().le(TOP_K).all()
    assert pairs.ranking_similitud_interno.between(1, TOP_K).all()


def test_missing_values_are_not_zero_imputed(profiles):
    matrix = robust_matrix(profiles, BASE_SPECS)
    for spec in BASE_SPECS:
        assert matrix.loc[profiles[spec.variable].isna(), spec.variable].isna().all()


def test_minimum_shared_coverage(engine):
    pairs, _, _ = engine
    assert pairs.n_variables_usadas.ge(MIN_SHARED).all()
    assert pairs.cobertura_comparacion.eq(pairs.n_variables_usadas / len(BASE_SPECS)).all()


def test_dimension_weights_are_balanced_and_documented():
    weights = dimension_weights(BASE_SPECS)
    assert set(weights) == {"territorio", "contexto", "oferta"}
    assert all(np.isclose(value, 1 / 3) for value in weights.values())
    assert np.isclose(sum(variable_weights(BASE_SPECS).values()), 1)
    dictionary = pd.read_csv("data/dictionaries/variables_pares_comparables.csv")
    used = dictionary[dictionary.usar_en_similitud.eq("base")]
    assert set(used.variable) == {spec.variable for spec in BASE_SPECS}


def test_reproducible_neighbors(profiles):
    first = neighbor_table(profiles, BASE_SPECS, "nacional")
    second = neighbor_table(profiles, BASE_SPECS, "nacional")
    pd.testing.assert_frame_equal(first, second)


def test_quality_categories_follow_documented_inputs(engine):
    pairs, _, sensitivity = engine
    rebuilt = add_quality(pairs.drop(columns=["estabilidad_origen", "calidad_comparacion"]), sensitivity)
    pd.testing.assert_series_equal(pairs.calidad_comparacion, rebuilt.calidad_comparacion)
    assert set(pairs.calidad_comparacion) == {"Alta comparabilidad", "Comparabilidad media", "Comparabilidad baja"}


def test_gaps_preserve_pair_identity_and_are_post_similarity(engine):
    pairs, gaps, _ = engine
    keys = ["departamento_id", "par_departamento_id", "tipo_comparacion"]
    pd.testing.assert_frame_equal(pairs[keys], gaps[keys])
    assert not any(column.startswith("brecha_") for column in pairs)


def test_partial_aprender_never_generates_complete_gap(engine, profiles):
    _, gaps, _ = engine
    status = profiles.set_index("departamento_id")
    for area in ["lengua", "matematica"]:
        gap = f"brecha_{area}_satisfactorio_avanzado_pp"
        complete_left = gaps.departamento_id.map(status[f"aprendizaje_{area}_cobertura"]).eq("completo")
        complete_right = gaps.par_departamento_id.map(status[f"aprendizaje_{area}_cobertura"]).eq("completo")
        assert gaps.loc[~(complete_left & complete_right), gap].isna().all()


def test_absence_never_becomes_zero_gap(engine, profiles):
    _, gaps, _ = engine
    lookup = profiles.set_index("departamento_id")
    missing = gaps.departamento_id.map(lookup.sobreedad_2025).isna() | gaps.par_departamento_id.map(lookup.sobreedad_2025).isna()
    assert gaps.loc[missing, "brecha_sobreedad_pp"].isna().all()


def test_sensitivity_has_expected_specs_and_bounds(engine):
    _, _, sensitivity = engine
    assert set(sensitivity.especificacion) == {"base", "sin_conectividad", "sin_oferta", "solo_territorio_contexto"}
    assert sensitivity.proporcion_estable_top5.between(0, 1).all()


def test_full_validation(engine):
    pairs, gaps, _ = engine
    validate(pairs, gaps)
