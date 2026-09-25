"""Audita el contraste de salidos sin pase Ramón Lista–Quebrachos."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis.ra_2025 import GRADES, prepare_trayectoria


SOURCE_PATH = ROOT / "data/processed/educacion_departamental/trayectoria_2025.parquet"
SOURCE_YEAR = 2025
MOVEMENT_PERIOD = "ciclo lectivo 2024 (informado en RA 2025)"
TERRITORIES = {"34063": "Ramón Lista", "86140": "Quebrachos"}


@dataclass(frozen=True)
class SalidosAudit:
    departamento_id: str
    territorio: str
    provincia: str
    numerador: float
    denominador: float
    ratio: float
    anio_fuente: int
    periodo_movimiento: str
    universo: str
    celdas_publicadas: int
    celdas_identificadas: int
    sectores: str
    ambitos: str
    pares_componentes_ausentes: str
    cobertura: str


def audit_territory(territory_id: str, source_path: Path = SOURCE_PATH) -> SalidosAudit:
    source = pd.read_parquet(source_path)
    rows = source.loc[source["departamento_id"].astype(str).eq(str(territory_id))].copy()
    if rows.empty:
        raise ValueError(f"No hay filas publicadas identificadas para {territory_id}.")
    prepared = prepare_trayectoria(rows)
    numerator = float(prepared["trayectoria_ssp_total"].sum(min_count=1))
    denominator = float(prepared["trayectoria_inicial_total"].sum(min_count=1))
    if denominator <= 0:
        raise ValueError(f"El denominador no es positivo para {territory_id}.")

    missing_pairs = []
    for grade in GRADES:
        initial_missing = rows[f"inicial_{grade}"].isna().all()
        salidos_missing = rows[f"ssp_{grade}"].isna().all()
        if initial_missing and salidos_missing:
            missing_pairs.append(grade)
        elif initial_missing != salidos_missing:
            raise ValueError(f"Faltante no pareado en la categoría {grade} de {territory_id}.")

    first = rows.iloc[0]
    coverage = (
        "filas identificadas por nombre normalizado; numerador y denominador disponibles "
        "en todas las celdas publicadas; faltantes pareados no se imputan"
    )
    return SalidosAudit(
        departamento_id=str(territory_id),
        territorio=str(first["departamento_nombre"]),
        provincia=str(first["provincia_nombre"]),
        numerador=numerator,
        denominador=denominator,
        ratio=numerator / denominator,
        anio_fuente=SOURCE_YEAR,
        periodo_movimiento=MOVEMENT_PERIOD,
        universo=(
            "Educación Común; categorías 1–12, 13/14 y organización no graduada (20); "
            "sectores/ámbitos publicados para el territorio"
        ),
        celdas_publicadas=len(rows),
        celdas_identificadas=int(rows["departamento_id"].notna().sum()),
        sectores="; ".join(sorted(rows["sector"].dropna().unique())),
        ambitos="; ".join(sorted(rows["ambito"].dropna().unique())),
        pares_componentes_ausentes="; ".join(missing_pairs) if missing_pairs else "ninguno",
        cobertura=coverage,
    )


def audit_table() -> pd.DataFrame:
    return pd.DataFrame(asdict(audit_territory(territory_id)) for territory_id in TERRITORIES)


def main() -> None:
    audits = [audit_territory(territory_id) for territory_id in TERRITORIES]
    print(
        "Definición oficial: estudiantes que dejaron de asistir al establecimiento durante "
        "el ciclo lectivo y fueron dados de baja sin solicitar pase a otra escuela."
    )
    print("Indicador del proyecto: suma de salidos sin pase / suma de matrícula inicial.")
    for audit in audits:
        print(f"\n{audit.territorio}, {audit.provincia}")
        print(f"  numerador: {audit.numerador:,.0f}")
        print(f"  denominador: {audit.denominador:,.0f}")
        print(f"  ratio: {audit.ratio:.8%}")
        print(f"  año fuente: RA {audit.anio_fuente}")
        print(f"  período real del movimiento: {audit.periodo_movimiento}")
        print(f"  universo: {audit.universo}")
        print(
            f"  cobertura: {audit.celdas_identificadas}/{audit.celdas_publicadas} celdas "
            f"identificadas; sector {audit.sectores}; ámbito {audit.ambitos}"
        )
        print(f"  componentes ausentes en numerador y denominador: {audit.pares_componentes_ausentes}")
    gap = abs(audits[0].ratio - audits[1].ratio) * 100
    print(f"\nDiferencia absoluta: {gap:.8f} puntos porcentuales ({gap:.2f} pp)")
    print("Salidos sin pase no equivale automáticamente a abandono escolar.")


if __name__ == "__main__":
    main()
