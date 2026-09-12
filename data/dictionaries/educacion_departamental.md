# Diccionario de datos: educación departamental

Documentación inicial de las bases abiertas del Relevamiento Anual (RA) 2025 agregadas por departamento. Esta etapa prepara archivos separados para el cruce territorial; no construye todavía un dataset maestro definitivo ni indicadores derivados.

## Procedencia y selección

- **Fuente:** Subsecretaría de Información y Evaluación Educativa, Secretaría de Educación de la Nación.
- **Catálogo oficial:** `https://www.argentina.gob.ar/capital-humano/educacion/informacion-y-evaluacion-educativa/datos-abiertos-de-la-subsecretaria-de`.
- **Buscador oficial:** `https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/datos-abiertos-de-la-secretaria-de-educacion`.
- **Fecha de descarga y consulta:** 2026-09-12.
- **Año seleccionado:** 2025, última edición RA listada en el catálogo al momento de la consulta.

| Dataset | Archivo raw | URL exacta | Filas | Columnas raw | Grano observado | Dimensiones |
|---|---|---|---:|---:|---|---|
| Matrícula | `2025_matricula_agregada.csv` | `https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/IQDZWBqkmmvuSasr3wVDZIhwAduAVd1G1KpOSmI4mDbbV4E?e=CLjtl2` | 1.217 | 103 | provincia, departamento, sector, ámbito | Acceso; Trayectoria; Equidad |
| Trayectoria | `2025_trayectoria_agregada.csv` | `https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/IQDLGg-8IsrvQ7GjtoSuTg36AahBDzrs4gFKEDnNMjwAOUI?e=SiVssS` | 1.210 | 316 | provincia, departamento, sector, ámbito | Permanencia; Trayectoria; Equidad |
| Características | `2025_caracteristicas_agregada.csv` | `https://ministeriodeeducaciondelanacion-my.sharepoint.com/:x:/g/personal/santiago_pomeranz_educacion_gob_ar/IQAR5DtMGXufQ4GWkxAbhQbWAaMz29BSWfoNPrvTA_ppkSo?e=vLzf4X` | 1.217 | 67 | provincia, departamento, sector, ámbito | Acceso; Equidad |

## Campos comunes preparados

| Campo | Descripción | Tipo | Año | Fuente | Observaciones |
|---|---|---|---:|---|---|
| `dataset` | Identifica la base de origen: matrícula, trayectoria o características. | texto | 2025 | Elaboración propia | No es un campo del raw. |
| `anio` | Año declarado por el catálogo y nombre del archivo. | entero | 2025 | RA | El año no aparece como columna en los CSV originales. |
| `url_origen` | Enlace exacto publicado por el buscador oficial. | texto | 2025 | SSIEE | Se conserva para trazabilidad. |
| `fecha_descarga` | Fecha en que se descargó el archivo. | fecha ISO como texto | 2025 | Elaboración propia | Valor: `2026-09-12`. |
| `provincia_nombre_fuente` | Nombre de provincia tal como aparece en RA. | texto | 2025 | RA | No se reemplaza por el nombre GeoRef. |
| `departamento_nombre_fuente` | Nombre de departamento tal como aparece en RA. | texto | 2025 | RA | Puede contener `Enmascarado` o `Sin datos`. |
| `sector` | Sector de gestión observado en los archivos. | texto | 2025 | RA | Valores observados: Estatal y Privado. |
| `ambito` | Ámbito observado en los archivos. | texto | 2025 | RA | Valores observados: Rural y Urbano. |
| `provincia_id` | Código oficial GeoRef de provincia. | texto | 2025 | GeoRef | Añadido por cruce; preserva ceros iniciales. |
| `provincia_nombre` | Nombre oficial de provincia en GeoRef. | texto | 2025 | GeoRef | Nulo cuando el territorio no es identificable. |
| `departamento_id` | Código oficial GeoRef de departamento o unidad equivalente. | texto | 2025 | GeoRef | Añadido por cruce; preserva ceros iniciales. |
| `departamento_nombre` | Nombre oficial GeoRef del departamento o unidad equivalente. | texto | 2025 | GeoRef | Nulo cuando el territorio no es identificable. |
| `clave_territorial` | Clave interna territorial definida por el pipeline GeoRef. | texto | 2025 | Proyecto | No es un identificador oficial. |
| `match_metodo` | Método de correspondencia territorial. | texto | 2025 | Elaboración propia | `nombre_normalizado`, `tabla_puente_documentada`, `puente_pendiente` o `no_identificable_en_fuente`. |

## Variables de cada base

Todos los encabezados se normalizan a minúsculas, ASCII y snake_case. Las columnas cuantitativas se preparan como enteros anulables (`Int64`); los blancos del raw se convierten en nulos. Se conservan todas las métricas publicadas, sin agregarlas ni reinterpretarlas.

| Dataset | Familias de campos confirmadas | Tipo preparado | Observaciones |
|---|---|---|---|
| Matrícula | Matrícula por sala y año de estudio; repitencia; sobreedad; secciones; grupos multiedad o multinivel. | entero anulable | Los nombres abreviados se conservan normalizados. Su definición precisa debe consultarse en el diccionario oficial RA antes de construir indicadores. |
| Trayectoria | Matrícula inicial y final; entrados; salidos sin pase; promovidos; no promovidos; regulares; otros; egresados; desagregaciones marcadas con prefijo `m_`. | entero anulable | No se infiere el significado de abreviaturas como `scp` y `ssp`; queda sujeto al diccionario oficial. |
| Características | Localizaciones, electricidad, equipamiento, conectividad, cooperadora, gestión escolar, laboratorios, bibliotecas y subvención estatal. | entero anulable | Son conteos agregados publicados por territorio, sector y ámbito; no describen necesariamente a cada establecimiento individual. |

## Correspondencia con GeoRef

Los CSV no contienen códigos de provincia o departamento. El pipeline aplica:

1. Normalización reproducible de mayúsculas, acentos, espacios y puntuación.
2. Dos equivalencias documentadas para nombres provinciales: Ciudad de Buenos Aires y Tierra del Fuego.
3. Una tabla puente explícita de 11 variantes departamentales en `puente_nombres_departamentos_2025.csv`: 3 confirmadas y 8 pendientes de evidencia oficial suficiente.
4. Ausencia deliberada de asignación para `Enmascarado` y `Sin datos`.

| Cobertura observada | Matrícula | Características | Trayectoria |
|---|---:|---:|---:|
| Pares provincia–departamento publicados | 537 | 537 | 539 |
| Unidades GeoRef con ID asignado | 506 | 506 | 506 |
| Variantes pendientes sin ID asignado | 8 | 8 | 8 |
| Unidades GeoRef sin representación identificable | 15 | 15 | 15 |
| Pares `Enmascarado` | 23 | 23 | 23 |
| Pares `Sin datos` | 0 | 0 | 2 |

La cobertura indica correspondencia territorial, no completitud de cada variable ni calidad de resultados.

## Limitaciones y comparabilidad

- La granularidad real es departamento o unidad equivalente × sector × ámbito; no es establecimiento ni estudiante.
- Las bases son agregadas y no permiten inferir relaciones individuales ni causalidad.
- Hay 15 unidades GeoRef sin representación identificable en 2025. La fuente no permite afirmar cuáles están contenidas en cada agregado `Enmascarado`.
- No se realizan asignaciones manuales para registros enmascarados o sin datos.
- Las 11 variantes nominales están separadas en una tabla puente auditable; solo 3 abreviaturas inequívocas se aplican y las otras 8 quedan pendientes. No se usa emparejamiento difuso automático.
- No deben combinarse años sin verificar cambios de cobertura, definiciones, categorías y diccionarios.
- Esta integración no incluye Aprender y no habilita comparaciones con operativos de evaluación.
- Antes de construir indicadores deben verificarse las definiciones del diccionario oficial RA, especialmente abreviaturas y universos de cada conteo.
