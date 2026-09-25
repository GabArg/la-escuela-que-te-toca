# Auditoría del agregado nacional de sobreedad

Fecha de ejecución: 2026-09-24. Script reproducible: `python scripts/audit_national_overage.py`.

## Conclusión del Gate 1

**A. ¿El 28,0% → 11,9% representa un total nacional?**

No. Los valores exactos 27,97264566% y 11,88075986% son el cociente entre conteos de sobreedad y matrícula comparable **solo de las filas con `departamento_id` identificado**. En 2011 la selección cubre 485 departamentos/unidades equivalentes y 23 de 24 jurisdicciones; en 2025 cubre 506 y las 24 jurisdicciones. La composición territorial no es la misma y se excluyen conteos publicados.

**B. ¿Qué representa exactamente?**

Un agregado ponderado de Educación Común, sectores Estatal y Privado, ámbitos Urbano y Rural, para años/categorías 1–12 y 13/14, restringido a las unidades que pudieron vincularse con GeoRef. No es un promedio simple de departamentos ni una tasa oficial publicada.

**C. ¿Existe un cálculo alternativo defendible como nacional?**

Sí. Para este universo comparable puede sumarse el numerador y el denominador de **todas las filas publicadas** en Matrícula RA, incluidas las filas `Enmascarado` y los nombres territoriales que no recibieron ID. Esas filas son parte del grano publicado provincia–departamento/agrupación–sector–ámbito y sus conteos son aditivos. Se suman al total nacional sin redistribuirlos ni atribuirlos a un departamento.

El resultado es:

| Año | Numerador publicado | Denominador publicado | Proporción |
|---:|---:|---:|---:|
| 2011 | 2.291.391 | 8.351.514 | 27,43683361% |
| 2025 | 1.026.048 | 8.672.298 | 11,83132775% |

El rótulo preciso es “agregado nacional del universo comparable publicado”. No equivale a toda la matrícula del sistema educativo: excluye categorías de inicial con definición ambigua, organización no graduada incorporada desde 2023 y modalidades que no pertenecen a la base de Educación Común auditada.

**D. ¿Se mantiene el sentido general de la tendencia?**

Sí. El agregado alternativo cae 15,6055 puntos porcentuales, de 27,44% a 11,83%. La dirección y la magnitud general del descenso se mantienen.

## Reproducción del cálculo vigente

| Año | Numerador con ID | Denominador con ID | Proporción | Filas originales | Filas con ID | Filas excluidas |
|---:|---:|---:|---:|---:|---:|---:|
| 2011 | 2.140.800 | 7.653.191 | 27,97264566% | 1.191 | 1.059 | 132 |
| 2025 | 1.004.758 | 8.457.018 | 11,88075986% | 1.217 | 1.133 | 84 |

Las cifras de portada 28,0% y 11,9% son exactamente el redondeo a un decimal de esas proporciones restringidas.

## Filas publicadas excluidas por el cálculo vigente

| Año | Enmascarado | Sin datos en Matrícula | Nombre por verificar | Numerador excluido | Denominador excluido |
|---:|---:|---:|---:|---:|---:|
| 2011 | 72 | 0 | 60 | 150.591 | 698.323 |
| 2025 | 68 | 0 | 16 | 21.290 | 215.280 |

En 2011, los nombres por verificar incluyen los distritos escolares I–XXI de CABA, que no deben convertirse artificialmente en comunas actuales, y variantes nominales no vinculadas. En 2025 quedan 16 filas con variantes nominales sin ID. La ausencia de ID impide el análisis departamental, pero no impide sumar sus conteos a un agregado nacional.

## Universo y comparabilidad

- Fuente: bases agregadas de Matrícula del Relevamiento Anual 2011 y 2025.
- Organismo: Secretaría de Educación / área nacional de información y evaluación educativa, según el inventario de fuentes del proyecto.
- Modalidad/base: Educación Común.
- Sectores: Estatal y Privado.
- Ámbitos: Urbano y Rural.
- Numerador: suma de `s_1`…`s_12` y `s_1314`, estudiantes publicados con sobreedad en categorías comunes.
- Denominador: suma de `campo_1`…`campo_12` y `campo_1314`, matrícula en las mismas categorías comparables.
- No se usan porcentajes publicados ni promedios de tasas.
- No se incorpora la categoría `_20`, ausente en 2011 y añadida desde 2023.
- No se incorporan categorías de inicial cuya definición disponible es ambigua/inconsistente.

Los componentes, la unidad de conteo, el sector, el ámbito y el grano fuente se mantienen en ambos extremos. La cobertura identificable cambia, pero el agregado de todas las filas publicadas evita que ese cambio altere la composición nacional calculada.

## Limitaciones

- Las filas enmascaradas no permiten análisis departamental ni conocer cuántas unidades subyacentes reúnen; solo permiten recuperar su aporte aditivo al total.
- El cociente es una medida derivada por el proyecto, no una tasa oficial publicada con ese nombre.
- El diccionario disponible describe los campos, pero no autoriza atribuir causas al cambio temporal.
- La serie 2020–2022 conserva la cautela ya documentada; esta auditoría no demuestra continuidad administrativa perfecta para interpretaciones causales.

## Decisión

Gate 1 aprobado. Corresponde reemplazar la lógica de portada y del SVG por el agregado de todas las filas publicadas, actualizar los tests y usar lenguaje que explicite universo, años y fuente. No corresponde mantener 28,0% como “nacional”.
