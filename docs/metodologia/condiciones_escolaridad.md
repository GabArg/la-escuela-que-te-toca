# Condiciones de escolaridad

## Alcance

Esta capa describe condiciones estructurales; no mide por sí sola acceso efectivo, permanencia ni calidad. Las asociaciones con RA 2025 son exploratorias y no prueban causalidad.

## Fuentes y años

- GeoRef Argentina: geometrías e identificadores territoriales oficiales.
- Censo Nacional 2022 (INDEC): población total y población por edad simple.
- Padrón Oficial de Establecimientos Educativos, actualización abril de 2022: localizaciones, sector, ámbito y oferta declarada.
- RA departamental 2025: sólo como resultado educativo para contrastes descriptivos. La diferencia temporal 2022–2025 impide leer el cruce como una fotografía sincrónica.

El archivo original del padrón se conserva sin cambios. SHA-256: `304EED05979FE068E5C0B1F4663E3CA163F78EBFE4D57B0BD18ABB05C7E01A4B`.

## Unidad, joins y cobertura

El grano final es una de las 529 unidades territoriales de GeoRef. El cruce usa nombres normalizados y sólo puentes históricos previamente confirmados; no se usa similitud difusa. Ocho variantes de nombres y una unidad sin registro quedan sin oferta asignada. Sus ausencias permanecen nulas.

## Identificadores educativos

La documentación oficial del RA confirma que el **CUE es la Clave Única de Establecimiento de siete dígitos**. El **CUE-anexo tiene nueve dígitos**: concatena el CUE y dos dígitos que identifican la localización; `00` corresponde a la sede y `01`, `02` y siguientes a anexos. Por ello, retirar los dos últimos dígitos del CUE-anexo recupera el CUE oficial y permite contar establecimientos sin construir un identificador nuevo.

La Secretaría de Educación distingue además la unidad educativa —oferta de nivel/modalidad en un establecimiento— de la unidad de servicio —oferta en una localización, sede o anexo—. En consecuencia, establecimientos y localizaciones son medidas válidas pero responden preguntas diferentes. `establecimiento_id` conserva el CUE de siete dígitos y `cueanexo`/`localizaciones_total` conserva la unidad publicada en el padrón.

La recomendación para la futura app es mostrar **localizaciones** como medida principal de despliegue territorial y acompañarla con establecimientos CUE cuando interese la organización institucional. Para accesibilidad, la localización es conceptualmente más cercana, aunque sin coordenadas todavía no mide distancia.

## Auditoría de nombres sin ID

La carga original dejó 587 filas (0,922% del padrón) sin match. Se encontraron equivalencias explícitas en una tabla oficial nacional para dos variantes de La Rioja: `GENERAL ANGEL V PEÑALOZA` → `Ángel Vicente Peñaloza` (29 filas) y `GENERAL JUAN F QUIROGA` → `General Juan Facundo Quiroga` (42). Se incorporaron como puentes auditables. Quedan 516 filas (0,811%) bajo seis denominaciones sin ID:

| Provincia | Denominación Padrón | Filas | % del padrón provincial | Inicial | Primaria | Secundaria | Sector | Ámbito | Estado |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| Buenos Aires | CORONEL DE MARINA L ROSALES | 93 | 0,476% | 26 | 35 | 26 | 83 estatal; 10 privada | 74 urbana; 19 rural | Pendiente |
| La Rioja | CORONEL FELIPE VARELA | 42 | 4,930% | 16 | 26 | 7 | 42 estatal | 23 urbana; 19 rural | Pendiente |
| La Rioja | GENERAL OCAMPO | 47 | 5,516% | 9 | 31 | 9 | 46 estatal; 1 privada | 10 urbana; 37 rural | Pendiente |
| San Luis | GENERAL JUAN MARTIN DE PUEYRREDON | 216 | 29,958% | 97 | 121 | 134 | 177 estatal; 39 privada | 171 urbana; 45 rural | Pendiente |
| Santiago del Estero | JUAN F IBARRA | 76 | 3,176% | 31 | 53 | 20 | 75 estatal; 1 privada | 13 urbana; 63 rural | Pendiente |
| Tucumán | JUAN B ALBERDI | 42 | 2,083% | 20 | 23 | 15 | 37 estatal; 5 privada | 22 urbana; 20 rural | Pendiente |

El archivo no incluye una variable de estado de actividad, por lo que no se afirma que estas filas sean localizaciones activas. Su peso es pequeño nacionalmente pero material dentro de San Luis y, en menor medida, La Rioja; excluirlas sesga los indicadores de esos departamentos. No se asignaron mediante similitud textual.

## Superficie y densidad

Las geometrías GeoRef se reproyectan desde su sistema de origen a EPSG:6933, una proyección equivalente global, antes de calcular área. No se calcula área en grados y no se simplifican geometrías.

`superficie_km2 = área proyectada / 1.000.000`.

`densidad_poblacional = población total Censo 2022 / superficie_km2`.

La superficie es adecuada para comparación exploratoria nacional, no para mensura legal.

## Oferta e indicadores derivados

Una oferta se cuenta cuando alguna columna del nivel contiene el valor `1`; los espacios en blanco no son presencia. Los conteos por nivel son establecimientos únicos con al menos una localización que declara esa oferta.

- establecimientos por 1.000 habitantes de 4–17;
- primarias por 1.000 habitantes de 4–11;
- secundarias por 1.000 habitantes de 12–17;
- establecimientos por 100 km²;
- relación entre establecimientos con secundaria y con primaria;
- proporción de establecimientos rurales.

Ningún cociente es una tasa oficial de cobertura. Más establecimientos no implica automáticamente más cupos, cercanía, calidad o mejor acceso.

## Sensibilidad: establecimiento frente a localización

En 520 unidades comparables, la mediana de la relación secundaria/primaria pasa de 0,500 por CUE a 0,555 por CUE-anexo; la diferencia relativa mediana es 2,7% y la correlación de rangos entre versiones es 0,861. Las localizaciones por población y por superficie son 14,0% mayores en la mediana, como corresponde al incluir anexos, pero conservan correlaciones de rangos de 0,967 y 0,993. La proporción rural cambia 1,1% en la mediana y su correlación de rangos es 0,991.

Los resultados generales son robustos en ordenamiento territorial, pero no intercambiables en magnitud. Las asociaciones de oferta total por población son las más sensibles; por ello no deben destacarse sin mostrar la unidad usada.

## Ausencia y sesgos

No se reemplazan nulos por cero. Un territorio sin match de padrón no se interpreta como territorio sin escuelas. El padrón no incluye coordenadas en la versión 2022 usada, por lo que no se estiman distancias, áreas de servicio ni tiempos de viaje. Los indicadores no consideran tamaño del establecimiento, vacantes, movilidad entre departamentos ni distribución interna de la población.

NBI, hacinamiento, internet, computadora y asistencia fueron auditados en las definiciones REDATAM del Censo 2022, pero no incorporados: falta una extracción departamental estática, reproducible y con universos/denominadores verificados. Conectividad ENACOM tampoco se incorporó por no haberse confirmado aquí un recurso departamental compatible y contemporáneo.
