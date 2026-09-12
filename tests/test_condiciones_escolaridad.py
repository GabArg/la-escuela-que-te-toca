import pandas as pd
import pytest
from src.ingestion.condiciones_escolaridad import build_conditions
from src.ingestion.condiciones_escolaridad import padron_table
from src.analysis.condiciones_escolaridad import sensitivity_localizations

@pytest.fixture(scope='module')
def conditions():
    return build_conditions()

def test_conditions_integrity(conditions):
    d=conditions; assert len(d)==529; assert d.departamento_id.is_unique
    assert (d.superficie_km2>0).all(); assert (d.poblacion_total.dropna()>=0).all()
    counts=[c for c in d if c.startswith('establecimientos_') and not c.startswith('establecimientos_por')]
    assert (d[counts].stack()>=0).all(); assert d.anio_poblacion.eq(2022).all(); assert d.anio_padron.eq(2022).all()

def test_derived_indicators_and_nulls(conditions):
    d=conditions; row=d.dropna(subset=['establecimientos_total','poblacion_4_17']).iloc[0]
    assert abs(row.establecimientos_por_1000_poblacion_escolar-row.establecimientos_total/(row.poblacion_4_17/1000))<1e-12
    missing=d.establecimientos_total.isna(); assert missing.any(); assert d.loc[missing,'establecimientos_total'].isna().all()
    zero=d.establecimientos_primaria.eq(0); assert d.loc[zero,'relacion_secundaria_primaria'].isna().all()

def test_coverage_documented(conditions):
    d=conditions; c=pd.read_csv('data/dictionaries/cobertura_condiciones_escolaridad.csv')
    assert len(c)==529; assert c.departamento_id.nunique()==529
    assert c.poblacion_disponible.sum()==d.poblacion_4_17.notna().sum()

def test_cue_and_cue_anexo_structure():
    p=padron_table()
    assert p.cueanexo.str.fullmatch(r'\d{9}').all()
    assert p.establecimiento_id.str.fullmatch(r'\d{7}').all()
    assert p.establecimiento_id.eq(p.cueanexo.str[:-2]).all()

def test_localization_sensitivity_preserves_nulls():
    d=sensitivity_localizations()
    assert d.departamento_id.is_unique
    assert (d.localizaciones.dropna()>=d.establecimientos_total.dropna()).all()
    missing=d.localizaciones.isna()
    assert d.loc[missing,'localizaciones_por_100_km2'].isna().all()
