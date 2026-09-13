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

El proyecto cuenta con pipelines territoriales y educativos auditados, perfiles integrados, series RA 2011–2025, contexto Censo 2022, Aprender 2024 y un motor de pares estructuralmente comparables. La primera versión funcional del MVP presenta estas capacidades en Streamlit; el diseño visual todavía es preliminar.

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

## Instalación

```bash
python -m venv .venv
# Activar el entorno según el sistema operativo
python -m pip install -r requirements.txt
```

## Datos procesados

Los parquets no se versionan. Cada módulo de `src/ingestion`, `src/features` y `src/analysis` expone una función o ejecución reproducible. Para reconstruir las capas finales, una vez disponibles sus insumos raw:

```bash
python -m src.features.perfiles_territoriales
python -m src.analysis.pares_comparables
```

La app intenta llamar esos módulos si falta una salida final; no duplica la lógica analítica.

## Ejecutar la app

```bash
streamlit run app/app.py
```

La navegación incluye Inicio, Perfil territorial, Historia, Comparables, Dónde mirar y Metodología.

## Alcance interpretativo

Los resultados son exploratorios y descriptivos. Las asociaciones no demuestran causalidad, los pares son similares por estructura y contexto —no por desempeño— y ninguna ausencia se interpreta como cero. La aplicación no crea un score ni un ranking educativo.

## Próximos pasos

- Probar el MVP con usuarios reales.
- Refinar accesibilidad e identidad visual.
- Incorporar el mapa localizador sin usarlo como ranking.
- Versionar outputs y procesos de actualización.
