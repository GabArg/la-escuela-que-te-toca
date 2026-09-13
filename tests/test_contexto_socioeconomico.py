import pandas as pd
import pytest

from src.ingestion.contexto_socioeconomico import BRIDGE, _attach_territory, build_context, load_household_context
from src.ingestion.ra_historico import load_georef


@pytest.fixture(scope="module")
def context():
    return build_context()


def test_territorial_integrity(context):
    geo = load_georef()
    assert len(context) == 529
    assert context.departamento_id.is_unique
    assert set(context.departamento_id) == set(geo.departamento_id)


def test_counts_and_denominators(context):
    counts = [c for c in context if c.startswith(("hogares_", "viviendas_", "total_", "asiste_"))]
    assert (context[counts].stack() >= 0).all()
    for group in ["4_5", "6_11", "12_14", "15_17"]:
        observed = context[f"porcentaje_asistencia_{group}"].notna()
        assert context.loc[observed, f"total_{group}"].gt(0).all()
        assert context.loc[observed, f"asiste_{group}"].le(context.loc[observed, f"total_{group}"]).all()
        complete = context[[f"total_{group}", f"asiste_{group}", f"no_asiste_asistio_{group}", f"nunca_asistio_{group}"]].dropna()
        assert (complete[f"total_{group}"] == complete[[f"asiste_{group}", f"no_asiste_asistio_{group}", f"nunca_asistio_{group}"]].sum(axis=1)).all()


def test_percentages_are_valid_and_nulls_preserved(context):
    percentages = [c for c in context if c.startswith("porcentaje_")]
    assert context[percentages].stack().between(0, 100).all()
    missing = context.hogares_total.isna()
    assert missing.any()
    assert context.loc[missing, "porcentaje_hogares_internet"].isna().all()


def test_confirmed_bridges_match_georef():
    bridge = pd.read_csv(BRIDGE, dtype={"departamento_id": "string"})
    geo = load_georef().set_index("departamento_id")
    for row in bridge[bridge.estado.eq("confirmado")].itertuples():
        assert row.departamento_id in geo.index
        assert geo.loc[row.departamento_id, "departamento_nombre"] == row.nombre_georef
    assert bridge[bridge.estado.eq("pendiente")].departamento_id.notna().all()
    source = _attach_territory(load_household_context())
    pending = bridge[bridge.estado.eq("pendiente")].nombre_censo.tolist()
    assert source[source.departamento_fuente.str.replace("\u00a0", " ").isin(pending)].departamento_id.isna().all()


def test_coverage_and_universes_documented(context):
    coverage = pd.read_csv("data/dictionaries/cobertura_contexto_socioeconomico.csv")
    dictionary = pd.read_csv("data/dictionaries/variables_contexto_socioeconomico.csv")
    assert len(coverage) == len(context)
    assert coverage.departamento_id.nunique() == 529
    assert dictionary.universo.notna().all() and dictionary.denominador.notna().all()
    assert not dictionary.query("incorporada == 'no'").variable_estandar.isin(context.columns).any()
    assert coverage.internet.sum() == context.porcentaje_hogares_internet.notna().sum()
