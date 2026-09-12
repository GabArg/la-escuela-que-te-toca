"""Análisis longitudinal transparente de los conteos RA comparables."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
LONG_PATH = ROOT / "data/processed/ra_2011_2025_long.parquet"
SIGNALS_PATH = ROOT / "data/processed/senales_ra_2011_2025.parquet"
ADVERSE = {
    "proporcion_repitentes": ("repitentes", "matricula_grados_comparables"),
    "proporcion_sobreedad": ("sobreedad", "matricula_grados_comparables"),
    "proporcion_salidos_sin_pase": ("salidos_sin_pase", "matricula_inicial"),
}


def department_counts(long: pd.DataFrame) -> pd.DataFrame:
    identified = long.loc[long["departamento_id"].notna()].copy()
    keys = ["anio", "provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "variable"]
    grouped = identified.groupby(keys, observed=True)["valor"].sum(min_count=1).reset_index()
    return grouped.pivot(index=keys[:-1], columns="variable", values="valor").reset_index()


def build_indicators(long: pd.DataFrame) -> pd.DataFrame:
    result = department_counts(long)
    for name, (numerator, denominator) in ADVERSE.items():
        result[name] = result[numerator].div(result[denominator].where(result[denominator].gt(0)))
    return result


def _spearman_year(group: pd.DataFrame, metric: str) -> float:
    observed = group[["anio", metric]].dropna()
    return observed["anio"].corr(observed[metric], method="spearman") if len(observed) >= 3 else np.nan


def classify_series(indicators: pd.DataFrame) -> pd.DataFrame:
    """Clasifica cada señal adversa con reglas simples, sin combinarlas en score."""
    rows = []
    for metric in ADVERSE:
        annual_q = indicators.groupby("anio")[metric].quantile([0.25, 0.75]).unstack()
        for identity, group in indicators.groupby(["provincia_nombre", "departamento_id", "departamento_nombre"]):
            observed = group[["anio", metric]].dropna().sort_values("anio")
            n = len(observed)
            classification = "Datos insuficientes"
            rho = _spearman_year(group, metric)
            delta = np.nan
            high_share = low_share = np.nan
            if n:
                values = observed[metric]
                years = observed["anio"]
                high_share = np.mean([value >= annual_q.loc[year, 0.75] for year, value in zip(years, values)])
                low_share = np.mean([value <= annual_q.loc[year, 0.25] for year, value in zip(years, values)])
            if n >= 10:
                first = observed.head(3)[metric].median()
                last = observed.tail(3)[metric].median()
                delta = last - first
                prior = observed.iloc[:-1][metric]
                recent = observed.iloc[-1][metric]
                iqr = prior.quantile(.75) - prior.quantile(.25)
                median_step = observed[metric].diff().abs().median()
                if len(prior) >= 8 and iqr > 0 and abs(recent - prior.median()) > 2.5 * iqr:
                    classification = "Anomalía reciente"
                elif median_step > .02:
                    classification = "Volátil"
                elif rho <= -.70 and delta <= -.02:
                    classification = "Mejora sostenida"
                elif rho >= .70 and delta >= .02:
                    classification = "Deterioro sostenido"
                elif high_share >= .70:
                    classification = "Persistente alto"
                elif low_share >= .70:
                    classification = "Persistente bajo"
                else:
                    classification = "Datos insuficientes"
            rows.append({
                "provincia_nombre": identity[0], "departamento_id": identity[1],
                "departamento_nombre": identity[2], "indicador": metric,
                "clasificacion": classification, "n_anios": n,
                "rho_spearman": rho, "cambio_mediana_ultimos_vs_primeros": delta,
                "proporcion_anios_cuartil_alto": high_share,
                "proporcion_anios_cuartil_bajo": low_share,
            })
    return pd.DataFrame(rows)


def write_signals(path: Path = SIGNALS_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    long = pd.read_parquet(LONG_PATH)
    indicators = build_indicators(long)
    signals = classify_series(indicators)
    path.parent.mkdir(parents=True, exist_ok=True)
    signals.to_parquet(path, index=False)
    return indicators, signals


if __name__ == "__main__":
    indicators, signals = write_signals()
    print(f"Panel: {len(indicators):,} filas; señales: {len(signals):,}")
    print(signals["clasificacion"].value_counts().to_string())
