# Cobertura territorial de las bases RA 2025

Auditoría metodológica de la correspondencia entre las bases abiertas agregadas del Relevamiento Anual (RA) 2025 y las 529 unidades publicadas por GeoRef Argentina. Fecha de consulta: **2026-09-12**.

## Fuentes oficiales revisadas

- [Datos abiertos de la Subsecretaría de Información y Evaluación Educativa](https://www.argentina.gob.ar/capital-humano/educacion/informacion-y-evaluacion-educativa/datos-abiertos-de-la-subsecretaria-de).
- [Datos abiertos](https://www.argentina.gob.ar/capital-humano/educacion/informacion-y-evaluacion-educativa/datos-abiertos).
- `Diccionario de bases RA anonimizadas.xlsx`, enlazado como documentación técnica en el buscador oficial.
- `Notas metodológicas acerca del proceso de anonimización.pdf`, enlazado en el mismo buscador.
- Bases RA 2025 de Matrícula, Trayectoria y Características.
- GeoRef Argentina: `territorios_argentina.parquet`, construido por el pipeline territorial del proyecto.

## Significado oficial de `Enmascarado`

La nota metodológica oficial explica que la publicación es una medida de anonimización para evitar la identificación de establecimientos y de departamentos con pocas localizaciones dentro de una combinación. El umbral principal es de **tres o menos localizaciones** para una combinación sector–ámbito en Características, o sector–ámbito–nivel en otras bases como Matrícula. Cuando ocultar un único departamento permitiría deducirlo, el procedimiento extiende el enmascaramiento a otro u otros departamentos.

Los departamentos alcanzados se **fusionan en una sola fila por provincia y combinación**, y las restantes variables se resumen mediante agregación. La documentación también indica que se consolidó un único listado de departamentos a enmascarar a partir de las bases de Características y Trayectoria, que luego se aplicó a las demás bases.

Consecuencias para este proyecto:

- `Enmascarado` no identifica un departamento concreto y nunca recibe `departamento_id`.
- Una fila puede reunir más de un departamento; no debe repartirse ni imputarse entre territorios.
- Sus métricas contienen agregados publicados y no son equivalentes a valores faltantes.
- Para sumas provinciales de variables aditivas, excluir estas filas omitiría los valores agregados que contienen. Cualquier agregación debe respetar primero la definición oficial de cada variable.
- No pueden utilizarse para análisis o mapas departamentales porque se desconoce qué parte corresponde a cada unidad.

## Registros especiales observados

La expresión “23 registros provincia–Enmascarado” se refiere a **23 pares únicos de provincia y etiqueta**, uno por cada jurisdicción donde aparece. Debido a las combinaciones de sector y ámbito, esos pares producen varias filas.

| Dataset | Filas `Enmascarado` | Provincias | Celdas métricas presentes | Celdas métricas nulas | Filas sin ninguna métrica | Pares `Sin datos` |
|---|---:|---:|---:|---:|---:|---:|
| Matrícula | 68 | 23 | 5.181 | 1.551 | 0 | 0 |
| Características | 68 | 23 | 3.122 | 1.162 | 0 | 0 |
| Trayectoria | 67 | 23 | 16.236 | 4.668 | 0 | 2 |

`Enmascarado` aparece en todas las provincias excepto Ciudad de Buenos Aires. Las combinaciones observadas son Estatal–Rural, Estatal–Urbano, Privado–Rural y Privado–Urbano, aunque no todas aparecen en cada provincia o dataset. Todas las filas enmascaradas contienen al menos una métrica numérica.

### `Sin datos`

La documentación oficial revisada no define la etiqueta `Sin datos`. En Trayectoria 2025 se observan dos filas:

| Provincia | Sector | Ámbito | Métricas numéricas presentes | Valores no nulos observados |
|---|---|---|---:|---|
| Formosa | Estatal | Rural | 81 de 312 | Todos son cero |
| Tucumán | Estatal | Rural | 81 de 312 | Todos son cero |

No aparece `Sin datos` en Matrícula ni Características 2025. La presencia de ceros no permite concluir que el fenómeno educativo sea cero ni identificar un departamento. Hasta contar con una definición oficial, estas filas:

- no reciben identificadores territoriales;
- no se imputan ni se redistribuyen;
- no se interpretan como ausencia real del fenómeno;
- quedan fuera de cruces departamentales;
- se conservan para trazabilidad, con estado no identificable.

No se pudo confirmar si deben participar en totales. Esa decisión queda pendiente de documentación oficial específica.

## Correspondencia con las 529 unidades GeoRef

| Categoría por dataset | Cantidad | Significado |
|---|---:|---|
| `directo` | 503 | Coincidencia por provincia y departamento después de normalizar mayúsculas, acentos, espacios y puntuación. |
| `puente` | 3 | Abreviatura inequívoca registrada y confirmada en la tabla puente. |
| `por_verificar` | 8 | Variante nominal plausible, pero sin equivalencia oficial explícita suficiente; no recibe ID. |
| `no_representado` | 15 | Unidad GeoRef sin fila identificable por su nombre en RA 2025. |
| **Total GeoRef** | **529** | Departamentos o unidades territoriales equivalentes según GeoRef. |

La matriz completa está en `data/dictionaries/cobertura_territorial_ra_2025.csv`.

**Sin registro no equivale a valor cero.** `no_representado` solo describe la ausencia de una fila identificable en la publicación. Tampoco demuestra que la unidad carezca de establecimientos, matrícula o trayectorias.

## Revisión de la tabla puente

No se utilizó similitud difusa. Se compararon los nombres publicados por RA con los nombres e IDs oficiales conservados desde GeoRef, siempre dentro de la misma provincia.

| Provincia | Nombre RA | Nombre GeoRef | Tipo | Estado | Fundamento |
|---|---|---|---|---|---|
| Buenos Aires | CORONEL DE MARINA L ROSALES | Coronel de Marina Leonardo Rosales | Abreviatura | Pendiente | No se halló fuente oficial explícita para expandir `L`. |
| Jujuy | DOCTOR MANUEL BELGRANO | Dr. Manuel Belgrano | Abreviatura | Confirmado | Única diferencia: tratamiento `Doctor`/`Dr.`; provincia y resto del nombre coinciden. |
| La Rioja | CORONEL FELIPE VARELA | General Felipe Varela | Denominación administrativa | Pendiente | `Coronel` y `General` no son equivalentes por mera normalización. |
| La Rioja | GENERAL ANGEL V PEÑALOZA | Ángel Vicente Peñaloza | Denominación administrativa | Pendiente | Falta equivalencia oficial explícita para la variante completa. |
| La Rioja | GENERAL JUAN F QUIROGA | General Juan Facundo Quiroga | Abreviatura | Pendiente | No se halló fuente oficial explícita para expandir `F`. |
| La Rioja | GENERAL OCAMPO | General Ortiz de Ocampo | Denominación administrativa | Pendiente | Falta evidencia oficial para la omisión `Ortiz de`. |
| Misiones | LIBERTADOR GRL SAN MARTIN | Libertador General San Martín | Abreviatura | Confirmado | `GRL` abrevia `General`; los demás términos y la provincia coinciden. |
| San Luis | GENERAL JUAN MARTIN DE PUEYRREDON | Juan Martín de Pueyrredón | Denominación administrativa | Pendiente | Falta equivalencia oficial explícita para la variante completa. |
| San Luis | LIBERTADOR GRL SAN MARTIN | Libertador General San Martín | Abreviatura | Confirmado | `GRL` abrevia `General`; los demás términos y la provincia coinciden. |
| Santiago del Estero | JUAN F IBARRA | Juan Felipe Ibarra | Abreviatura | Pendiente | No se halló fuente oficial explícita para expandir `F`. |
| Tucumán | JUAN B ALBERDI | Juan Bautista Alberdi | Abreviatura | Pendiente | No se halló fuente oficial explícita para expandir `B`. |

Solo los tres registros `confirmado` se aplican automáticamente. Los ocho `pendiente` permanecen sin `departamento_id` hasta obtener evidencia oficial adicional.

## Los 15 territorios sin representación identificable en 2025

Los 15 están ausentes como nombre identificable en Matrícula, Trayectoria y Características 2025. La metodología de anonimización hace posible que una unidad no identificada forme parte de alguna fila agregada `Enmascarado`, pero la publicación **no permite determinar cuál**. Por lo tanto, no se vincula ningún territorio con esos agregados.

La revisión de las bases oficiales de Matrícula 2011–2025 encontró:

| Provincia | Unidad GeoRef | Aparición identificable en Matrícula de años anteriores |
|---|---|---|
| Córdoba | Sobremonte | Ninguna entre 2011 y 2024. |
| Corrientes | Berón de Astrada | 2012–2022 y 2024; no aparece identificable en 2011, 2023 ni 2025. |
| Chubut | Florentino Ameghino | Ninguna entre 2011 y 2024. |
| Chubut | Mártires | 2014 solamente. |
| La Pampa | Caleu Caleu | 2011–2023; no aparece identificable en 2024 ni 2025. |
| La Pampa | Chalileo | Ninguna entre 2011 y 2024. |
| La Pampa | Lihuel Calel | Ninguna entre 2011 y 2024. |
| La Pampa | Limay Mahuida | Ninguna entre 2011 y 2024. |
| La Rioja | General Lamadrid | Ninguna entre 2011 y 2024. |
| La Rioja | Sanagasta | Ninguna entre 2011 y 2024. |
| San Juan | Ullum | Ninguna entre 2011 y 2024. |
| San Juan | Zonda | Ninguna entre 2011 y 2024. |
| Santiago del Estero | Belgrano | 2011–2013, 2015, 2020 y 2023. |
| Tierra del Fuego | Islas del Atlántico Sur | Ninguna entre 2011 y 2024. |
| Tierra del Fuego | Antártida Argentina | Ninguna entre 2011 y 2024. |

Esta revisión comprueba presencia nominal, no continuidad estadística. No se encontró una explicación oficial individual para la ausencia 2025 de ninguno de los 15 territorios. No debe concluirse que una ausencia histórica refleje valor cero, inexistencia de oferta educativa o pertenencia cierta a `Enmascarado`.

## Reglas metodológicas operativas

- Nunca transformar ausencia territorial en cero.
- Nunca asignar `Enmascarado` o `Sin datos` a un departamento específico.
- Nunca redistribuir métricas enmascaradas sin fundamento metodológico oficial.
- Mantener separados `directo`, `puente`, `por_verificar` y `no_representado`.
- Preservar nombres originales además de nombres e IDs GeoRef.
- No inferir causalidad a partir de agregados territoriales.
- Revisar comparabilidad y anonimización para cada año antes de construir una serie temporal.
