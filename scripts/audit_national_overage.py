"""Audita el agregado de sobreedad RA usado en el storytelling.

Compara el cálculo vigente —solo filas con departamento GeoRef— con el
agregado de todos los registros publicados para un universo de componentes
comparable entre 2011 y 2025. No imputa ni redistribuye filas enmascaradas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ingestion.ra_historico import (
    VARIABLES,
    _sum_preserving_null,
    attach_territory,
    load_bridge,
    load_georef,
    load_raw,
)


AUDIT_YEARS = (2011, 2025)


@dataclass(frozen=True)
class OverageAudit:
    anio: int
    numerador_identificado: float
    denominador_identificado: float
    ratio_identificado: float
    numerador_publicado: float
    denominador_publicado: float
    ratio_publicado: float
    filas_originales: int
    filas_departamento_identificado: int
    filas_excluidas: int
    filas_enmascaradas_excluidas: int
    filas_sin_datos_excluidas: int
    filas_por_verificar_excluidas: int
    departamentos_identificados: int
    provincias_identificadas: int
    provincias_publicadas: int
    numerador_excluido: float
    denominador_excluido: float


def audit_overage_year(year: int) -> OverageAudit:
    """Devuelve conteos verificables para un año de Matrícula RA."""
    raw = load_raw(year, "matricula")
    attached = attach_territory(raw, year, load_georef(), load_bridge())
    numerator = _sum_preserving_null(attached, VARIABLES["matricula"]["sobreedad"])
    denominator = _sum_preserving_null(
        attached, VARIABLES["matricula"]["matricula_grados_comparables"]
    )
    identified = attached["departamento_id"].notna()
    excluded = ~identified

    identified_numerator = float(numerator.loc[identified].sum(min_count=1))
    identified_denominator = float(denominator.loc[identified].sum(min_count=1))
    published_numerator = float(numerator.sum(min_count=1))
    published_denominator = float(denominator.sum(min_count=1))

    statuses = attached.loc[excluded, "tipo_match"].value_counts()
    return OverageAudit(
        anio=year,
        numerador_identificado=identified_numerator,
        denominador_identificado=identified_denominator,
        ratio_identificado=identified_numerator / identified_denominator,
        numerador_publicado=published_numerator,
        denominador_publicado=published_denominator,
        ratio_publicado=published_numerator / published_denominator,
        filas_originales=len(raw),
        filas_departamento_identificado=int(identified.sum()),
        filas_excluidas=int(excluded.sum()),
        filas_enmascaradas_excluidas=int(statuses.get("enmascarado", 0)),
        filas_sin_datos_excluidas=int(statuses.get("sin datos", 0)),
        filas_por_verificar_excluidas=int(statuses.get("por_verificar", 0)),
        departamentos_identificados=attached.loc[identified, "departamento_id"].nunique(),
        provincias_identificadas=attached.loc[identified, "provincia_id"].nunique(),
        provincias_publicadas=raw["provincia"].nunique(),
        numerador_excluido=published_numerator - identified_numerator,
        denominador_excluido=published_denominator - identified_denominator,
    )


def audit_table() -> pd.DataFrame:
    return pd.DataFrame(asdict(audit_overage_year(year)) for year in AUDIT_YEARS)


def _print_audit(audit: OverageAudit) -> None:
    print(f"\nRA {audit.anio}")
    print(f"  numerador actual (territorios identificados): {audit.numerador_identificado:,.0f}")
    print(f"  denominador actual (territorios identificados): {audit.denominador_identificado:,.0f}")
    print(f"  ratio actual: {audit.ratio_identificado:.8%}")
    print(f"  filas originales: {audit.filas_originales:,}")
    print(f"  filas con departamento identificado: {audit.filas_departamento_identificado:,}")
    print(f"  filas excluidas: {audit.filas_excluidas:,}")
    print(f"    Enmascarado: {audit.filas_enmascaradas_excluidas:,}")
    print(f"    Sin datos: {audit.filas_sin_datos_excluidas:,}")
    print(f"    nombre por verificar: {audit.filas_por_verificar_excluidas:,}")
    print(
        "  cobertura territorial identificada: "
        f"{audit.departamentos_identificados} departamentos/unidades equivalentes; "
        f"{audit.provincias_identificadas}/{audit.provincias_publicadas} jurisdicciones"
    )
    print(f"  numerador publicado excluido hoy: {audit.numerador_excluido:,.0f}")
    print(f"  denominador publicado excluido hoy: {audit.denominador_excluido:,.0f}")
    print(f"  numerador nacional publicado: {audit.numerador_publicado:,.0f}")
    print(f"  denominador nacional publicado: {audit.denominador_publicado:,.0f}")
    print(f"  ratio nacional publicado: {audit.ratio_publicado:.8%}")
    print(f"  diferencia frente al cálculo actual: {(audit.ratio_publicado - audit.ratio_identificado):.8%}")


def main() -> None:
    print("Universo: Educación Común; sectores Estatal y Privado; ámbitos Urbano y Rural;")
    print("años/categorías 1–12 y 13/14 presentes con la misma definición en 2011–2025.")
    print("Las filas enmascaradas se suman como agregados publicados; no se asignan a departamentos.")
    for year in AUDIT_YEARS:
        _print_audit(audit_overage_year(year))


if __name__ == "__main__":
    main()
