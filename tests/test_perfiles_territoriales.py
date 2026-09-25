import pandas as pd
import pytest

from src.features.perfiles_territoriales import (
    COMPARISON_VARIABLES,
    MIN_PROVINCIAL_N,
    SIGNAL_RULES,
    STRUCTURAL_CONTEXT_VARIABLES,
    build_profiles,
    prioritized_signals,
    validate_profiles,
)


@pytest.fixture(scope="module")
def profiles():
    return build_profiles()


def test_exactly_529_georef_units(profiles):
    assert len(profiles) == 529
    assert profiles.departamento_id.nunique() == 529


def test_territorial_key_is_complete_and_unique(profiles):
    assert profiles.clave_territorial.notna().all()
    assert profiles.clave_territorial.is_unique


def test_source_absence_is_preserved(profiles):
    assert profiles.localizaciones_total_2022.isna().any()
    assert profiles.sobreedad_2025.isna().any()


def test_ranges_are_valid(profiles):
    validate_profiles(profiles)
    percentages = [c for c in profiles if c.startswith("porcentaje_") and "__" not in c]
    assert all(profiles[c].dropna().between(0, 100).all() for c in percentages)


@pytest.mark.parametrize("area", ["lengua", "matematica"])
def test_partial_learning_has_no_percentages(profiles, area):
    partial = profiles[f"aprendizaje_{area}_cobertura"].eq("parcial")
    values = [c for c in profiles if c.startswith(f"{area}_") and c.endswith("_2024")]
    assert profiles.loc[partial, values].isna().all().all()


def test_satisfactory_plus_advanced_is_transparent(profiles):
    expected = profiles.lengua_satisfactorio_2024 + profiles.lengua_avanzado_2024
    pd.testing.assert_series_equal(profiles.lengua_satisfactorio_o_avanzado_2024, expected, check_names=False)


def test_flags_are_nullable_when_input_is_missing(profiles):
    pairs = {
        "bandera_asistencia_15_17_baja_relativa": "porcentaje_asistencia_15_17_2022",
        "bandera_baja_oferta_localizaciones_relativa": "localizaciones_por_1000_poblacion_escolar_2022",
        "bandera_vulnerabilidad_habitacional_relativa": "porcentaje_viviendas_rancho_casilla_2022",
    }
    for flag, source in pairs.items():
        assert profiles.loc[profiles[source].isna(), flag].isna().all()


def test_flags_are_reproducible(profiles):
    rebuilt = build_profiles()
    flags = [c for c in profiles if c.startswith("bandera_")]
    pd.testing.assert_frame_equal(profiles[flags], rebuilt[flags])


def test_at_most_three_prioritized_signals(profiles):
    signals = prioritized_signals(profiles)
    assert signals.groupby("departamento_id").size().max() <= 3
    assert signals.prioridad.between(1, 3).all()


def test_provincial_comparison_requires_minimum_n(profiles):
    for variable in COMPARISON_VARIABLES:
        counts = profiles.groupby("provincia_id")[variable].transform("count")
        median = profiles[f"{variable}__mediana_provincial"]
        assert median.loc[counts.lt(MIN_PROVINCIAL_N)].isna().all()


def test_structural_context_excludes_educational_results():
    forbidden = ("aprendizaje", "sobreedad", "repeticion", "promocion", "salidos")
    assert not any(any(token in variable for token in forbidden) for variable in STRUCTURAL_CONTEXT_VARIABLES)


def test_no_score_or_ordinal_ranking(profiles):
    forbidden = {"score", "ranking", "puesto"}
    assert not forbidden.intersection(profiles.columns)
    assert not any("percentil" in c for c in profiles.columns)


def test_rule_dictionary_matches_pipeline():
    rules = pd.read_csv("data/dictionaries/reglas_banderas_perfiles.csv")
    assert set(rules.bandera) == {rule[0] for rule in SIGNAL_RULES}


def test_metadata_covers_every_column(profiles):
    metadata = pd.read_csv("data/dictionaries/variables_perfil_territorial.csv")
    assert set(metadata.variable) == set(profiles.columns)


def test_coverage_dictionary_has_529_unique_units():
    coverage = pd.read_csv("data/dictionaries/cobertura_perfiles_territoriales.csv", dtype={"departamento_id": "string"})
    assert len(coverage) == coverage.departamento_id.nunique() == 529


def test_historical_persistent_high_is_integrated_by_indicator(profiles):
    historical = pd.read_parquet("data/processed/senales_ra_2011_2025.parquet")
    persistent = historical[historical.clasificacion.eq("Persistente alto")]
    assert persistent.groupby("indicador").size().to_dict() == {
        "proporcion_repitentes": 39,
        "proporcion_salidos_sin_pase": 56,
    }
    assert not persistent.indicador.eq("proporcion_sobreedad").any()
    expected = profiles.proporcion_sobreedad_clasificacion_historica.eq("Persistente alto")
    pd.testing.assert_series_equal(
        profiles.bandera_sobreedad_persistente_alta.fillna(False),
        expected,
        check_names=False,
        check_dtype=False,
    )


def test_aprender_partial_definition_is_unambiguous(profiles):
    language = profiles.aprendizaje_lengua_cobertura
    mathematics = profiles.aprendizaje_matematica_cobertura
    expected = language.eq("parcial") | mathematics.eq("parcial")
    present = language.notna() | mathematics.notna()
    assert int(expected.sum()) == 354
    assert int((language.eq("completo") & mathematics.eq("parcial")).sum()) == 335
    assert int((language.eq("parcial") & mathematics.eq("parcial")).sum()) == 19
    assert int((language.isna() & mathematics.isna()).sum()) == 30
    assert profiles.loc[present, "bandera_dato_aprender_parcial"].equals(expected.loc[present].astype("boolean"))
    assert profiles.loc[~present, "bandera_dato_aprender_parcial"].isna().all()


def test_flag_counts_match_independent_rules(profiles):
    rules = {
        "bandera_asistencia_15_17_baja_relativa": profiles.porcentaje_asistencia_15_17_2022.le(profiles.porcentaje_asistencia_15_17_2022.quantile(.25)),
        "bandera_baja_oferta_localizaciones_relativa": profiles.localizaciones_por_1000_poblacion_escolar_2022.le(profiles.localizaciones_por_1000_poblacion_escolar_2022.quantile(.25)),
        "bandera_vulnerabilidad_habitacional_relativa": profiles.porcentaje_viviendas_rancho_casilla_2022.ge(profiles.porcentaje_viviendas_rancho_casilla_2022.quantile(.75)),
        "bandera_sobreedad_persistente_alta": profiles.proporcion_sobreedad_clasificacion_historica.eq("Persistente alto"),
        "bandera_cobertura_dato_baja": profiles.calidad_total_del_perfil.eq("Cobertura baja"),
    }
    for flag, expected in rules.items():
        observed = profiles[flag]
        assert int(observed.fillna(False).sum()) == int(expected.sum())
        assert not observed.loc[expected.isna()].fillna(False).any()


def test_prioritized_signal_evidence_and_confidence(profiles):
    signals = prioritized_signals(profiles)
    assert len(signals) == 751
    assert signals.evidencia.notna().all()
    assert signals.evidencia.str.contains("=", regex=False).all()
    assert set(signals.nivel_confianza) <= {"Alto", "Medio"}
    coverage_facts = signals.tipo_senal.eq("Advertencia de cobertura / calidad documental")
    assert signals.loc[coverage_facts, "nivel_confianza"].eq("Alto").all()
    assert signals.loc[coverage_facts, "dimension"].isin(["Calidad documental", "Cobertura de Aprender"]).all()
    assert signals.loc[~coverage_facts, "tipo_senal"].eq("Señal educativa").all()
