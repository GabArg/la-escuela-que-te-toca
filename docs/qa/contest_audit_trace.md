# Trazabilidad de la auditoría del concurso

Documento de trabajo previo a cambios de aplicación. Rama: `fix/contest-audit-p0-p1`. Commit base: `6d406d45b008d64cf2980afd0140d99b8b39e979`.

## Inventario funcional y metodológico

| Tema | Archivo | Función o elemento | Entrada | Transformación | Salida | Dónde se muestra |
|---|---|---|---|---|---|---|
| RA histórico 2011–2025 | `src/ingestion/ra_historico.py` | `load_raw`, `attach_territory`, `transform_family`, `build_long` | 45 CSV en `data/raw/ra_historico/{anio}/` | Normaliza columnas y nombres; asigna GeoRef por igualdad o puente confirmado; preserva `Enmascarado`/`Sin datos` sin ID; suma componentes comparables | `data/processed/ra_2011_2025_long.parquet` | Historia territorial y storytelling, a través de `load_history` |
| Fuentes y hashes RA | `data/dictionaries/fuentes_ra_historico.csv` | manifiesto | CSV oficiales 2011–2025 | Registra URL, fecha, SHA-256, filas, columnas y filas especiales | inventario auditable de 45 archivos | Metodología documental; no se expone completo en UI |
| Comparabilidad RA | `data/dictionaries/comparabilidad_ra_2011_2025.csv` | inventario anual de variables | esquemas de Matrícula, Trayectoria y Características | Aprueba solo componentes estables y documenta exclusiones | reglas de comparabilidad | `docs/metodologia/comparabilidad_ra_2011_2025.md`; resumen en Metodología |
| Diccionario RA | `data/raw/acceso_escolar/diccionario_bases_ra.xlsx` y URL en manifiesto histórico | hojas del diccionario oficial | planilla oficial | define campos RA usados por los pipelines | metadatos de variables | documentación metodológica y auditorías |
| Sobreedad histórica | `src/analysis/ra_historico.py` | `department_counts`, `build_indicators` | parquet largo con `sobreedad` y `matricula_grados_comparables` | excluye filas sin `departamento_id`, agrega por departamento y divide conteos | `proporcion_sobreedad` por territorio/año | Historia territorial, perfiles y portada |
| 28,0% → 11,9% | `app/components/storytelling.py` | `national_overage_story` | panel departamental retornado por `load_history` | suma numeradores y denominadores de los departamentos identificados para 2011 y 2025 | diccionario con porcentajes 2011/2025 | bloque “Una trayectoria nacional” de Inicio |
| Curva 2011–2025 | `app/components/story_visuals.py` | `national_trajectory_svg` | mismo panel departamental | agregado anual de conteos identificados y cociente ponderado | SVG de trayectoria | storytelling de Inicio |
| RA 2025 departamental | `src/ingestion/educacion_departamental.py` | `prepare_dataset`, `attach_georef_ids`, `run_pipeline` | tres CSV 2025 agregados | normaliza, asigna GeoRef y conserva filas especiales sin ID | tres parquets en `data/processed/educacion_departamental/` | insumo del perfil 2025 |
| Indicadores RA 2025 | `src/analysis/ra_2025.py` | `prepare_matricula`, `prepare_trayectoria`, `aggregate_departments` | parquets RA 2025 por sector/ámbito | excluye filas sin ID; suma conteos; recalcula cocientes después de agregar | `ra_2025_analitico.parquet` | perfiles territoriales, comparables y caso guiado |
| Salidos sin pase | `src/analysis/ra_2025.py` | `prepare_trayectoria`, `aggregate_departments` | `ssp_1`…`ssp_20` y `inicial_1`…`inicial_20` | numerador `salidos_sin_pase`; denominador `matricula_inicial`; cociente departamental | `proporcion_salidos_sin_pase_sobre_inicial` | perfil y caso Ramón Lista–Quebrachos |
| Caso Ramón Lista / Quebrachos | `app/components/storytelling.py` | `guided_case_data`, `render_guided_case` | perfiles, pares y brechas publicados | fija IDs 34063/86140; valida el par; recupera estructura y diferencia educativa | payload narrativo y HTML | Inicio, secciones 03–04 |
| Pares comparables | `src/analysis/pares_comparables.py` | `BASE_SPECS`, `neighbor_table`, `educational_gaps` | perfiles territoriales | similitud solo con territorio, contexto y oferta; resultados educativos se adjuntan después | pares y brechas | Inicio y vista Comparar |
| Señales | `src/features/perfiles_territoriales.py` | `add_coverage_and_flags`, `SIGNAL_RULES`, `prioritized_signals` | perfil integrado y clasificaciones históricas | activa reglas transparentes, mezcla actualmente señales educativas y documentales, asigna `nivel_confianza` | `senales_prioritarias_perfiles.parquet` | perfil, mapas y radar de investigación |
| Clasificación histórica | `src/analysis/ra_historico.py` | `classify_series` | indicadores por territorio/año | cuartiles anuales, Spearman, delta, anomalía y mediana de diferencias observadas | clasificación por indicador/territorio | historia, perfiles y señales |
| Radar de investigación | `app/components/senales.py` | `filter_signals`, `render_signals` | señales publicadas y filtros | ordena alfabéticamente y renderiza `head(40)` | hasta 40 tarjetas | sección Investigar |
| CSS funcional/storytelling | `app/assets/styles.css` | variables y reglas `.story-*`, sidebar, botones, responsive | HTML/DOM Streamlit | colores, layout, cascada, estados hover y media queries | estilo inyectado | toda la app |
| Fuentes y metodología UI | `app/components/metodologia.py` | `render_methodology` | texto embebido y documentación local | organiza fuentes, años, límites y uso de IA | sección metodológica | navegación “Metodología” |
| Carga pública | `app/components/data.py` | `artifact_path`, `_verify_public`, `load_*` | `data/public` y `manifest.json` | verifica SHA-256; usa procesados solo como respaldo explícito | DataFrames de serving | todas las vistas |
| Navegación | `app/app.py`, `app/components/escalas.py`, `app/components/territorio.py` | `main`, `render_main_navigation`, `_go`, colas de navegación | estado de sesión y selectores | conserva selección y decide vista/escala | navegación Streamlit | header, sidebar, Inicio, Explorar y Comparar |
| Referencias visibles de autoría | repositorio completo | búsqueda de `GabArg`, autor, perfiles y URLs | app, metadatos, documentación y README | auditoría textual pendiente de clasificación pública/no pública | lista de exposiciones | potencialmente app desplegada y enlaces salientes |

## Flujo crítico resumido

1. Los CSV oficiales se leen con `load_raw` y se vinculan territorialmente con `attach_territory`.
2. `transform_family` suma columnas comparables por fila sector–ámbito; `build_long` conserva también filas especiales sin ID.
3. `department_counts` descarta toda fila sin `departamento_id` y suma las restantes.
4. `build_indicators` calcula los tres cocientes desde conteos agregados.
5. `national_overage_story` vuelve a sumar los conteos departamentales identificados y presenta el cociente como nacional.
6. Para 2025, el caso guiado usa el pipeline RA específico, los perfiles publicados y la brecha adjuntada luego de seleccionar el par estructural.

## Puntos de control para los gates

- El rótulo “nacional” depende de demostrar que las filas sin ID no contienen conteos publicados que pertenezcan al total nacional.
- La comparabilidad temporal requiere verificar que el universo de componentes, sector, ámbito y cobertura territorial sea estable entre 2011 y 2025.
- “Salidos sin pase” es un conteo RA dividido por matrícula inicial; la definición temporal exacta debe confirmarse en el diccionario oficial antes de redactar el resultado.
- Las filas `Enmascarado`, `Sin datos` y `por_verificar` se preservan en el largo, pero hoy quedan fuera de los agregados de la app.
- La superficie pública de seudónimo debe evaluarse separando contenido controlado por la app de identidad expuesta por la plataforma o por GitHub.
