# Principios de visualización

## Reglas de diseño

1. Una visualización responde una pregunta identificable.
2. Año, fuente y cobertura aparecen junto al dato, no solo en metodología.
3. Cada dimensión conserva unidad y escala; no hay radar ni suma visual.
4. Las ausencias interrumpen líneas y dejan espacio explícito; nunca se dibujan en cero.
5. El color distingue dimensiones o estados de dato, no territorios buenos/malos.
6. La referencia principal es una mediana o distribución, no un puesto.
7. La explicación textual describe evidencia antes que interpretación.
8. Una comparación A/B muestra condiciones antes de resultados.
9. Toda señal enlaza regla, evidencia, fuente y limitación.
10. La versión móvil conserva la secuencia narrativa, aunque reduzca comparación simultánea.

## Lenguaje consistente

| Estado o concepto | Texto recomendado | No usar |
|---|---|---|
| Ausencia | Sin dato publicado identificable | 0; no existe |
| Cobertura incompleta | Parcial: faltan categorías para calcular la distribución | Bajo; incompleto sin explicar |
| Censo con participación | Operativo censal; participación informada X | Cobertura total |
| Cociente propio | Cociente exploratorio matrícula/población | Tasa de escolarización |
| Relación estadística | Se observa una asociación territorial | X explica/causa Y |
| Vecino | Similar en estructura y contexto | Similar educativamente |
| Diferencia | Brecha descriptiva | Ventaja; fracaso; ganador |
| Umbral relativo | Debajo/encima del P25/P75 territorial | Alerta roja |

## Visualizaciones candidatas

| Pregunta | Recurso | Cuándo usar | Evitar |
|---|---|---|---|
| ¿Dónde está? | Mapa localizador | Inicio y encabezado territorial | Convertirlo en mapa de resultados por defecto |
| ¿Cómo se distribuye un indicador? | Coroplético | Solo con cobertura suficiente, denominador claro y leyenda de ausencias | Conteos absolutos sin controlar población; escalas rojo/verde |
| ¿Dónde están las localizaciones? | Mapa de puntos | Cuando existan coordenadas y el punto represente localización | Inferir accesibilidad o cobertura de servicio |
| ¿Cómo está cada dimensión? | Dot plots independientes | Valor frente a mediana/rango en su propia unidad | Radar o gauge 0–100 |
| ¿Cómo evolucionó? | Línea única | Un indicador y territorio, con huecos e hitos metodológicos | Quince líneas simultáneas |
| ¿Cuánta heterogeneidad provincial hay? | Small multiples o boxplots | Misma variable/unidad y n suficiente | Ordenar provincias como ranking |
| ¿Qué cambió entre A y B? | Dot plot A/B o barras divergentes | Diferencias firmadas con punto cero significativo | Colorear automáticamente ganador/perdedor |
| ¿Cambió en dos momentos? | Slope chart | Dos años comparables y pocos casos | Usarlo si la serie tiene ruptura metodológica |
| ¿Dónde cae el territorio? | Banda de distribución | Percentiles aproximados sin puesto ordinal | Tabla ordenada 1–529 |

## Mapas

Un mapa debe servir para localizar un patrón espacial. Debe incluir categoría separada para sin dato/parcial, fecha y unidad territorial. No se usa para comparar áreas geográficas muy distintas mediante conteos ni para decorar la portada con una métrica arbitraria.

## Accesibilidad

- Contraste suficiente y paleta apta para daltonismo.
- Estado nunca comunicado solo por color.
- Texto alternativo que resuma pregunta, cobertura y patrón.
- Navegación por teclado y foco visible en la implementación futura.
- Tabla accesible equivalente para cada gráfico sustantivo.
- Números con unidad, separador local y precisión proporcional a la fuente.

## Divulgación progresiva

Nivel 1: señal y lectura breve. Nivel 2: gráfico y comparación. Nivel 3: definición, fórmula, cobertura, fuente y archivo. La transparencia no debe convertirse en ruido inicial, pero ninguna advertencia esencial puede quedar escondida exclusivamente en un tooltip.
