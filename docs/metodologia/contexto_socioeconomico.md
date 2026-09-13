# Contexto socioeconómico y condiciones del hogar

## Alcance

La capa describe condiciones estructurales observadas por el Censo 2022. No demuestra causas de repetición, sobreedad, salidas sin pase o asistencia. El dataset usa como universo territorial las 529 unidades de GeoRef y preserva toda ausencia como nula.

## Extracción reproducible

Se descargaron 120 cuadros XLSX oficiales de INDEC: cinco familias para cada una de las 24 jurisdicciones. Son archivos estáticos de asistencia escolar, tecnologías del hogar, agua, saneamiento y tipo de vivienda. Los originales se conservan sin modificar en `data/raw/contexto_socioeconomico/`; el inventario registra URL exacta y SHA-256 por archivo.

Se prefirieron estos cuadros a automatizar REDATAM. REDATAM permite consultas hasta radio censal, pero su interfaz interactiva no ofrece en este flujo un artefacto estático departamental estable. NBI y hacinamiento crítico tienen definición alta, pero se excluyeron del parquet hasta disponer de una descarga oficial reproducible con universo y denominador comprobables.

## Definiciones y universos

**NBI:** hogar que presenta al menos una privación: vivienda inconveniente; ausencia de baño o letrina; más de tres personas por cuarto; al menos un niño de 6–12 años que no asiste; o cuatro o más personas por miembro ocupado y jefatura que no completó tercer grado primario. Universo: hogares. No fue incorporada.

**Hacinamiento crítico:** más de tres personas por cuarto de uso exclusivo del hogar. Universo: hogares. No fue incorporado.

**Internet:** hogar con internet fijo/alámbrico o mediante punto inalámbrico; no incluye abonos de uso exclusivo del teléfono móvil. Denominador: total de hogares del cuadro.

**Computadora:** hogar con al menos una computadora, tablet u otro equipo de almacenamiento y procesamiento. Se suman las celdas con computadora de ambos estratos de internet; denominador: total de hogares.

**Agua y cloaca:** hogares con procedencia de agua de red pública y hogares con inodoro que desagua a red pública, respectivamente. No miden continuidad, calidad ni disponibilidad diaria.

**Rancho o casilla:** viviendas particulares ocupadas de esos dos tipos sobre total de viviendas particulares ocupadas. No es NBI vivienda y no debe mezclarse con porcentajes de hogares.

**Asistencia censal:** población residente en viviendas particulares que al momento del Censo declaró asistir a un establecimiento educativo. Cada grupo se construye sumando edades simples; el denominador incluye quienes asisten, quienes no asisten pero asistieron y quienes nunca asistieron. No asistir no equivale por sí solo a abandono ni a estar permanentemente fuera del sistema.

## Territorio

Los cuadros se vinculan por nombres normalizados y puentes explícitos. Se confirmaron `Nueve de Julio`/`9 de Julio` y la variante del símbolo ordinal en `1º de Mayo`/`1° de Mayo`, con IDs verificados contra GeoRef. `Coronel de Marina L. Rosales` y `Lezana` permanecen pendientes y no reciben ID. No se usa similitud difusa.

## Censo frente a RA

El Censo territorializa personas por residencia habitual y pregunta asistencia. RA territorializa matrícula por el establecimiento. La asistencia censal es conceptualmente más apropiada para describir escolarización de residentes; RA es más apropiado para dimensionar demanda atendida por la oferta localizada. Ninguna debe sustituir silenciosamente a la otra: movilidad entre departamentos, fechas de referencia y universos producen diferencias legítimas.

## Asociaciones y composición

Las correlaciones simples son Spearman. Como sensibilidad se residualizaron rangos respecto de densidad, población 4–17, proporción de establecimientos rurales y secundarias por 1.000 adolescentes. Estas correlaciones parciales siguen siendo exploratorias: controlar cuatro variables no elimina selección, medición imperfecta, desfase 2022–2025 ni confusión no observada.

No se suman ni promedian porcentajes territoriales. Para agregaciones futuras deben sumarse numeradores y denominadores originales.
