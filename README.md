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

El proyecto cuenta con pipelines auditados, perfiles integrados, series RA 2011–2025, contexto Censo 2022, Aprender 2024, pares comparables y un MVP Streamlit con mapa e identidad visual.

## Datos y transparencia

La versión pública utiliza **únicamente datos abiertos**, con prioridad para fuentes oficiales. Las fuentes, transformaciones, decisiones metodológicas y usos de inteligencia artificial se documentarán en `docs/`.

## Estructura general

- `data/`: datos originales, procesados, bundle público y diccionarios.
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

## Bundle público

La aplicación usa primero el bundle mínimo versionado en `data/public`. Incluye solo los artefactos finales y el manifiesto necesarios para serving, sin fuentes raw.

Para regenerarlo desde outputs procesados locales:

```bash
python scripts/build_public_bundle.py
```

En producción se recomienda definir `APP_ALLOW_PIPELINE_REBUILD=0`. Los hashes, esquemas y tamaños están en `data/public/manifest.json`. Véase `docs/deploy/public_bundle.md`.

## Reconstrucción para desarrollo

Los outputs completos de `data/processed` y los insumos raw siguen ignorados. Para reconstruir las capas finales:

```bash
python -m src.features.perfiles_territoriales
python -m src.analysis.pares_comparables
```

La app solo intenta llamar esos módulos como respaldo de desarrollo; un deployment normal no reconstruye las fuentes.

## Ejecutar la app

```bash
streamlit run app/app.py
```

La navegación incluye Inicio, Perfil territorial, Historia, Comparables, Dónde mirar y Metodología.

## Alcance interpretativo

Los resultados son exploratorios y descriptivos. Las asociaciones no demuestran causalidad, los pares son similares por estructura y contexto —no por desempeño— y ninguna ausencia se interpreta como cero. La aplicación no crea un score ni un ranking educativo.

## Próximos pasos

- Probar el MVP con usuarios reales.
- Completar auditoría formal de accesibilidad.
- Probar el deployment público y el enlace anónimo.
- Definir el ciclo de actualización del bundle.
