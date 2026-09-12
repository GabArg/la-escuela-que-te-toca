# Diccionario de datos: territorios de Argentina

Base maestra de provincias y departamentos o unidades territoriales equivalentes construida a partir de GeoRef Argentina. La descarga consultada el **2026-09-12** contiene 24 provincias y 529 departamentos o unidades territoriales equivalentes según GeoRef; no se asume que todas estas unidades reciban jurídicamente el nombre de departamento.

- **Fuente:** GeoRef Argentina.
- **Página oficial:** `https://www.argentina.gob.ar/georef/descarga-de-la-base-completa`.
- **Fecha de descarga y consulta:** 2026-09-12.
- **Tratamiento de identificadores:** los IDs oficiales se preservan como texto para no perder ceros iniciales.
- **Tratamiento geométrico:** las geometrías se conservan como las entrega GeoRef, sin simplificación.

## Mapeo de campos

| Campo resultante | Campo GeoRef | Descripción | Fuente | Tipo | Observaciones |
|---|---|---|---|---|---|
| `provincia_id` | `provincia.id` en departamentos; `id` en provincias | Código oficial de la provincia asociada al departamento. | GeoRef Argentina | texto | Se preserva sin conversión numérica. |
| `provincia_nombre` | `nombre` en provincias | Nombre oficial de la provincia. | GeoRef Argentina | texto | Se toma del recurso de provincias mediante `provincia_id`. |
| `departamento_id` | `id` en departamentos | Código oficial del departamento o unidad equivalente publicada por GeoRef. | GeoRef Argentina | texto | Se preserva sin conversión numérica. En la descarga validada es único a nivel nacional y no se modifica. |
| `departamento_nombre` | `nombre` en departamentos | Nombre oficial del departamento o unidad equivalente. | GeoRef Argentina | texto | La clasificación territorial proviene directamente del recurso de departamentos. |
| `clave_territorial` | Derivado | Clave interna formada como `provincia_id-departamento_id` para facilitar validaciones y futuros joins. | Elaboración propia sobre códigos de GeoRef | texto | Es una construcción interna del proyecto y no es un identificador oficial de GeoRef. No reemplaza ni modifica `departamento_id`. |
| `geometry` | `geometry` de cada Feature | Geometría oficial de la unidad territorial. | GeoRef Argentina | geometría GeoJSON | Solo está en `departamentos_argentina.geojson`; se conserva sin simplificación. |

## Archivos fuente y salidas

- Fuente de provincias: `data/raw/georef/provincias.json`.
- Fuente de departamentos: `data/raw/georef/departamentos.geojson`.
- Tabla maestra: `data/processed/territorios_argentina.parquet`.
- Geometrías: `data/processed/departamentos_argentina.geojson`.

Los recursos se obtienen desde los endpoints oficiales de GeoRef:

- `https://apis.datos.gob.ar/georef/api/provincias.json`
- `https://apis.datos.gob.ar/georef/api/departamentos.geojson`

El comando `python -m src.ingestion.georef --download` permite reproducir la descarga y el procesamiento cuando los archivos raw todavía no existen. Por seguridad, se detiene si alguno de los destinos raw ya está presente.

## Controles de integridad

- Identificadores no nulos ni vacíos.
- Identificadores de provincia únicos en su catálogo.
- Identificadores de departamento y claves territoriales únicos.
- Cada departamento asociado a una provincia válida.
- Ausencia de filas exactamente duplicadas.

> **TODO:** registrar fecha o versión de GeoRef de forma automatizada cuando el recurso exponga ese metadato en la descarga utilizada.
