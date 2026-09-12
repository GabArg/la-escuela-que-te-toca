"""Pruebas de las bases RA 2025 agregadas por departamento."""

import pytest

from src.ingestion.educacion_departamental import (
    BRIDGE_PATH,
    DATASETS,
    UNIDENTIFIABLE_DEPARTMENT_LABELS,
    build_coverage_table,
    load_bridge,
    load_georef,
    prepare_dataset,
    validate_prepared_dataset,
)


@pytest.fixture(scope="module")
def prepared():
    return {key: prepare_dataset(spec) for key, spec in DATASETS.items()}


@pytest.mark.parametrize("dataset", DATASETS)
def test_required_columns_and_year(prepared, dataset):
    frame = prepared[dataset]
    validate_prepared_dataset(frame, dataset)
    assert set(frame["anio"]) == {2025}


@pytest.mark.parametrize("dataset", DATASETS)
def test_expected_territorial_ids_are_not_null(prepared, dataset):
    frame = prepared[dataset]
    identifiable = ~frame["match_metodo"].isin(
        ["no_identificable_en_fuente", "puente_pendiente"]
    )
    assert frame.loc[
        identifiable, ["provincia_id", "departamento_id", "clave_territorial"]
    ].notna().all().all()


@pytest.mark.parametrize("dataset", DATASETS)
def test_no_unexpected_grain_duplicates(prepared, dataset):
    frame = prepared[dataset]
    grain = [
        "anio",
        "provincia_nombre_fuente",
        "departamento_nombre_fuente",
        "sector",
        "ambito",
    ]
    assert not frame.duplicated(grain).any()


@pytest.mark.parametrize("dataset", DATASETS)
def test_matches_reference_georef_ids(prepared, dataset):
    frame = prepared[dataset]
    matched = frame.loc[frame["departamento_id"].notna(), "departamento_id"]
    assert matched.nunique() == 506


def test_reported_source_coverage(prepared):
    assert prepared["matricula"][["provincia_nombre_fuente", "departamento_nombre_fuente"]].drop_duplicates().shape[0] == 537
    assert prepared["caracteristicas"][["provincia_nombre_fuente", "departamento_nombre_fuente"]].drop_duplicates().shape[0] == 537
    assert prepared["trayectoria"][["provincia_nombre_fuente", "departamento_nombre_fuente"]].drop_duplicates().shape[0] == 539


@pytest.mark.parametrize("dataset", DATASETS)
def test_masked_and_no_data_rows_never_receive_ids(prepared, dataset):
    frame = prepared[dataset]
    special = frame["departamento_clave_fuente"].isin(
        UNIDENTIFIABLE_DEPARTMENT_LABELS
    )
    assert frame.loc[special, ["provincia_id", "departamento_id", "clave_territorial"]].isna().all().all()


def test_bridge_is_explicit_and_auditable():
    bridge = load_bridge(BRIDGE_PATH)
    assert len(bridge) == 11
    assert set(bridge["estado"]) == {"confirmado", "pendiente"}
    assert bridge["evidencia"].str.strip().ne("").all()
    assert bridge["tipo_diferencia"].str.strip().ne("").all()
    assert bridge["estado"].eq("confirmado").sum() == 3


def test_pending_bridges_are_not_assigned(prepared):
    bridge = load_bridge()
    pending_source_names = set(
        zip(
            bridge.loc[bridge["estado"].eq("pendiente"), "provincia_fuente"],
            bridge.loc[bridge["estado"].eq("pendiente"), "departamento_fuente"],
        )
    )
    for frame in prepared.values():
        pending_rows = frame.apply(
            lambda row: (
                row["provincia_nombre_fuente"], row["departamento_nombre_fuente"]
            )
            in pending_source_names,
            axis=1,
        )
        assert frame.loc[pending_rows, "departamento_id"].isna().all()


def test_coverage_categories_and_counts(prepared):
    coverage = build_coverage_table(prepared, load_georef(), load_bridge())
    valid = {"directo", "puente", "no_representado", "por_verificar"}
    state_columns = [f"{dataset}_estado" for dataset in DATASETS]
    assert len(coverage) == 529
    assert set(coverage[state_columns].stack()).issubset(valid)
    for column in state_columns:
        assert coverage[column].value_counts().to_dict() == {
            "directo": 503,
            "no_representado": 15,
            "por_verificar": 8,
            "puente": 3,
        }


def test_absent_territories_are_not_converted_to_zero(prepared):
    coverage = build_coverage_table(prepared, load_georef(), load_bridge())
    absent = coverage["tipo_match"].eq("no_representado")
    assert absent.sum() == 15
    assert coverage.loc[absent, "observaciones"].str.contains(
        "no equivale a valor cero", case=False
    ).all()
