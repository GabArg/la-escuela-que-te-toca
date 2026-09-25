"""Construccion reproducible de perfiles territoriales multidimensionales.

GeoRef define el universo. Todos los joins son izquierdos y uno-a-uno; ninguna
ausencia se reemplaza por cero. Las banderas describen dimensiones separadas y
nunca se combinan en un score educativo.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.ra_2025 import add_structural_shares, aggregate_departments

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed"
OUTPUT = PROCESSED / "perfiles_territoriales.parquet"
SIGNALS_OUTPUT = PROCESSED / "senales_prioritarias_perfiles.parquet"
COVERAGE_OUTPUT = ROOT / "data/dictionaries/cobertura_perfiles_territoriales.csv"
VARIABLES_OUTPUT = ROOT / "data/dictionaries/variables_perfil_territorial.csv"
MIN_PROVINCIAL_N = 4
STRUCTURAL_CONTEXT_VARIABLES = [
    "poblacion_total", "poblacion_4_17", "densidad_poblacional",
    "proporcion_cue_rurales_2022", "localizaciones_por_1000_poblacion_escolar_2022",
    "porcentaje_hogares_internet_2022", "porcentaje_hogares_computadora_2022",
    "porcentaje_hogares_agua_red_publica_2022", "porcentaje_hogares_cloaca_2022",
    "porcentaje_viviendas_rancho_casilla_2022",
]

COMPARISON_VARIABLES = [
    "porcentaje_asistencia_15_17_2022",
    "sobreedad_2025",
    "repeticion_2025",
    "salidos_sin_pase_2025",
    "localizaciones_por_1000_poblacion_escolar_2022",
    "lengua_satisfactorio_o_avanzado_2024",
    "matematica_satisfactorio_o_avanzado_2024",
]


def _left_join(base: pd.DataFrame, addition: pd.DataFrame) -> pd.DataFrame:
    if addition["departamento_id"].duplicated().any():
        raise ValueError("El modulo fuente no tiene grano territorial unico.")
    return base.merge(addition, on="departamento_id", how="left", validate="one_to_one")


def _conditions() -> pd.DataFrame:
    source = pd.read_parquet(PROCESSED / "condiciones_escolaridad_2022.parquet")
    columns = [
        "departamento_id", "superficie_km2", "poblacion_total", "poblacion_4_17",
        "densidad_poblacional", "localizaciones_total", "establecimientos_total",
        "establecimientos_primaria", "establecimientos_secundaria",
        "relacion_secundaria_primaria", "proporcion_establecimientos_rurales",
        "anio_poblacion", "anio_padron",
    ]
    result = source[columns].copy()
    result["localizaciones_por_1000_poblacion_escolar_2022"] = (
        result["localizaciones_total"] / result["poblacion_4_17"].where(result["poblacion_4_17"].gt(0)) * 1000
    )
    result["localizaciones_por_100_km2_2022"] = (
        result["localizaciones_total"] / result["superficie_km2"].where(result["superficie_km2"].gt(0)) * 100
    )
    return result.rename(columns={
        "localizaciones_total": "localizaciones_total_2022",
        "establecimientos_total": "establecimientos_cue_total_2022",
        "establecimientos_primaria": "establecimientos_cue_primaria_2022",
        "establecimientos_secundaria": "establecimientos_cue_secundaria_2022",
        "relacion_secundaria_primaria": "relacion_cue_secundaria_primaria_2022",
        "proporcion_establecimientos_rurales": "proporcion_cue_rurales_2022",
    })


def _context() -> pd.DataFrame:
    source = pd.read_parquet(PROCESSED / "contexto_socioeconomico_2022.parquet")
    variables = [
        "porcentaje_hogares_internet", "porcentaje_hogares_computadora",
        "porcentaje_hogares_agua_red_publica", "porcentaje_hogares_cloaca",
        "porcentaje_viviendas_rancho_casilla", "porcentaje_asistencia_4_5",
        "porcentaje_asistencia_6_11", "porcentaje_asistencia_12_14",
        "porcentaje_asistencia_15_17",
    ]
    result = source[["departamento_id", *variables]].copy()
    return result.rename(columns={name: f"{name}_2022" for name in variables})


def _access() -> pd.DataFrame:
    source = pd.read_parquet(PROCESSED / "acceso_escolar.parquet")
    values = source.pivot(index="departamento_id", columns="grupo_edad", values="indicador_acceso")
    values.columns = [f"cociente_matricula_poblacion_{str(c).replace('-', '_')}_2022" for c in values]
    return values.reset_index()


def _trajectory() -> pd.DataFrame:
    source = pd.read_parquet(PROCESSED / "ra_2025_analitico.parquet")
    current = add_structural_shares(source, aggregate_departments(source))
    keep = [
        "departamento_id", "matricula_total", "proporcion_matricula_rural",
        "proporcion_matricula_estatal", "proporcion_repetidores_sobre_matricula",
        "proporcion_sobreedad_sobre_matricula", "proporcion_promovidos_sobre_ultimo",
        "proporcion_no_promovidos_sobre_ultimo", "proporcion_salidos_sin_pase_sobre_inicial",
    ]
    result = current[keep].rename(columns={
        "matricula_total": "matricula_total_2025",
        "proporcion_matricula_rural": "proporcion_matricula_rural_2025",
        "proporcion_matricula_estatal": "proporcion_matricula_estatal_2025",
        "proporcion_repetidores_sobre_matricula": "repeticion_2025",
        "proporcion_sobreedad_sobre_matricula": "sobreedad_2025",
        "proporcion_promovidos_sobre_ultimo": "promocion_2025",
        "proporcion_no_promovidos_sobre_ultimo": "no_promocion_2025",
        "proporcion_salidos_sin_pase_sobre_inicial": "salidos_sin_pase_2025",
    })

    historical = pd.read_parquet(PROCESSED / "ra_2011_2025_long.parquet")
    from src.analysis.ra_historico import build_indicators
    indicators = build_indicators(historical)
    metrics = ["proporcion_repitentes", "proporcion_sobreedad", "proporcion_salidos_sin_pase"]
    medians = indicators.groupby("departamento_id")[metrics].median().add_suffix("_mediana_historica")
    signals = pd.read_parquet(PROCESSED / "senales_ra_2011_2025.parquet")
    signal_parts = []
    for value, suffix in [
        ("clasificacion", "clasificacion_historica"),
        ("n_anios", "n_anios_historicos"),
        ("rho_spearman", "tendencia_spearman_historica"),
        ("cambio_mediana_ultimos_vs_primeros", "cambio_mediana_historica"),
    ]:
        wide = signals.pivot(index="departamento_id", columns="indicador", values=value)
        wide.columns = [f"{c}_{suffix}" for c in wide]
        signal_parts.append(wide)
    classifications = pd.concat(signal_parts, axis=1)
    result = result.merge(medians, on="departamento_id", how="left", validate="one_to_one")
    return result.merge(classifications, on="departamento_id", how="left", validate="one_to_one")


def _learning() -> pd.DataFrame:
    source = pd.read_parquet(PROCESSED / "aprender_analitico.parquet")
    identity = "departamento_id"
    parts = []
    for area in ["Lengua", "Matematica"]:
        area_data = source[source["area"].eq(area)].copy()
        wide = area_data.pivot(index=identity, columns="indicador", values="valor")
        prefix = area.lower()
        wide.columns = [f"{prefix}_{c}_2024" for c in wide]
        status = area_data.groupby(identity)["estado_cobertura"].first().rename(f"aprendizaje_{prefix}_cobertura")
        wide = wide.join(status)
        sat = f"{prefix}_satisfactorio_2024"
        advanced = f"{prefix}_avanzado_2024"
        wide[f"{prefix}_satisfactorio_o_avanzado_2024"] = wide[sat] + wide[advanced]
        parts.append(wide.reset_index())
    return parts[0].merge(parts[1], on=identity, how="outer", validate="one_to_one")


def add_comparisons(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for variable in COMPARISON_VARIABLES:
        observed = result[variable].notna()
        count = result.groupby("provincia_id")[variable].transform("count")
        median = result.groupby("provincia_id")[variable].transform("median").where(count.ge(MIN_PROVINCIAL_N))
        result[f"{variable}__mediana_provincial"] = median
        result[f"{variable}__diferencia_mediana_provincial"] = result[variable] - median
        quartile = result.groupby("provincia_id")[variable].rank(pct=True).mul(4).apply(np.ceil).clip(1, 4)
        result[f"{variable}__cuartil_provincial"] = quartile.where(observed & count.ge(MIN_PROVINCIAL_N)).astype("Int64")
        national_median = result[variable].median()
        result[f"{variable}__mediana_nacional"] = national_median
        position = pd.Series(pd.NA, index=result.index, dtype="string")
        position.loc[observed & result[variable].lt(national_median)] = "debajo"
        position.loc[observed & result[variable].eq(national_median)] = "igual"
        position.loc[observed & result[variable].gt(national_median)] = "encima"
        result[f"{variable}__respecto_mediana_nacional"] = position
    return result


def _flag(series: pd.Series, condition: pd.Series) -> pd.Series:
    result = pd.Series(pd.NA, index=series.index, dtype="boolean")
    result.loc[series.notna()] = condition.loc[series.notna()]
    return result


def add_coverage_and_flags(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["cobertura_territorio"] = True
    result["cobertura_oferta"] = result["localizaciones_total_2022"].notna()
    result["cobertura_acceso"] = result["porcentaje_asistencia_15_17_2022"].notna()
    result["cobertura_trayectoria"] = result["sobreedad_2025"].notna()
    result["cobertura_contexto"] = result["porcentaje_hogares_internet_2022"].notna()
    result["cobertura_aprendizaje_lengua"] = result["aprendizaje_lengua_cobertura"].eq("completo")
    result["cobertura_aprendizaje_matematica"] = result["aprendizaje_matematica_cobertura"].eq("completo")
    result["cobertura_serie_historica"] = result["proporcion_sobreedad_clasificacion_historica"].notna()
    dimensions = [c for c in result if c.startswith("cobertura_") and c not in {"cobertura_territorio"}]
    result["dimensiones_disponibles"] = result[dimensions].sum(axis=1)
    result["calidad_total_del_perfil"] = pd.cut(
        result["dimensiones_disponibles"], bins=[-1, 2, 5, len(dimensions)],
        labels=["Cobertura baja", "Cobertura media", "Alta cobertura"],
    ).astype("string")

    q25_assistance = result["porcentaje_asistencia_15_17_2022"].quantile(.25)
    q25_offer = result["localizaciones_por_1000_poblacion_escolar_2022"].quantile(.25)
    q75_housing = result["porcentaje_viviendas_rancho_casilla_2022"].quantile(.75)
    result["bandera_asistencia_15_17_baja_relativa"] = _flag(
        result["porcentaje_asistencia_15_17_2022"], result["porcentaje_asistencia_15_17_2022"].le(q25_assistance))
    history = result["proporcion_sobreedad_clasificacion_historica"]
    result["bandera_sobreedad_persistente_alta"] = _flag(history, history.eq("Persistente alto"))
    classes = [c for c in result if c.endswith("_clasificacion_historica")]
    any_history = result[classes].notna().any(axis=1)
    deteriorating = result[classes].eq("Deterioro sostenido").any(axis=1)
    result["bandera_deterioro_sostenido_trayectoria"] = pd.Series(pd.NA, index=result.index, dtype="boolean")
    result.loc[any_history, "bandera_deterioro_sostenido_trayectoria"] = deteriorating[any_history]
    result["bandera_baja_oferta_localizaciones_relativa"] = _flag(
        result["localizaciones_por_1000_poblacion_escolar_2022"],
        result["localizaciones_por_1000_poblacion_escolar_2022"].le(q25_offer))
    result["bandera_vulnerabilidad_habitacional_relativa"] = _flag(
        result["porcentaje_viviendas_rancho_casilla_2022"],
        result["porcentaje_viviendas_rancho_casilla_2022"].ge(q75_housing))
    aprender_present = result[["aprendizaje_lengua_cobertura", "aprendizaje_matematica_cobertura"]].notna().any(axis=1)
    result["bandera_dato_aprender_parcial"] = pd.Series(pd.NA, index=result.index, dtype="boolean")
    result.loc[aprender_present, "bandera_dato_aprender_parcial"] = (
        result.loc[aprender_present, ["aprendizaje_lengua_cobertura", "aprendizaje_matematica_cobertura"]]
        .eq("parcial").any(axis=1)
    )
    result["bandera_cobertura_dato_baja"] = result["calidad_total_del_perfil"].eq("Cobertura baja").astype("boolean")
    return result


def build_profiles() -> pd.DataFrame:
    base = pd.read_parquet(PROCESSED / "territorios_argentina.parquet")
    for module in (_conditions(), _context(), _access(), _trajectory(), _learning()):
        drop = [c for c in module if c != "departamento_id" and c in base]
        base = _left_join(base, module.drop(columns=drop))
    return add_coverage_and_flags(add_comparisons(base))


SIGNAL_RULES = [
    ("bandera_cobertura_dato_baja", 1, "Advertencia de cobertura / calidad documental", "Calidad documental", "Cobertura documental baja"),
    ("bandera_dato_aprender_parcial", 2, "Advertencia de cobertura / calidad documental", "Cobertura de Aprender", "Aprender tiene cobertura parcial"),
    ("bandera_deterioro_sostenido_trayectoria", 3, "Señal educativa", "Trayectoria", "Deterioro histórico sostenido"),
    ("bandera_sobreedad_persistente_alta", 4, "Señal educativa", "Trayectoria", "Sobreedad persistentemente alta"),
    ("bandera_asistencia_15_17_baja_relativa", 5, "Señal educativa", "Acceso / asistencia", "Asistencia 15–17 relativamente baja"),
    ("bandera_baja_oferta_localizaciones_relativa", 6, "Señal educativa", "Oferta", "Baja oferta relativa de localizaciones"),
    ("bandera_vulnerabilidad_habitacional_relativa", 7, "Señal educativa", "Contexto", "Rancho/casilla relativamente alto"),
]


def prioritized_signals(profiles: pd.DataFrame) -> pd.DataFrame:
    thresholds = {
        "asistencia": profiles["porcentaje_asistencia_15_17_2022"].quantile(.25),
        "oferta": profiles["localizaciones_por_1000_poblacion_escolar_2022"].quantile(.25),
        "vivienda": profiles["porcentaje_viviendas_rancho_casilla_2022"].quantile(.75),
    }

    def evidence(row: pd.Series, flag: str) -> str:
        if flag == "bandera_cobertura_dato_baja":
            return f"dimensiones_disponibles={int(row.dimensiones_disponibles)}; categoria={row.calidad_total_del_perfil}"
        if flag == "bandera_dato_aprender_parcial":
            return f"lengua={row.aprendizaje_lengua_cobertura}; matematica={row.aprendizaje_matematica_cobertura}"
        if flag == "bandera_deterioro_sostenido_trayectoria":
            columns = [c for c in row.index if c.endswith("_clasificacion_historica")]
            active = [c.removesuffix("_clasificacion_historica") for c in columns if row[c] == "Deterioro sostenido"]
            return "clasificacion=Deterioro sostenido; indicadores=" + ";".join(active)
        if flag == "bandera_sobreedad_persistente_alta":
            return f"clasificacion={row.proporcion_sobreedad_clasificacion_historica}"
        if flag == "bandera_asistencia_15_17_baja_relativa":
            return f"valor={row.porcentaje_asistencia_15_17_2022:.4f}; umbral_P25={thresholds['asistencia']:.4f}"
        if flag == "bandera_baja_oferta_localizaciones_relativa":
            return f"valor={row.localizaciones_por_1000_poblacion_escolar_2022:.4f}; umbral_P25={thresholds['oferta']:.4f}"
        if flag == "bandera_vulnerabilidad_habitacional_relativa":
            return f"valor={row.porcentaje_viviendas_rancho_casilla_2022:.4f}; umbral_P75={thresholds['vivienda']:.4f}"
        raise ValueError(f"Bandera sin evidencia definida: {flag}")

    rows = []
    for flag, order, signal_type, dimension, label in SIGNAL_RULES:
        for index in profiles.index[profiles[flag].fillna(False)]:
            row = profiles.loc[index]
            rows.append({"departamento_id": row.departamento_id, "provincia_nombre": row.provincia_nombre,
                         "departamento_nombre": row.departamento_nombre, "orden_regla": order,
                         "tipo_senal": signal_type, "dimension": dimension,
                         "senal": label, "evidencia": evidence(row, flag),
                         "nivel_confianza": "Alto" if flag in {"bandera_cobertura_dato_baja", "bandera_dato_aprender_parcial"} else "Medio"})
    signals = pd.DataFrame(rows)
    if signals.empty:
        return signals
    signals = signals.sort_values(["departamento_id", "orden_regla"])
    signals["prioridad"] = signals.groupby("departamento_id").cumcount() + 1
    return signals[signals["prioridad"].le(3)].drop(columns="orden_regla")


def validate_profiles(frame: pd.DataFrame) -> None:
    if len(frame) != 529 or frame["departamento_id"].nunique() != 529:
        raise ValueError("El perfil debe conservar exactamente las 529 unidades GeoRef.")
    if frame["clave_territorial"].isna().any() or frame["clave_territorial"].duplicated().any():
        raise ValueError("La clave territorial debe ser completa y unica.")
    percentage = [c for c in frame if "__" not in c and (c.startswith("porcentaje_") or "_satisfactorio_" in c or any(level in c for level in ["_basico_2024", "_avanzado_2024"]))]
    for column in percentage:
        if not frame[column].dropna().between(0, 100).all():
            raise ValueError(f"{column} fuera de rango.")
    partial_l = frame["aprendizaje_lengua_cobertura"].eq("parcial")
    partial_m = frame["aprendizaje_matematica_cobertura"].eq("parcial")
    if frame.loc[partial_l, [c for c in frame if c.startswith("lengua_") and c.endswith("_2024")]].notna().any().any():
        raise ValueError("Aprendizaje parcial de Lengua convertido en porcentaje.")
    if frame.loc[partial_m, [c for c in frame if c.startswith("matematica_") and c.endswith("_2024")]].notna().any().any():
        raise ValueError("Aprendizaje parcial de Matematica convertido en porcentaje.")
    if any(c in frame for c in ["score", "ranking", "puesto"]):
        raise ValueError("El perfil no puede contener score ni ranking ordinal.")


def write_coverage(profiles: pd.DataFrame, path: Path = COVERAGE_OUTPUT) -> pd.DataFrame:
    columns = ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre",
               "cobertura_territorio", "cobertura_oferta", "cobertura_acceso",
               "cobertura_trayectoria", "cobertura_contexto", "cobertura_aprendizaje_lengua",
               "cobertura_aprendizaje_matematica", "cobertura_serie_historica",
               "calidad_total_del_perfil"]
    coverage = profiles[columns].copy()
    coverage.to_csv(path, index=False)
    return coverage


def write_variable_metadata(profiles: pd.DataFrame, path: Path = VARIABLES_OUTPUT) -> pd.DataFrame:
    """Documenta todas las columnas; los derivados se describen por regla nominal."""
    rows = []
    for variable in profiles.columns:
        dimension, source, year, unit, direction = "Calidad del dato", "Construccion interna", "varios", "categoria", "descriptivo"
        description, universe, kind, comparability, warning = variable.replace("_", " "), "departamento o equivalente", "metadata", "segun fuente", "No usar para score."
        if variable in {"provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "clave_territorial"}:
            dimension, source, year, unit, kind = "Territorio", "GeoRef Argentina", "consulta vigente", "identificador o nombre", "identificador"
            warning = "Clave territorial es interna cuando corresponda; los IDs GeoRef se preservan como texto."
        elif variable.startswith("bandera_"):
            dimension, source, year, unit, kind = "Señal descriptiva", "Reglas del perfil", "varios", "booleano nullable", "bandera"
            warning = "No implica causalidad ni valoración integral."
        elif variable.startswith("cobertura_") or variable in {"dimensiones_disponibles", "calidad_total_del_perfil"}:
            dimension, source, year, unit, kind = "Calidad del dato", "Outputs integrados", "varios", "disponibilidad", "metadata"
            warning = "Mide completitud documental, no calidad educativa."
        elif "2024" in variable or variable.startswith("aprendizaje_"):
            dimension, source, year, unit, kind = "Aprendizaje", "Aprender Secundaria 2024", "2024", "porcentaje o categoria", "resultado"
            direction = "no_interpretable_sin_contexto"
            warning = "Solo con distribución completa; censal no equivale a participación completa."
        elif "historica" in variable or variable in {"sobreedad_2025", "repeticion_2025", "promocion_2025", "no_promocion_2025", "salidos_sin_pase_2025"}:
            dimension, source, year, unit, kind = "Trayectoria", "Relevamiento Anual", "2011-2025", "proporcion o categoria", "resultado"
            direction = "mayor_generalmente_desfavorable" if variable not in {"promocion_2025"} else "mayor_generalmente_favorable"
            warning = "Cocientes internos documentados; no son tasas causales."
        elif variable in {"matricula_total_2025", "proporcion_matricula_rural_2025", "proporcion_matricula_estatal_2025"}:
            dimension, source, year, unit, kind = "Territorio", "Relevamiento Anual", "2025", "conteo o proporcion", "estructura"
            direction = "descriptivo"
        elif variable.startswith("porcentaje_asistencia_") or variable.startswith("cociente_matricula_poblacion_"):
            dimension, source, year, unit, kind = "Acceso / asistencia", "Censo 2022 y RA 2022", "2022", "porcentaje o cociente", "indicador"
            direction = "mayor_generalmente_favorable" if variable.startswith("porcentaje_asistencia") else "no_interpretable_sin_contexto"
            warning = "El cociente matrícula/población no es tasa oficial de escolarización."
        elif variable.startswith("porcentaje_"):
            dimension, source, year, unit, kind = "Contexto socioeconomico", "Censo 2022", "2022", "porcentaje", "estructura"
            direction = "descriptivo"
            warning = "Condición estructural; no es causa demostrada."
        elif any(token in variable for token in ["localizaciones", "establecimientos_cue", "relacion_cue", "proporcion_cue"]):
            dimension, source, year, unit, kind = "Oferta", "Padrón oficial 2022", "2022", "conteo, cociente o proporcion", "estructura"
            direction = "mayor_no_implica_mejor"
            warning = "CUE y CUE-anexo no son intercambiables; no mide cupos ni distancia."
        elif variable in {"superficie_km2", "poblacion_total", "poblacion_4_17", "densidad_poblacional", "anio_poblacion", "anio_padron"}:
            dimension, source, year, unit, kind = "Territorio", "GeoRef / Censo / Padrón", "2022", "conteo, km2 o densidad", "estructura"
            direction = "descriptivo"
        if "__mediana" in variable or "__diferencia" in variable or "__cuartil" in variable or "__respecto" in variable:
            kind, source, warning = "comparacion descriptiva", "Derivación del perfil", "No es ranking ordinal; mediana provincial exige n>=4."
        rows.append({"variable": variable, "dimension": dimension, "descripcion": description,
                     "fuente": source, "anio": year, "unidad": unit, "universo": universe,
                     "tipo": kind, "comparabilidad": comparability,
                     "direccion_interpretativa": direction, "cobertura": int(profiles[variable].notna().sum()),
                     "advertencia": warning})
    metadata = pd.DataFrame(rows)
    metadata.to_csv(path, index=False)
    return metadata


def write_profiles(output: Path = OUTPUT, signals_output: Path = SIGNALS_OUTPUT) -> tuple[pd.DataFrame, pd.DataFrame]:
    profiles = build_profiles()
    validate_profiles(profiles)
    signals = prioritized_signals(profiles)
    output.parent.mkdir(parents=True, exist_ok=True)
    profiles.to_parquet(output, index=False)
    signals.to_parquet(signals_output, index=False)
    write_coverage(profiles)
    write_variable_metadata(profiles)
    return profiles, signals


if __name__ == "__main__":
    profiles, signals = write_profiles()
    print(f"perfiles={len(profiles)} columnas={len(profiles.columns)} senales={len(signals)}")
