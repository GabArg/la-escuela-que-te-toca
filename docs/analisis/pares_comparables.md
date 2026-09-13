# Análisis del motor de pares comparables

## A. Calidad general

El motor encuentra pares nacionales para 504 de 529 territorios; 25 quedan sin vecinos elegibles por cobertura o restricciones estructurales. Produce 2.520 relaciones nacionales y 2.455 provinciales. La distancia nacional mediana es 0,02361.

En el conjunto nacional y provincial hay 987 relaciones de alta comparabilidad, 2.135 de comparabilidad media y 1.853 de comparabilidad baja. Entre los pares nacionales son 575, 1.291 y 654, respectivamente. La estabilidad evita ponderar dos veces las especificaciones equivalentes `sin oferta` y `solo territorio+contexto`.

## B. Estabilidad

- Sin conectividad: conserva en promedio 73,1% del top 5; rho de distancias comunes 0,911; 10 territorios quedan bajo 40%.
- Sin oferta: conserva 61,5%; rho 0,826; 32 territorios quedan bajo 40%.
- Solo territorio+contexto: es idéntica a `sin oferta`, por construcción.

La oferta cambia más vecinos que retirar conectividad. Esto no demuestra que la oferta explique resultados; solo muestra su influencia en la definición estructural.

## C. Pares y brechas para investigar

Entre relaciones con comparabilidad alta o media aparecen:

- Collón Curá–Picunches: 30,13 puntos de brecha absoluta en sobreedad.
- Mercedes (Corrientes)–Pehuenches: 10,33 puntos en repetición.
- Ramón Lista–Quebrachos: 9,15 puntos en salidos sin pase.
- El Alto–Minas: 52,55 puntos en Lengua satisfactoria o avanzada.
- Vicente López–Tres de Febrero: 20,48 puntos en Matemática satisfactoria o avanzada.

Son brechas descriptivas que requieren verificar tamaño, cobertura y contexto local. No identifican territorio superior, eficiencia ni causa.

## D. Pares exploratorios anteriores

Ituzaingó–San Isidro, Salto–San Justo, Lobos–San Justo, Comuna 1–Morón y General Pueyrredón–Capital (La Rioja) cumplen las restricciones y comparten las 12 variables. Sus distancias son 0,0526; 0,0475; 0,0517; 0,0290 y 0,0817 respectivamente, pero ninguno entra en el top 5 de ninguno de sus integrantes. El motor los reemplaza porque encuentra territorios estructuralmente más cercanos al incorporar vivienda, servicios y una oferta balanceada; no porque el vínculo anterior sea imposible.

## E. Casos para investigar

Las brechas anteriores, los territorios con estabilidad menor a 40% y los 25 sin vecino elegible merecen revisión. Un vecino inestable debe mostrarse con advertencia en la futura app y no como referencia única.

## F. Limitaciones

- La similitud es relativa a doce variables disponibles, no equivalencia total.
- La calidad baja no significa mal desempeño.
- La salida contiene relaciones dirigidas; A puede elegir B aunque B no elija A.
- Las brechas de Aprender están limitadas por su cobertura, especialmente Matemática.
- Dos territorios pueden ser cercanos estructuralmente y diferir en factores no observados.
- No se infiere causalidad ni se recomiendan políticas específicas.

## G. Recomendaciones para la app futura

Mostrar cinco pares con distancia, calidad, estabilidad, variables similares y diferencias principales; permitir alternar nacional/provincial; advertir cobertura; separar visualmente estructura y brechas educativas; y evitar palabras como mejor, peor o eficiencia.
