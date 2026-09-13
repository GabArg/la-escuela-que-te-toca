# Estrategia de datos para deployment

## Diagnóstico

La aplicación necesita perfiles, señales, pares, brechas, serie histórica y GeoJSON. data/raw y data/processed siguen ignorados; el bundle versionado en data/public resuelve la ejecución desde un clon limpio.

## Estrategia implementada

Se genera un **bundle de aplicación versionado** en data/public, compuesto solo por los outputs públicos necesarios:

- perfiles_territoriales.parquet;
- senales_prioritarias_perfiles.parquet;
- pares_comparables.parquet;
- brechas_entre_pares.parquet;
- ra_2011_2025_long.parquet;
- departamentos_argentina.geojson;
- manifiesto con versión, fecha, tamaño y SHA-256.

El bundle completo ocupa 2,73 MB. Para este proyecto se recomienda versionarlo directamente en Git: es la alternativa más simple y robusta para Streamlit Community Cloud y el jurado, sin descargas durante el arranque.

## Alternativas

1. Git directo: elegido por tamaño, simplicidad y arranque inmediato.
2. GitHub Release u object storage: útil si el bundle crece, pero suma dependencia externa.
3. Git LFS o Docker: innecesarios para el tamaño actual.

No se reconstruye en producción: el fallback queda desactivado por defecto. La política de actualización está documentada en public_bundle.md.
