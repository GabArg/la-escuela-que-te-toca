# Metodología de perfiles educativos territoriales

## Propósito y grano

El perfil integra dimensiones separadas para las 529 unidades territoriales de GeoRef. GeoRef es siempre el universo izquierdo: un territorio permanece aunque no tenga observación educativa. El resultado no contiene score, ranking ordinal ni imputaciones.

## Fuentes, años y dimensiones

- Territorio, población y oferta: GeoRef, Censo 2022 y Padrón Oficial 2022.
- Acceso/asistencia: asistencia censal 2022; el cociente matrícula/población 2022 se mantiene secundario y no se denomina tasa de escolarización.
- Trayectoria: RA 2025 y clasificaciones históricas auditadas de RA 2011–2025.
- Contexto: Censo 2022 (internet, computadora, agua, cloaca y rancho/casilla).
- Aprendizaje: Aprender Secundaria 2024, separado por Lengua y Matemática.

Todos los joins usan `departamento_id`, grano uno-a-uno. No se reabre ni renormaliza ninguna fuente raw.

## Oferta: CUE frente a CUE-anexo

`localizaciones_total_2022` cuenta CUE-anexo y es el indicador principal de despliegue espacial. Los conteos primaria y secundaria disponibles en el output auditado corresponden a establecimientos CUE con al menos una localización que declara el nivel; por eso se nombran `establecimientos_cue_*`. No se fabrican localizaciones por nivel. Se derivan localizaciones totales por 1.000 habitantes de 4–17 y por 100 km²; no miden vacantes, distancia ni accesibilidad efectiva.

## Trayectoria histórica

Se reutilizan sin alterar las clasificaciones existentes: Persistente alto/bajo, Mejora sostenida, Deterioro sostenido, Volátil, Anomalía reciente y Datos insuficientes. Se incorporan valor 2025, mediana histórica y clasificación por indicador. No se crea una nueva etiqueta integrada.

El parquet histórico tiene grano `territorio × indicador`; no conserva sector ni ámbito. Las 95 clasificaciones `Persistente alto` documentadas históricamente son el total entre indicadores: 39 corresponden a repitencia, 56 a salidos sin pase y ninguna a sobreedad. Por eso `bandera_sobreedad_persistente_alta` evalúa 506 territorios y activa cero. No hubo pérdida en el pivot ni en el merge: la bandera es específica de sobreedad y no representa el total de persistencias adversas.

## Aprendizaje

Las cuatro categorías oficiales se incluyen únicamente si la distribución del área está completa. `satisfactorio_o_avanzado` es la suma transparente de dos categorías oficiales; permanece nulo ante cobertura parcial. Censal describe el diseño, no participación completa. Lengua tiene 480 territorios completos y Matemática 145.

## Comparaciones

Para siete indicadores seleccionados se calcula mediana provincial, diferencia y cuartil provincial solo si hay al menos cuatro observaciones en la provincia. La referencia nacional informa exclusivamente encima/igual/debajo de la mediana territorial. No se genera posición ordinal ni percentil.

## Banderas y señales prioritarias

Las reglas están en `reglas_banderas_perfiles.csv`. Los cuantiles se calculan entre territorios observados. Si falta el insumo, la bandera queda nula. La tabla interpretativa elige hasta tres señales mediante un orden fijo: calidad, cobertura Aprender, deterioro, persistencia, asistencia, oferta y vivienda. El orden organiza revisión; no suma puntos ni mide gravedad.

`bandera_dato_aprender_parcial` significa que al menos un área publicada tiene estado `parcial`; no significa cualquier perfil Aprender incompleto. En este corte: Lengua completa 480, Lengua parcial 19, Matemática completa 145, Matemática parcial 354 y Aprender totalmente ausente 30. Los 354 activados son 335 con Lengua completa/Matemática parcial y 19 con ambas áreas parciales. La ausencia total deja la bandera nula.

Cada señal priorizada conserva el valor o categoría fuente y, cuando corresponde, el umbral aplicado. Los desempates no dependen de magnitudes: cada regla tiene un orden único y fijo. La confianza es Alta para hechos de cobertura y Media para banderas sustantivas relativas o históricas.

## Completitud documental

Se cuentan siete dimensiones no territoriales disponibles. 0–2 es Cobertura baja, 3–5 Cobertura media y 6–7 Alta cobertura. Esta categoría mide disponibilidad documental, no calidad educativa.

## Limitaciones

Los años no coinciden; las unidades de residencia, escuela y publicación difieren; los cuantiles son relativos a esta cobertura; faltan localizaciones por nivel y accesibilidad; Matemática tiene cobertura limitada. Ausencia no equivale a cero. Ninguna asociación o bandera demuestra causalidad ni prescribe una política.
