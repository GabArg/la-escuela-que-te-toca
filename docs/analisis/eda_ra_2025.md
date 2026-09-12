# Análisis exploratorio RA 2025

## Alcance y método

Este EDA usa Matrícula, Trayectoria y Características RA 2025 agregadas por departamento o unidad equivalente, sector y ámbito. La unidad territorial de referencia es GeoRef. Se analizaron solo las 506 unidades con identificación confirmada (503 coincidencias directas y 3 mediante puente). Las 8 denominaciones pendientes, 15 unidades GeoRef no representadas, filas **Enmascarado** y **Sin datos** no se imputan ni se convierten en cero.

Los indicadores denominados `proporcion_*` son cocientes exploratorios recalculados desde conteos, no tasas oficiales. No se suman porcentajes ni se promedian tasas. Para agregaciones se suman numeradores y denominadores por separado. Toda asociación es descriptiva y no implica causalidad.

Cobertura analítica: 1.133 celdas departamento–sector–ámbito; 1.125 tienen las tres fuentes y 8 carecen de conteos de Trayectoria en esa celda. Los 506 departamentos tienen alguna observación en las tres fuentes. En cada base hay 23 combinaciones provincia–Enmascarado; al considerar sector y ámbito representan 68 filas en Matrícula, 68 en Características y 67 en Trayectoria. Trayectoria contiene además 2 filas Sin datos. Estos registros permanecen fuera del análisis departamental.

## A. Hallazgos confirmados por los datos

### 1. Sobreedad y repetición se concentran conjuntamente

- **Descripción:** los cocientes departamentales de estudiantes con sobreedad y repitentes sobre matrícula de años comparables muestran asociación positiva.
- **Evidencia:** correlación de Pearson 0,775; n=506. Medianas departamentales: 11,90% y 3,80%, respectivamente.
- **Territorios:** universo de 506 unidades identificables.
- **Cobertura:** completa a nivel de departamento para los conteos usados.
- **Confianza:** Alta para la asociación descriptiva.
- **Interpretación permitida:** ambas señales tienden a presentarse juntas territorialmente.
- **No interpretar como:** que una cause la otra ni como tasas oficiales de toda la población escolar.
- **Fuente adicional:** series históricas, definiciones por nivel y SInIDE agregado/no nominal.

### 2. Existe una cola territorial marcada de sobreedad

- **Descripción:** la distribución no es simétrica y algunos territorios se separan claramente del centro.
- **Evidencia:** P25=9,04%, mediana=11,90%, P75=15,51%, P90=21,49%. Ramón Lista (Formosa) registra 41,45% sobre 5.342 matrículas comparables; Mburucuyá y Lavalle (Corrientes), 37,12% y 36,44%.
- **Territorios:** 506; ejemplos indicados por su distancia descriptiva, no como ranking de calidad.
- **Cobertura:** conteos observados e identificados.
- **Confianza:** Alta.
- **Interpretación permitida:** son casos para profundizar y verificar por nivel.
- **No interpretar como:** desempeño general del sistema local ni causa atribuible al territorio.
- **Fuente adicional:** composición por nivel/edad, población y contexto socioeconómico.

### 3. La salida sin pase es infrecuente en el agregado, pero presenta casos atípicos

- **Descripción:** el cociente `salidos sin pase / matrícula inicial` tiene mediana baja y cola derecha.
- **Evidencia:** mediana 0,56%, P90=1,92%; Ramón Lista 10,18% (5.473 de matrícula inicial), Pehuenches 7,54% (6.724) y Famatina 7,38% (881).
- **Territorios:** 506.
- **Cobertura:** completa departamental; el tamaño del denominador varía y se informa.
- **Confianza:** Media: el cociente es transparente, pero no debe rotularse abandono sin confirmación adicional.
- **Interpretación permitida:** señal administrativa de permanencia que amerita investigación.
- **No interpretar como:** tasa causal de abandono.
- **Fuente adicional:** diccionario ampliado, registros longitudinales agregados y series previas.

### 4. Los perfiles agregados difieren fuertemente por sector y ámbito

- **Descripción:** los cocientes ponderados difieren entre las cuatro celdas estructurales.
- **Evidencia:** sobreedad/matrícula: estatal rural 15,84%, estatal urbano 14,93%, privado rural 13,36%, privado urbano 3,43%. Repetición/matrícula: 5,29%, 4,94%, 4,17% y 0,87%, en el mismo orden.
- **Territorios:** agregación nacional de las celdas observadas; 862 celdas estatales, 271 privadas, 462 rurales y 671 urbanas.
- **Cobertura:** no balanceada; la oferta privada rural es mucho menor.
- **Confianza:** Media.
- **Interpretación permitida:** la composición sector–ámbito importa para comparar territorios.
- **No interpretar como:** efecto causal de la gestión o ruralidad; hay selección y composición no observadas.
- **Fuente adicional:** matrícula por nivel, población, ingreso y características de la oferta.

## B. Patrones exploratorios

### 5. Hay brechas rural–urbanas locales que el promedio nacional oculta

- **Descripción:** dentro del mismo departamento algunas diferencias son sustanciales.
- **Evidencia:** entre 349 departamentos con al menos 100 matrículas comparables en cada ámbito, San Luis del Palmar muestra 51,96% rural frente a 11,65% urbano en sobreedad; Feliciano, 37,69% frente a 16,32%; Saladas, 36,25% frente a 17,71%.
- **Territorios:** subconjunto indicado; umbral de estabilidad exploratorio, no oficial.
- **Cobertura:** casos con ambos ámbitos y denominadores >=100.
- **Confianza:** Media.
- **Interpretación permitida:** localizar contrastes internos para posterior diagnóstico.
- **No interpretar como:** prueba de desventaja causada por ruralidad.
- **Fuente adicional:** distancias, dispersión poblacional, oferta y nivel socioeconómico.

### 6. También aparecen contrastes internos por sector de gestión

- **Descripción:** las brechas estatal–privado en sobreedad son grandes en determinados departamentos.
- **Evidencia:** entre 244 departamentos con denominador >=100 en ambos sectores, Iguazú registra 32,17% estatal frente a 7,21% privado; Chimbas 31,66% frente a 6,84%; Santa Lucía 24,98% frente a 1,24%.
- **Territorios:** subconjunto comparable indicado.
- **Cobertura:** exige presencia suficiente de ambos sectores; excluye muchos territorios sin oferta privada comparable.
- **Confianza:** Media.
- **Interpretación permitida:** diferencia observada de composición y trayectoria.
- **No interpretar como:** eficacia relativa de los sectores.
- **Fuente adicional:** selección de matrícula, nivel, jornada y contexto socioeconómico.

### 7. La heterogeneidad intraprovincial es material

- **Descripción:** algunos promedios provinciales ocultan dispersión departamental amplia.
- **Evidencia:** entre provincias con al menos 10 unidades identificables, los mayores IQR exploratorios de sobreedad corresponden a San Juan (7,01 puntos porcentuales), Salta (6,65), Santiago del Estero (6,43), Chaco (6,06) y Mendoza (5,68).
- **Territorios:** departamentos identificables de esas provincias.
- **Cobertura:** provincias con n>=10; no se comparan como ranking de desempeño.
- **Confianza:** Alta para dispersión, Media para su interpretación.
- **Interpretación permitida:** el promedio provincial no basta para focalizar el diagnóstico.
- **No interpretar como:** que una provincia tenga peor política educativa.
- **Fuente adicional:** series, población y composición de niveles.

### 8. Ruralidad agregada explica poco por sí sola la variación de sobreedad

- **Descripción:** la proporción de matrícula rural tiene una asociación lineal débil con sobreedad departamental.
- **Evidencia:** Pearson r=0,101; n=435 departamentos con matrícula rural observada. Con repetición, r=0,014.
- **Territorios:** 435 unidades; 71 sin celda rural observada no se codifican como ruralidad cero.
- **Cobertura:** casos completos únicamente.
- **Confianza:** Media.
- **Interpretación permitida:** una única proporción estructural no resume los contrastes rurales observados dentro de territorios.
- **No interpretar como:** ausencia de problemas rurales ni inexistencia de relaciones no lineales/contextuales.
- **Fuente adicional:** población rural, accesibilidad, oferta y distancias.

### 9. Las señales de trayectoria forman un patrón multivariado

- **Descripción:** no promoción se asocia con repetición y, en menor medida, con sobreedad y salida sin pase.
- **Evidencia:** r repetición–no promoción=0,787; sobreedad–no promoción=0,556; repetición–salida sin pase=0,432; n=506.
- **Territorios:** 506 unidades.
- **Cobertura:** casos completos departamentales.
- **Confianza:** Alta para las asociaciones; Baja para cualquier explicación.
- **Interpretación permitida:** conviene mostrar un perfil de señales separado, no un score.
- **No interpretar como:** dimensiones independientes ni relaciones causales.
- **Fuente adicional:** definiciones temporales, cohortes y datos longitudinales.

### 10. La calidad de dato es en sí misma una señal para la herramienta

- **Descripción:** la cobertura territorial no es total y la apertura protege unidades mediante enmascaramiento.
- **Evidencia:** 506/529 unidades GeoRef identificables; 8 denominaciones pendientes; 15 no representadas; 68/68/67 filas Enmascarado y 2 Sin datos según base; 8 celdas analíticas sin Trayectoria.
- **Territorios:** detalle en `cobertura_territorial_ra_2025.csv`.
- **Cobertura:** auditoría completa de las tres bases.
- **Confianza:** Alta.
- **Interpretación permitida:** la app futura necesita estados de disponibilidad visibles.
- **No interpretar como:** cero, ausencia de oferta o falta de estudiantes.
- **Fuente adicional:** aclaración oficial específica de cada ausencia y próximas publicaciones RA.

## C. Hipótesis que requieren otras fuentes

- Los contrastes rural–urbanos podrían relacionarse con accesibilidad, dispersión y estructura de oferta; RA sola no permite probarlo.
- Las diferencias estatal–privado pueden reflejar composición social, nivel, selectividad y localización.
- Los territorios con varias señales altas podrían atravesar problemas persistentes o episodios administrativos; se necesitan series.
- Para pares comparables podrían usarse matrícula total, proporción rural, proporción estatal y localizaciones. Deben excluirse repetición, sobreedad, promoción, no promoción y salida sin pase para evitar circularidad. Faltan población por edad, pobreza/ingresos, conectividad territorial, distancias y estructura de oferta confirmada.

## D. Limitaciones

- Es una fotografía RA 2025; no se mezcla con otros años.
- Los cocientes combinan categorías/años compatibles disponibles, pero no sustituyen indicadores oficiales por nivel.
- La falta de oferta en una celda y la falta de dato no siempre pueden distinguirse; nunca se fuerza cero.
- Las filas Enmascarado pueden aportar a totales provinciales bajo reglas específicas, pero este EDA departamental no las redistribuye ni las incorpora.
- La unidad de varias variables de Características figura de modo ambiguo; solo `localizacion` se usa sustantivamente.
- No hay ajuste por tamaño, estructura etaria, nivel socioeconómico ni composición por nivel.

## E. Preguntas nuevas

- ¿Persisten las señales en años RA anteriores?
- ¿Qué parte de las diferencias se explica por nivel y modalidad?
- ¿Cambian los patrones al incorporar población en edad escolar y tasas de escolarización?
- ¿Los resultados Aprender acompañan o contradicen las señales de trayectoria?
- ¿Qué explica las unidades sin representación y denominaciones pendientes?

## F. Posibles usos para política pública

- Tablero de disponibilidad y calidad antes de mostrar indicadores.
- Perfil multidimensional de señales, sin ranking compuesto.
- Comparación de brechas internas rural–urbano y estatal–privado con denominadores visibles.
- Detección de territorios atípicos para investigación y validación local.
- Visualización de dispersión intraprovincial para evitar decisiones basadas solo en promedios.

## G. Indicadores que todavía no deberían mostrarse en la app

- “Tasa de abandono”: `salidos sin pase / matrícula inicial` no debe rotularse así.
- Tasas oficiales de promoción, repitencia o sobreedad por nivel hasta validar denominadores y universos específicos.
- Variables de equipamiento, conectividad, biblioteca, subvención y otras Características cuya unidad agregada permanece por verificar.
- Comparaciones crudas estatal–privado o rural–urbano sin cobertura, denominadores y advertencias de composición.
- Cualquier indicador para unidades no representadas, pendientes, Enmascarado o Sin datos.
