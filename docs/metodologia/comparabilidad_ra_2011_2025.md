# Comparabilidad RA 2011–2025

## Criterio de decisión

Una variable se clasifica como comparable solo cuando coinciden en todos los años: nombre y componentes publicados, definición en el diccionario oficial, unidad de conteo, grano provincia–departamento–sector–ámbito y universo educativo representado. Compartir nombre no alcanza.

- **Alta:** mismos componentes, unidad, definición y grano en 2011–2025.
- **Media:** definición estable pero existe una discontinuidad contextual o de publicación que obliga a separar interpretaciones.
- **Baja:** equivalencia parcial o documentación insuficiente.
- **No comparable:** cambia el universo, aparece solo en una parte del período, tiene unidad ambigua o no hay evidencia suficiente.

El parquet largo incluye únicamente conteos de comparabilidad Alta. Los cocientes analíticos se recalculan después de sumar numeradores y denominadores; nunca se suman ni promedian tasas.

## Fuentes y trazabilidad

El catálogo es la planilla pública embebida en la página oficial de Datos abiertos de la Secretaría de Educación. Se descargaron 45 archivos: Matrícula, Trayectoria y Características para cada año 2011–2025. `fuentes_ra_historico.csv` conserva URL, nombre original, fecha, ruta y SHA-256. Los archivos raw no se modifican ni sobrescriben.

## Cambios de esquema detectados

- Matrícula mantiene 99 columnas entre 2011–2022, pasa a 103 en 2023 y 2025, y tiene 104 en 2024 porque incluye además `Localizacion`.
- La categoría `_20` y sus variantes aparecen desde 2023. Se excluye de las series completas.
- Trayectoria mantiene 268 columnas en 2011–2022, 288 en 2023–2024 y 316 en 2025.
- `promovidos_mas_2mat_*` aparece solo en 2025 y se excluye.
- Características pasa de 65 columnas (2011–2022) a 66 (2023–2024) y 67 (2025). Cambian categorías de servicio gratuito de internet, reproductores y teléfonos inteligentes.
- `Departamento`/`departamento` y `Localizacion`/`localizacion` son diferencias de encabezado normalizadas, no cambios sustantivos.
- En 2021 existe una discontinuidad empírica muy grande en repitencia y salidos sin pase. No se atribuye a una causa ni se declara cambio metodológico sin documentación oficial adicional; los análisis que atraviesan 2020–2022 deben considerarse de comparabilidad interpretativa Media.

## Variables incluidas

Se conservaron categorías presentes durante los 15 años:

- matrícula total en componentes comunes;
- matrícula de años de estudio comparables;
- repitentes y sobreedad de esos años;
- matrícula inicial y al último día;
- salidos con y sin pase;
- promovidos y no promovidos;
- egresados de primaria y secundaria;
- localizaciones;
- sector y ámbito como dimensiones del grano.

No se incorporan porcentajes publicados. Sobreedad de categorías iniciales queda excluida por ambigüedades del diccionario.

## Territorio

El matching usa nombres normalizados exactos contra GeoRef y puentes explícitos. No se usa similitud difusa. Los tres puentes confirmados en la auditoría 2025 se heredan únicamente cuando aparece exactamente la misma denominación. Las restantes diferencias quedan pendientes y sin ID.

En 2011–2012, CABA se publica mediante distritos escolares romanos I–XXI, que no se consideran equivalentes automáticos de las comunas GeoRef actuales. También queda pendiente `1º DE MAYO` de Chaco y las ocho variantes nominales ya auditadas en 2025.

`Enmascarado` y `Sin datos` conservan valor agregado y estado, pero nunca reciben `departamento_id`. No se redistribuyen, imputan ni transforman en cero. La falta de una fila territorial tampoco equivale a cero.

## Reglas de señales temporales

Las reglas se aplican por indicador adverso —repitentes/matrícula comparable, sobreedad/matrícula comparable y salidos sin pase/matrícula inicial—, nunca se combinan en un score:

- **Datos insuficientes:** menos de 10 años válidos.
- **Sin patrón definido por estas reglas:** al menos 10 años válidos, pero ninguna regla posterior se activa.
- **Anomalía reciente:** último valor a más de 2,5 rangos intercuartílicos de la mediana previa, con al menos 8 observaciones previas.
- **Volátil:** mediana del cambio anual absoluto superior a 2 puntos porcentuales, calculada solo entre observaciones de años consecutivos. Los saltos entre observaciones separadas por más de un año no se tratan como interanuales.
- **Mejora sostenida:** Spearman año–indicador <= −0,70 y descenso de al menos 2 puntos entre la mediana de los primeros y últimos tres años.
- **Deterioro sostenido:** Spearman >= 0,70 y aumento de al menos 2 puntos.
- **Persistente alto/bajo:** al menos 70% de los años en el cuartil superior/inferior de la distribución anual.

El orden anterior resuelve superposiciones. Las etiquetas describen el patrón matemático, no su causa, calidad ni valor normativo.

## Exclusiones

Se excluyen variables de Características distintas de localizaciones por unidad agregada ambigua y cambios de categorías; campos exclusivos de 2023–2025; el bloque exclusivo de Trayectoria 2025; y toda equivalencia territorial dudosa. La decisión favorece continuidad defendible sobre cantidad de indicadores.
