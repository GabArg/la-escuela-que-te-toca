import pandas as pd
import pytest

from app.components.perfil import format_value
from app.components.ui import readable_evidence
from scripts.audit_national_overage import audit_overage_year
from scripts.audit_salidos_sin_pase import audit_territory
from src.analysis.ra_historico import ADVERSE, classify_series


def test_national_overage_audit_reproduces_old_and_corrected_aggregates():
    audit_2011 = audit_overage_year(2011)
    audit_2025 = audit_overage_year(2025)
    assert audit_2011.ratio_identificado * 100 == pytest.approx(27.9726456585)
    assert audit_2025.ratio_identificado * 100 == pytest.approx(11.8807598612)
    assert audit_2011.ratio_publicado * 100 == pytest.approx(27.4368336089)
    assert audit_2025.ratio_publicado * 100 == pytest.approx(11.8313277519)
    assert audit_2011.filas_excluidas == 132
    assert audit_2025.filas_excluidas == 84
    assert audit_2011.ratio_publicado > audit_2025.ratio_publicado


def test_salidos_sin_pase_case_is_reproducible_from_counts():
    ramon = audit_territory("34063")
    quebrachos = audit_territory("86140")
    assert (ramon.numerador, ramon.denominador) == (557, 5473)
    assert (quebrachos.numerador, quebrachos.denominador) == (23, 2240)
    assert ramon.ratio * 100 == pytest.approx(10.1772336927)
    assert quebrachos.ratio * 100 == pytest.approx(1.0267857143)
    assert abs(ramon.ratio - quebrachos.ratio) * 100 == pytest.approx(9.1504479784)
    assert ramon.periodo_movimiento.startswith("ciclo lectivo 2024")


def _classification_panel(years: list[int]) -> pd.DataFrame:
    rows = []
    for name, territory_id, values in (
        ("Bajo", "1", [0.1] * len(years)),
        ("Medio", "2", [0.3, 0.7] * (len(years) // 2)),
        ("Alto", "3", [0.9] * len(years)),
    ):
        for year, value in zip(years, values):
            row = {
                "anio": year,
                "provincia_nombre": "Prueba",
                "departamento_id": territory_id,
                "departamento_nombre": name,
            }
            row.update({metric: value for metric in ADVERSE})
            rows.append(row)
    return pd.DataFrame(rows)


def test_historical_residual_is_not_labeled_insufficient():
    panel = _classification_panel(list(range(2000, 2010)))
    middle = panel.departamento_id.eq("2")
    for metric in ADVERSE:
        panel.loc[middle, metric] = [0.495, 0.505] * 5
    signals = classify_series(panel)
    middle = signals.loc[signals.departamento_id.eq("2")]
    assert middle.clasificacion.eq("Sin patrón definido por estas reglas").all()
    assert middle.n_cambios_anuales_consecutivos.eq(9).all()


def test_nonconsecutive_observations_are_not_called_annual_volatility():
    signals = classify_series(_classification_panel(list(range(2000, 2020, 2))))
    middle = signals.loc[signals.departamento_id.eq("2")]
    assert middle.clasificacion.eq("Sin patrón definido por estas reglas").all()
    assert middle.n_cambios_anuales_consecutivos.eq(0).all()


def test_public_numeric_format_policy():
    assert format_value(76.7802, "percent") == "76,8%"
    assert format_value(83.3540, "percent") == "83,4%"
    assert format_value(15, "integer") == "15"
    assert readable_evidence(
        "valor=76.7802; umbral_P25=83.3540",
        "Asistencia 15–17 relativamente baja",
    ) == (
        "Asistencia 15–17: 76,8%\n"
        "Referencia: el umbral del 25% de territorios con valores más bajos es 83,4%"
    )
