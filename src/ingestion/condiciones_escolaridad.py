"""Construye condiciones territoriales 2022 con fuentes oficiales."""
from pathlib import Path
import pandas as pd
import geopandas as gpd
from src.ingestion.acceso_escolar import CENSUS_DIR, PROVINCES, _province_from_filename
from src.ingestion.educacion_departamental import normalize_text
from src.ingestion.ra_historico import load_georef, load_bridge

ROOT=Path(__file__).resolve().parents[2]
PADRON=ROOT/'data/raw/condiciones_escolaridad/padron/padron_2022.xlsx'
ACCESS=ROOT/'data/processed/acceso_escolar.parquet'
GEOJSON=ROOT/'data/processed/departamentos_argentina.geojson'
OUTPUT=ROOT/'data/processed/condiciones_escolaridad_2022.parquet'
COVERAGE=ROOT/'data/dictionaries/cobertura_condiciones_escolaridad.csv'
PADRON_BRIDGE=ROOT/'data/dictionaries/puente_nombres_padron_2022.csv'

def surface_table():
    g=gpd.read_file(GEOJSON)
    g['superficie_km2']=g.to_crs('EPSG:6933').geometry.area/1_000_000
    return g[['departamento_id','superficie_km2']]

def padron_table():
    d=pd.read_excel(PADRON,header=6,dtype={'Cueanexo':'string'})
    d=d.rename(columns={'Jurisdicción':'provincia_fuente','Departamento':'departamento_fuente','Sector':'sector','Ámbito':'ambito','Cueanexo':'cueanexo'})
    d['provincia_key']=d.provincia_fuente.map(normalize_text).replace({'ciudad de buenos aires':'ciudad autonoma de buenos aires','tierra del fuego':'tierra del fuego antartida e islas del atlantico sur'})
    d['departamento_key']=d.departamento_fuente.map(normalize_text)
    g=load_georef(); lookup=g[['provincia_key','departamento_key','departamento_id']]
    d=d.merge(lookup,on=['provincia_key','departamento_key'],how='left',validate='many_to_one')
    local_bridge=pd.read_csv(PADRON_BRIDGE,dtype={'departamento_id':'string'})
    local_bridge=local_bridge[local_bridge.estado.eq('confirmado')].copy()
    local_bridge['provincia_key']=local_bridge.provincia.map(normalize_text)
    local_bridge['departamento_key']=local_bridge.nombre_padron.map(normalize_text)
    local_bridge=local_bridge[['provincia_key','departamento_key','departamento_id']]
    historical=load_bridge()
    historical=historical[(historical.anio.astype('Int64')==2022)&historical.estado.eq('confirmado')][['provincia_key','departamento_key','departamento_id']]
    b=pd.concat([historical,local_bridge],ignore_index=True).drop_duplicates(['provincia_key','departamento_key'])
    b=b.rename(columns={'departamento_id':'bridge_id'})
    d=d.merge(b,on=['provincia_key','departamento_key'],how='left',validate='many_to_one'); d['departamento_id']=d.departamento_id.fillna(d.bridge_id)
    # El CUE oficial tiene 7 dígitos; CUE-anexo agrega 2 (00 sede, 01+ anexos).
    # Se conserva además el CUE-anexo completo como identificador de localización.
    d['establecimiento_id']=d.cueanexo.str.slice(0,7)
    offer={'inicial':[c for c in d if 'inicial' in normalize_text(c)],'primaria':[c for c in d if 'primario' in normalize_text(c)],'secundaria':[c for c in d if 'secundario' in normalize_text(c)]}
    for level,cols in offer.items():
        # En el padrón, la oferta se marca con 1 y la ausencia con una celda en blanco.
        d[f'oferta_{level}']=d[cols].apply(pd.to_numeric,errors='coerce').eq(1).any(axis=1)
    return d

def census_totals():
    rows=[]
    for path in sorted(CENSUS_DIR.glob('c2022_*_est_c4_*.xlsx')):
        province=_province_from_filename(path); book=pd.ExcelFile(path)
        for sheet in book.sheet_names[3:]:
            raw=pd.read_excel(path,sheet_name=sheet,header=None,nrows=6); title=str(raw.iloc[1,0])
            import re
            m=re.search(r',\s*(?:departamento|partido|Comuna)\s+(.+?)\.\s*Total',title,flags=re.I)
            if not m: continue
            department=m.group(1).strip(); department=f'Comuna {department}' if province=='Ciudad Autónoma de Buenos Aires' else department
            rows.append({'provincia_key':normalize_text(province),'departamento_key':normalize_text(department),'poblacion_total':pd.to_numeric(raw.iloc[4,1],errors='coerce')})
    d=pd.DataFrame(rows); g=load_georef(); return d.merge(g[['provincia_key','departamento_key','departamento_id']],on=['provincia_key','departamento_key'],how='left').dropna(subset=['departamento_id'])[['departamento_id','poblacion_total']]

def build_conditions():
    geo=load_georef()[['provincia_id','provincia_nombre','departamento_id','departamento_nombre']].merge(surface_table(),on='departamento_id',validate='one_to_one')
    acc=pd.read_parquet(ACCESS)
    pop=acc.pivot(index='departamento_id',columns='grupo_edad',values='poblacion').reset_index()
    pop['poblacion_4_11']=pop[['4-5','6-11']].sum(axis=1,min_count=2)
    pop['poblacion_12_17']=pop[['12-14','15-17']].sum(axis=1,min_count=2)
    pop['poblacion_4_17']=pop[['poblacion_4_11','poblacion_12_17']].sum(axis=1,min_count=2)
    pop=pop[['departamento_id','poblacion_4_11','poblacion_12_17','poblacion_4_17']]
    p=padron_table(); identified=p[p.departamento_id.notna()].copy()
    base=identified.drop_duplicates(['departamento_id','establecimiento_id'])
    counts=base.groupby('departamento_id').agg(establecimientos_total=('establecimiento_id','nunique'),establecimientos_estatales=('sector',lambda x:(x=='Estatal').sum()),establecimientos_privados=('sector',lambda x:(x=='Privado').sum()),establecimientos_rurales=('ambito',lambda x:(x=='Rural').sum()),establecimientos_urbanos=('ambito',lambda x:(x=='Urbano').sum())).reset_index()
    localizaciones=identified.groupby('departamento_id').cueanexo.nunique().rename('localizaciones_total')
    counts=counts.merge(localizaciones,on='departamento_id',how='left')
    for level in ['inicial','primaria','secundaria']:
        x=identified[identified[f'oferta_{level}']].groupby('departamento_id').establecimiento_id.nunique().rename(f'establecimientos_{level}')
        counts=counts.merge(x,on='departamento_id',how='left')
    out=geo.merge(pop,on='departamento_id',how='left').merge(census_totals(),on='departamento_id',how='left').merge(counts,on='departamento_id',how='left')
    out['densidad_poblacional']=out.poblacion_total/out.superficie_km2
    out['establecimientos_por_1000_poblacion_escolar']=out.establecimientos_total/(out.poblacion_4_17/1000)
    out['establecimientos_por_1000_ninos']=out.establecimientos_primaria/(out.poblacion_4_11/1000)
    out['secundarias_por_1000_adolescentes']=out.establecimientos_secundaria/(out.poblacion_12_17/1000)
    out['establecimientos_por_100_km2']=out.establecimientos_total/(out.superficie_km2/100)
    out['relacion_secundaria_primaria']=out.establecimientos_secundaria/out.establecimientos_primaria.where(out.establecimientos_primaria.gt(0))
    out['proporcion_establecimientos_rurales']=out.establecimientos_rurales/out.establecimientos_total.where(out.establecimientos_total.gt(0))
    out['anio_poblacion']=2022; out['anio_padron']=2022
    return out

def write_conditions():
    out=build_conditions(); OUTPUT.parent.mkdir(parents=True,exist_ok=True); out.to_parquet(OUTPUT,index=False)
    cov=out[['provincia_id','provincia_nombre','departamento_id','departamento_nombre']].copy()
    cov['poblacion_disponible']=out.poblacion_4_17.notna(); cov['superficie_disponible']=out.superficie_km2.notna(); cov['padron_disponible']=out.establecimientos_total.notna(); cov['contexto_socioeconomico_disponible']=False; cov['conectividad_disponible']=False; cov['oferta_educativa_disponible']=out.establecimientos_total.notna(); cov['observaciones']='Ausencia preservada. Dos variantes 2022 tienen puente oficial confirmado; seis siguen pendientes y no reciben ID. Contexto censal y conectividad pendientes.'
    cov.to_csv(COVERAGE,index=False); return out

if __name__=='__main__':
    x=write_conditions(); print(x[['poblacion_4_17','establecimientos_total']].notna().sum()); print(len(x))
