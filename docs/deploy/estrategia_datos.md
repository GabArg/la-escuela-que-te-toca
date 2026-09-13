# Estrategia de datos para deployment

## Diagnóstico

La aplicación necesita perfiles, señales, pares, brechas, serie histórica y GeoJSON. En el repositorio actual, data/raw y data/processed están ignorados. Un clon limpio no puede iniciar: los parquets no estarán presentes y la reconstrucción automática tampoco será posible porque sus insumos raw están igualmente ausentes.

## Estrategia implementada

Se genera un **bundle de aplicación versionado** en data/public, compuesto solo por los outputs públicos necesarios:

- perfiles_territoriales.parquet;
- senales_prioritarias_perfiles.parquet;
- pares_comparables.parquet;
- brechas_entre_pares.parquet;
- ra_2011_2025_long.parquet, o una proyección mínima para las series mostradas;
- departamentos_argentina.geojson;
- manifiesto con versión, fecha, tamaño y SHA-256.

El bundle completo ocupa 2,73 MB. Para este proyecto se recomienda versionarlo directamente en Git: es la alternativa más simple y robusta para Streamlit Community Cloud y el jurado, sin descargas durante el arranque.

## Alternativas

1. Git directo: elegido por tamaño, simplicidad y arranque inmediato.
2. GitHub Release u object storage: útil si el bundle crece, pero suma dependencia externa.
3. Git LFS o Docker: innecesarios para el tamaño actual.

No se recomienda reconstruir todo al iniciar Streamlit. Antes de cambiar .gitignore se debe decidir hosting, tamaño máximo y política de actualización.
