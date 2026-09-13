# Metodología del motor de pares comparables

## Principio

El motor responde con qué territorios resulta razonable comparar una unidad, no cuál tiene mejores resultados. La matriz de similitud se construye antes de adjuntar asistencia, trayectoria o aprendizaje. No contiene sobreedad, repetición, promoción, salidos sin pase, Aprender, banderas ni clasificaciones históricas.

## Variables y pesos

Se usan doce variables en tres dimensiones con peso total idéntico (1/3):

- Territorio: población total, superficie y densidad; 1/9 cada una.
- Contexto: internet, computadora, agua de red, cloaca y rancho/casilla; 1/15 cada una.
- Oferta: ruralidad CUE, relación secundaria/primaria, localizaciones por población escolar y localizaciones por superficie; 1/12 cada una.

Así una dimensión no domina por contener más columnas. Los pesos son conceptuales y no se optimizaron contra resultados. Asistencia 15–17 se excluye de la similitud porque es un resultado educativo censal, aunque después pueda compararse como brecha.

## Transformación y normalización

Se aplica `log1p` a población, superficie, densidad, rancho/casilla y las dos razones de localizaciones porque sus distribuciones son fuertemente asimétricas. Los demás porcentajes/proporciones conservan su escala. Cada variable se centra por mediana y divide por IQR; luego se acota a [-5, 5] para limitar la influencia de extremos.

La distancia es Manhattan ponderada sobre variables compartidas:

`d(i,j) = suma(w_k × |z_ik-z_jk| / 10) / suma(w_k compartidos)`

Con el recorte, su rango es [0,1]: menor distancia implica mayor semejanza estructural, nunca mejor desempeño.

## Nulos y elegibilidad

No se imputa ni se usa cero. Un par exige al menos 9 de 12 variables compartidas y dos variables por cada dimensión. Además, la razón entre poblaciones no puede superar 10 y la diferencia absoluta de ruralidad no puede superar 0,50. Se permiten pares interprovinciales. Se generan hasta cinco vecinos nacionales y hasta cinco dentro de la provincia.

## Explicabilidad

Para cada par se informan las tres diferencias estandarizadas menores y las tres mayores, cantidad y lista de variables compartidas y cobertura. La explicación es estructurada; no se genera una conclusión libre.

## Calidad del par

Los umbrales se fijan con las distancias de los vecinos nacionales: P25=0,019286 y P75=0,029060.

- Alta: distancia ≤ P25, cobertura completa y estabilidad ≥0,60.
- Media: distancia ≤ P75, cobertura ≥0,80 y estabilidad ≥0,40.
- Baja: cualquier otro caso.

La categoría utiliza solo distancia, cobertura y estabilidad. No utiliza resultados educativos.

## Sensibilidad

Se comparan cuatro especificaciones: base, sin internet/computadora, sin oferta y territorio+contexto. Las dos últimas son matemáticamente idénticas en la versión base; se muestran para hacer explícita esa equivalencia, pero se cuentan una sola vez al calcular calidad. La estabilidad territorial es la proporción de vecinos base que permanece en el top 5. La correlación de distancias usa únicamente pares presentes en ambos top 5.

## Brechas posteriores

Una vez congelados los vecinos se calculan diferencias absolutas, en puntos porcentuales, de asistencia, sobreedad, repetición, salidos sin pase y aprendizaje. Aprender solo produce brecha cuando ambos territorios tienen distribución completa. Las brechas no retroalimentan distancia, pesos, elegibilidad ni calidad.

## Limitaciones

Los datos estructurales son principalmente de 2022; RA es 2025 y Aprender 2024. La distancia depende del conjunto elegido, los filtros son amplios pero normativos y cercanía estadística no garantiza comparabilidad institucional. Falta accesibilidad efectiva, dispersión intradepartamental, capacidad escolar y contexto laboral. El orden 1–5 es técnico del vecino, no ranking educativo.
