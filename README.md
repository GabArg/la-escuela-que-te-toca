# La escuela que te toca

Aplicación interactiva para el análisis territorial de la educación argentina a partir de datos abiertos oficiales.

## Propósito

Construir una herramienta reutilizable y escalable que permita explorar desigualdades, patrones y oportunidades de mejora en el sistema educativo desde una perspectiva territorial. El proyecto se inicia en el marco del concurso **Contar con Datos 2026**, con vocación de continuidad más allá de esa instancia.

## Problema que busca resolver

La información educativa suele encontrarse dispersa entre distintas fuentes, períodos y escalas geográficas. El proyecto busca facilitar su integración, análisis y comunicación para apoyar diagnósticos comparables y decisiones basadas en evidencia.

> **TODO:** delimitar las preguntas prioritarias, la unidad territorial principal y el alcance temporal del primer producto.

## Público objetivo

- Gobiernos nacionales y provinciales.
- Municipios y equipos de gestión local.
- Responsables de política educativa.
- Investigadores y organizaciones de la sociedad civil.
- Comunidades educativas y ciudadanía interesada.

## Dimensiones iniciales de análisis

1. **Acceso:** disponibilidad y posibilidad efectiva de ingresar al sistema educativo.
2. **Permanencia:** continuidad de las y los estudiantes dentro del sistema.
3. **Trayectoria:** progresión, repitencia, sobreedad, egreso y otros recorridos educativos.
4. **Aprendizaje:** resultados y condiciones vinculadas con los aprendizajes.
5. **Equidad:** brechas territoriales y sociales en oportunidades y resultados educativos.

> **TODO:** acordar definiciones operativas e indicadores para cada dimensión según la disponibilidad y calidad de las fuentes oficiales.

## Estado actual

Proyecto en etapa inicial: organización del repositorio, inventario de fuentes y definición metodológica. Todavía no se han producido análisis, resultados ni visualizaciones finales.

## Datos y transparencia

La versión pública utiliza **únicamente datos abiertos**, con prioridad para fuentes oficiales. Las fuentes, transformaciones, decisiones metodológicas y usos de inteligencia artificial se documentarán en `docs/`.

## Estructura general

- `data/`: datos originales, procesados, externos y diccionarios.
- `notebooks/`: exploración, cruces territoriales y análisis experimental.
- `src/`: código reutilizable del flujo de datos y análisis.
- `app/`: aplicación interactiva.
- `docs/`: metodología, fuentes, decisiones y documentación del concurso.
- `outputs/`: productos generados.
- `tests/`: pruebas automatizadas.

## Próximos pasos

- Completar el inventario de fuentes oficiales.
- Definir unidades geográficas, períodos e indicadores.
- Establecer criterios de calidad, trazabilidad y actualización.
- Implementar el primer flujo reproducible de ingestión y limpieza.

