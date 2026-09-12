# Metodología del módulo de acceso escolar

## Qué mide cada fuente

La familia **Población** del catálogo RA no representa habitantes del departamento. El catálogo la describe como composición de la matrícula y el diccionario confirma variables sobre población indígena, idiomas, país de origen, discapacidad, alimentación, jornada y otras características de estudiantes/localizaciones. No constituye un denominador demográfico y no se usa para estimar escolarización.

**Matrícula por edad RA** contiene matrícula observada por edad simple, grado, provincia, departamento, sector y ámbito. Está disponible para 2011–2025. Las edades 0–24 aparecen en 2011–2019; 0–29 en 2020–2024; en 2025 se mantienen 0–29 con un cambio en columnas resumen. Para el cruce 2022 se usan solo edades simples 4–17, presentes con la misma estructura.

El denominador seleccionado son los resultados definitivos del **Censo Nacional de Población, Hogares y Viviendas 2022 del INDEC**, cuadros jurisdiccionales `est_c4`: población por edad simple y departamento, partido o comuna. Según las notas de los cuadros, se excluye la población en situación de calle. El dato se asigna por residencia habitual.

## Año común

Se usa 2022: el RA tiene fecha de referencia 30 de abril y el operativo censal se desarrolló entre marzo y mayo de 2022. Es la coincidencia temporal más cercana y territorialmente detallada disponible. Aun así, las fechas y universos no son idénticos.

## Indicador

`indicador_acceso = matrícula RA 2022 por edad / población residente Censo 2022 por edad`.

Se denomina **cociente exploratorio matrícula/población residente**, no tasa de escolarización. Puede superar 1 porque el numerador se territorializa por localización educativa y el denominador por residencia; estudiantes pueden cruzar límites departamentales. Se calculan cuatro grupos: 4–5, 6–11, 12–14 y 15–17. Los grupos no equivalen automáticamente a niveles educativos.

## Diferencias conceptuales

- **Matrícula:** estudiantes registrados en ofertas educativas del RA.
- **Población:** personas residentes censadas de una edad determinada.
- **Cobertura del dato:** disponibilidad técnica de ambos componentes.
- **Escolarización:** condición de asistencia de las personas residentes; requiere una medición residencial, como la variable censal de asistencia.
- **Fuera del sistema:** condición individual que este cruce agregado no identifica.

## Territorio y ausencias

Se usa coincidencia normalizada exacta con GeoRef y el puente histórico auditado. No se usa matching difuso. Enmascarado y Sin datos nunca reciben ID. Las 22 unidades con solo población conservan matrícula nula, no cero. Dos unidades GeoRef no aparecen identificadas en la salida combinada. Las correspondencias dudosas no se fuerzan.

## Causas alternativas de cocientes bajos o altos

- movilidad cotidiana entre departamentos;
- escuelas que reciben población de zonas vecinas;
- internados u ofertas concentradas regionalmente;
- residencia censal distinta de la localización escolar;
- diferencias de fecha de referencia;
- repetición, sobreedad y estudiantes fuera del rango teórico;
- migración durante el período;
- educación domiciliaria, hospitalaria u otras modalidades;
- cobertura territorial incompleta y enmascaramiento;
- errores o cambios administrativos de registro.

Por estas razones, `1 - indicador_acceso` tampoco representa “chicos fuera de la escuela”.

## Datos necesarios para una versión institucional

La medición preferible es la condición censal de asistencia por edad y residencia, complementada con proyecciones intercensales por edad y departamento, registros nominales protegidos con gobernanza adecuada, residencia del estudiante, movilidad escolar y series homogéneas. Ningún dato individual debe exponerse.
