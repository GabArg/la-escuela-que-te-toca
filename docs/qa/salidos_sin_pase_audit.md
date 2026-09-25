# Auditoría de salidos sin pase: Ramón Lista–Quebrachos

Fecha de ejecución: 2026-09-24. Script reproducible: `python scripts/audit_salidos_sin_pase.py`.

## Conclusión del Gate 2

**A. Definición exacta.** La documentación oficial define como salidos sin pase a estudiantes que dejaron de asistir al establecimiento durante el ciclo lectivo y fueron dados de baja de sus registros sin haber solicitado pase a otra escuela. El diccionario usado por el proyecto identifica `ssp_1`…`ssp_12`, `ssp_1314` y `ssp_20` como salidos sin pase por año/categoría.

**B. Qué significa.** El indicador del proyecto es un cociente descriptivo: conteo publicado de salidos sin pase dividido por la matrícula inicial publicada en las mismas categorías, sumado primero entre las celdas sector–ámbito del territorio.

**C. Qué no significa.** No identifica trayectorias individuales fuera del establecimiento, no comprueba que la persona haya quedado fuera del sistema educativo, no distingue una reinscripción posterior no registrada como pase y no mide por sí solo abandono o deserción escolar.

> Salidos sin pase no equivale automáticamente a abandono escolar.

**D. Período correcto.** La base se publica como Relevamiento Anual 2025, pero el bloque de trayectoria releva el ciclo lectivo anterior: **ciclo lectivo 2024**. La metodología oficial del RA distingue datos del ciclo actual a la fecha de corte de la trayectoria del ciclo anterior; el Anuario 2022 confirma el criterio al describir como ciclo 2021 los salidos informados en RA 2022.

**E. Denominador.** Matrícula inicial de Educación Común en las categorías 1–12, 13/14 y organización no graduada (`20`) que estén publicadas para las celdas sector–ámbito del territorio. Los componentes completamente ausentes en numerador y denominador se preservan como faltantes y no se convierten en cero.

**F. ¿Es correcta la diferencia de 9,15 pp?** Sí. La diferencia absoluta calculada con precisión completa es 9,15044798 puntos porcentuales; el formato narrativo correcto es **9,15 pp**.

## Reproducción

| Territorio | Provincia | Numerador | Denominador | Cociente exacto | Presentación |
|---|---|---:|---:|---:|---:|
| Ramón Lista | Formosa | 557 | 5.473 | 10,17723369% | 10,18% |
| Quebrachos | Santiago del Estero | 23 | 2.240 | 1,02678571% | 1,03% |

`abs(557 / 5.473 − 23 / 2.240) × 100 = 9,15044798 pp`.

## Universo y cobertura

- Base: Trayectoria, Educación Común, RA 2025.
- Movimiento: ciclo lectivo 2024.
- Categorías: años/categorías 1–12, 13/14 y organización no graduada 20.
- Ramón Lista: una celda publicada e identificada, sector Estatal, ámbito Rural.
- Quebrachos: dos celdas publicadas e identificadas, sector Estatal, ámbitos Rural y Urbano.
- Las filas de ambos territorios se vinculan por nombre normalizado, no mediante imputación ni matching difuso.
- En ambos territorios la categoría 20 está ausente de forma pareada en matrícula inicial y salidos sin pase. Quebrachos Rural también tiene 13/14 ausente de forma pareada, pero la categoría está publicada en su celda Urbana. Las sumas usan los componentes observados y preservan los faltantes.
- No hay filas `Enmascarado` ni `Sin datos` atribuidas a Ramón Lista o Quebrachos. Las filas provinciales enmascaradas corresponden a unidades no identificables y no pueden asignarse a estos casos.

## Fuentes verificadas

- [Relevamiento Anual — descripción oficial](https://www.argentina.gob.ar/node/246606): operativo censal con corte anual al 30 de abril y criterios metodológicos comunes.
- [Diccionario oficial de bases usuarias RA](https://www.argentina.gob.ar/sites/default/files/201608.-bases-usuarias_diccionario-datos.pdf): universo de la base Trayectoria y campos de salidos con/sin pase.
- [Anuario Estadístico Educativo 2022](https://www.argentina.gob.ar/sites/default/files/2018/04/anuario_estadistico_educativo_2022.pdf): definición operacional de salidos sin pase y ejemplo explícito de que RA 2022 registra movimientos del ciclo 2021.
- [Cuadernillos de Relevamiento Anual](https://www.argentina.gob.ar/node/83809): los instructivos distinguen datos del ciclo actual de trayectoria del ciclo lectivo anterior.
- Archivo utilizado: `data/raw/educacion_departamental/2025_trayectoria_agregada.csv`, descargado el 2026-09-04 según el inventario del proyecto.

## Decisión

Gate 2 aprobado. Se mantiene 9,15 pp y deben corregirse los rótulos para indicar “ciclo lectivo 2024 · informado en RA 2025”, el denominador usado y la advertencia de interpretación. Deben evitarse “abandono”, “deserción” y “quedaron fuera del sistema” como equivalencias del indicador.
