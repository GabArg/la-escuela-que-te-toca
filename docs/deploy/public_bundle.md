# Bundle público de datos

El bundle de serving está en data/public y contiene exclusivamente los artefactos abiertos que consume la aplicación.

| Archivo | Usado por | Obligatorio | Tamaño | Filas | Columnas | Reconstruible | Observaciones |
|---|---|---:|---:|---:|---:|---|---|
| perfiles_territoriales.parquet | Inicio, mapa, Perfil, Historia y contraste | Sí | 332.430 B | 529 | 119 | Sí | Perfil integrado |
| senales_prioritarias_perfiles.parquet | Perfil y Dónde mirar | Sí | 19.885 B | 751 | 8 | Sí | Reglas ya procesadas |
| pares_comparables.parquet | Comparables | Sí | 116.303 B | 4.975 | 16 | Sí | Pares nacionales y provinciales |
| brechas_entre_pares.parquet | Contraste A/B | Sí | 258.476 B | 4.975 | 22 | Sí | Brechas posteriores a similitud |
| ra_2011_2025_long.parquet | Historia | Sí | 937.497 B | 233.397 | 12 | Sí | Variables históricas admitidas |
| departamentos_argentina.geojson | Mapa | Sí | 1.051.216 B | 529 | 5 | Sí | GeoRef sin simplificar |
| manifest.json | Verificación | Sí | variable | — | — | Sí | Versión, commit, esquemas y hashes |

Tamaño de la versión 2026.09.13.1: 2.725.826 bytes incluyendo manifiesto.

No contiene fuentes raw, outputs intermedios, secretos ni rutas locales. Las capas de acceso, contexto y Aprender ya están integradas en el perfil.

## Regeneración y actualización

Desde la raíz, con data/processed disponible:

    python scripts/build_public_bundle.py

El script valida esquemas, copia bytes sin recalcular indicadores y genera SHA-256. Al actualizar datos hay que incrementar BUNDLE_VERSION, reconstruir, ejecutar tests y revisar el manifiesto.

La app busca primero data/public y verifica hashes. En desarrollo puede recurrir a data/processed y a pipelines; en producción debe usarse APP_ALLOW_PIPELINE_REBUILD=0.
