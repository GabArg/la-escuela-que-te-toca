"""Asociaciones descriptivas entre condiciones 2022 y señales RA 2025."""
import pandas as pd
from src.analysis.ra_2025 import aggregate_departments
from src.ingestion.condiciones_escolaridad import padron_table

def analysis_table():
    c=pd.read_parquet('data/processed/condiciones_escolaridad_2022.parquet')
    r=aggregate_departments(pd.read_parquet('data/processed/ra_2025_analitico.parquet'))
    return c.merge(r[['departamento_id','proporcion_repetidores_sobre_matricula','proporcion_sobreedad_sobre_matricula','proporcion_salidos_sin_pase_sobre_inicial']],on='departamento_id',how='inner',validate='one_to_one')

def correlations():
    d=analysis_table(); structural=['densidad_poblacional','establecimientos_por_1000_poblacion_escolar','establecimientos_por_100_km2','relacion_secundaria_primaria']; outcomes=['proporcion_repetidores_sobre_matricula','proporcion_sobreedad_sobre_matricula','proporcion_salidos_sin_pase_sobre_inicial']
    rows=[]
    for x in structural:
        for y in outcomes:
            z=d[[x,y]].dropna(); rows.append({'condicion':x,'resultado':y,'n':len(z),'spearman':z[x].corr(z[y],method='spearman')})
    return pd.DataFrame(rows)

def sensitivity_localizations():
    """Compara el CUE de 7 dígitos con la unidad oficial CUE-anexo."""
    conditions=pd.read_parquet('data/processed/condiciones_escolaridad_2022.parquet')
    p=padron_table(); p=p[p.departamento_id.notna()].copy()
    local=p.drop_duplicates(['departamento_id','cueanexo'])
    grouped=local.groupby('departamento_id').agg(
        localizaciones=('cueanexo','nunique'),
        localizaciones_rurales=('ambito',lambda x:(x=='Rural').sum()),
    )
    for level in ['primaria','secundaria']:
        grouped[f'localizaciones_{level}']=local[local[f'oferta_{level}']].groupby('departamento_id').cueanexo.nunique()
    d=conditions.merge(grouped.reset_index(),on='departamento_id',how='left',validate='one_to_one')
    d['relacion_secundaria_primaria_localizaciones']=d.localizaciones_secundaria/d.localizaciones_primaria.where(d.localizaciones_primaria.gt(0))
    d['localizaciones_por_1000_poblacion_escolar']=d.localizaciones/(d.poblacion_4_17/1000)
    d['localizaciones_por_100_km2']=d.localizaciones/(d.superficie_km2/100)
    d['proporcion_localizaciones_rurales']=d.localizaciones_rurales/d.localizaciones.where(d.localizaciones.gt(0))
    return d
