# Estrategia de datos para deployment

## Diagnóstico

La aplicación necesita perfiles, señales, pares, brechas, serie histórica y GeoJSON. En el repositorio actual, data/raw y data/processed están ignorados. Un clon limpio no puede iniciar: los parquets no estarán presentes y la reconstrucción automática tampoco será posible porque sus insumos raw están igualmente ausentes.

## Estrategia recomendada

Generar en CI o en una release un **bundle de aplicación versionado**, compuesto solo por los outputs públicos necesarios:

- perfiles_territoriales.parquet;
- senales_prioritarias_perfiles.parquet;
- pares_comparables.parquet;
- brechas_entre_pares.parquet;
- ra_2011_2025_long.parquet, o una proyección mínima para las series mostradas;
- departamentos_argentina.geojson;
- manifiesto con versión, fecha, tamaño y SHA-256.

El deployment debe descargar ese bundle una vez al construir la imagen o recibirlo como artefacto de release. No debe descargar cientos de fuentes ni ejecutar toda la ingeniería de datos por sesión. La app debe seguir fallando con un mensaje legible si falta un artefacto.

## Alternativas

1. Versionar outputs seleccionados con Git LFS: simple, pero agrega dependencia operativa.
2. Publicar bundle en release/object storage con URL y hash: opción recomendada.
3. Imagen Docker con artefactos incorporados: reproducible, si el hosting admite contenedores.

No se recomienda reconstruir todo al iniciar Streamlit. Antes de cambiar .gitignore se debe decidir hosting, tamaño máximo y política de actualización.
