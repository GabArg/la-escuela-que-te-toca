# Metodología del módulo Aprender

## Corte seleccionado

Se utiliza Aprender Secundaria 2024, operativo censal aplicado al último año (5.º/6.º según la estructura jurisdiccional) en Lengua y Matemática. La publicación informa 11.846 escuelas participantes (96,6 %) y 379.050 estudiantes (70,2 %). “Censal” describe el diseño, no cobertura completa ni ausencia de error.

Los archivos agregados oficiales tienen grano `jurisdicción × departamento × sector × ámbito`. Sus cuatro columnas de desempeño son conteos ponderados, no porcentajes. El pipeline suma los conteos entre sector y ámbito y recién entonces calcula la participación de cada nivel. Una distribución se publica solo cuando están presentes las cuatro categorías; una categoría ausente no se trata como cero.

## Territorialidad y confidencialidad

La salida usa únicamente agregados departamentales publicados. El match con GeoRef reutiliza normalización y puentes ya auditados: 499 unidades obtienen ID, mientras las categorías `Enmascarado` y ocho denominaciones con puente pendiente quedan sin asignación. No se usa similitud difusa, no se distribuyen valores enmascarados y no se intenta reidentificar escuelas o estudiantes.

## Ponderación

Aunque el operativo es censal, la base agregada publica conteos ponderados. El módulo conserva esos conteos y marca `ponderado=True`. En Primaria 2024 el diseño es muestral complejo: los ponderadores corrigen probabilidades desiguales y no respuesta. Por ello no se producen estimaciones departamentales primarias ni porcentajes simples.

## Comparabilidad

La etiqueta Alta asignada a Secundaria 2024 vale únicamente para comparación transversal dentro del operativo. No valida una serie temporal. Coincidencia de nombre, grado o área no demuestra invariancia de escala, puntos de corte, marco, cobertura o instrumentos. Primaria 2024 (3.º, muestral) no es comparable con Primaria 2023 (6.º, censal). Los cuestionarios de contexto requieren auditoría pregunta por pregunta.

## Cobertura analítica

- 499 unidades identificadas en al menos una fila.
- Lengua: 480 distribuciones completas y 19 parciales.
- Matemática: 145 completas y 354 parciales.

La diferencia surge de categorías de desempeño ausentes en la publicación; no se rellenan con cero. Las correlaciones usan eliminación por pares y reportan `n`.

## Cruces y límites

Se cruza 2024 con Censo 2022, condiciones 2022 y RA 2025. La asincronía impide interpretar asociaciones como contemporáneas exactas. Spearman resume asociación monotónica, no causalidad. La comparación de pares estandariza exclusivamente variables estructurales; sus umbrales son exploratorios y no constituyen clustering, ranking ni eficiencia.

TODO: auditar documentación psicométrica común antes de habilitar cualquier serie temporal.
