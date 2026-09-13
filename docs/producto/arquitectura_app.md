# Arquitectura narrativa de la aplicación

## Estructura general

| Etapa | Pregunta | Objetivo | Información | Interacción | Visualización candidata | Advertencia | Siguiente acción |
|---|---|---|---|---|---|---|---|
| Inicio | ¿Qué territorio quiero conocer? | Orientar sin exigir conocimiento técnico | Buscador, selección y explicación breve | Buscar o elegir en mapa/lista | Mapa localizador neutro | Disponibilidad desigual | Abrir perfil |
| Perfil | ¿Qué pasa acá? | Dar una lectura inicial multidimensional | Cobertura, hasta 3 señales, cinco dimensiones | Abrir señal o dimensión | Fila de tarjetas textuales + dot plots independientes | No existe nota general | Ver historia o evidencia |
| Historia | ¿Esto viene de antes? | Separar nivel actual, tendencia y anomalía | Serie 2011–2025 de un indicador | Cambiar indicador; inspeccionar año | Línea con huecos y banda de referencia | Ruptura 2020–2022; cocientes internos | Contextualizar señal |
| Contexto | ¿En qué condiciones ocurre? | Describir estructura sin explicar causalmente | Población, densidad, ruralidad, hogar y oferta | Alternar territorio/contexto/oferta | Dot plots contra distribución | Asociación no es causa | Buscar pares |
| Comparables | ¿Con quién tiene sentido compararlo? | Ofrecer referencias más justas | Top 5, distancia, calidad, estabilidad, similitudes | Nacional/provincial; seleccionar par | Lista explicada, no leaderboard | Similaridad estructural, no educativa | Abrir contraste |
| Contrastes | ¿Qué cambia entre territorios parecidos? | Separar condiciones y resultados | A/B estructural y brechas educativas | Cambiar par/resultado | Barras o dots A/B, dos bloques | No hay ganador; años diferentes | Formular investigación |
| Señales | ¿Qué merece mirar? | Explorar reglas auditables sin ranking | Señales, evidencia, año, fuente, limitación | Filtrar por dimensión/cobertura; abrir caso | Lista o matriz pequeña | No mide urgencia | Abrir territorio/fuente |
| Metodología | ¿Qué tan sólido es este dato? | Hacer auditable la experiencia | Definición, universo, cálculo, cobertura, comparabilidad | Buscar variable/fuente | Tabla y ficha textual | Alcance específico | Volver conservando estado |

## Navegación

Navegación principal corta: `Inicio · Perfil · Comparables · Dónde mirar · Metodología`. Historia, Contexto y Contraste son profundizaciones dentro del territorio, no destinos aislados. El selector territorial permanece visible pero no domina la pantalla.

## Ficha territorial

La cabecera responde dónde estoy, años principales y completitud documental. Luego aparecen hasta tres señales con verbo neutral: “merece revisar”, “dato parcial”, “diferencia relativa”. Debajo, cinco módulos independientes:

- Acceso/asistencia.
- Trayectoria.
- Oferta.
- Contexto.
- Aprendizaje.

No se usa radar: su geometría sugiere una escala común y un área total. Cada dimensión usa su propia unidad y referencia mediante dot plot o texto comparativo.

## Wireframes textuales

### 1. Inicio

```text
[HEADER] La escuela que te toca                         [Metodología]

[TÍTULO] Entender un territorio antes de compararlo
[SUBTÍTULO] Perfil, historia, contexto y pares comparables con datos abiertos.

[BUSCADOR: provincia, departamento o equivalente]
[SELECTOR PROVINCIA] [SELECTOR TERRITORIO] [Ver perfil]

[MAPA LOCALIZADOR DE ARGENTINA]        [¿QUÉ HACE ESTA HERRAMIENTA?]
                                       Detecta → entiende → compara → investiga

[NOTA] Sin score ni ranking. La cobertura varía según fuente.
```

En diez segundos debe entenderse: se elige un territorio, se obtiene una historia contextual y no es un ranking de escuelas.

### 2. Perfil territorial

```text
[MIGA] Argentina / Provincia / Territorio
[NOMBRE] [tipo de unidad]                    [Cobertura documental: alta/media/baja]
[AÑOS] Censo/Padrón 2022 · Aprender 2024 · RA 2025

[QUÉ MERECE MIRAR — máximo 3]
[Señal 1 + evidencia] [Señal 2 + evidencia] [Señal 3 + evidencia]

[ACCESO] [TRAYECTORIA] [OFERTA] [CONTEXTO] [APRENDIZAJE]
valor + referencia + año + estado; sin nota agregada

[Ver historia] [Buscar pares] [Ver datos faltantes]
```

### 3. Evolución histórica

```text
[TERRITORIO] Historia de [selector: sobreedad / repetición / salidos sin pase]
[CLASIFICACIÓN AUDITADA] [años observados] [valor 2025] [mediana histórica]

[LÍNEA 2011–2025 CON HUECOS]
              [marca visual de período 2020–2022]

[LECTURA PERMITIDA] evolución descriptiva
[LÍMITE] cambios administrativos/metodológicos posibles
[Contextualizar] [Comparar este indicador]
```

### 4. Comparación con pares

```text
[TERRITORIO A]     [Nacionales | Dentro de provincia]

[PAR 1] distancia · calidad · estabilidad
  Similares en: ...
  Difieren más en: ...                         [Comparar A/B]
[PAR 2] ...
[PAR 3] ...
[PAR 4] ...
[PAR 5] ...

[DEFINICIÓN] Similar = estructura/contexto/oferta; no resultados educativos.

[CONTRASTE A / B]
CONDICIONES: dots A/B y diferencias normalizadas
──────────── separación explícita ────────────
RESULTADOS: asistencia · trayectoria · aprendizaje disponible
[Sin ganador] [Ver fuentes y años]
```

### 5. Dónde mirar

```text
[TÍTULO] Señales para investigar, no ranking de alertas
[DIMENSIÓN] [COBERTURA] [PROVINCIA opcional]

[SEÑAL]
Territorio · evidencia · umbral · confianza
[Abrir evidencia] [Ver perfil] [Fuente/año]

[DATO PARCIAL / AUSENTE explicado]
```

El orden por defecto es narrativo o alfabético, nunca por “gravedad total”.

### 6. Metodología

```text
[BUSCAR VARIABLE O FUENTE]
[TEMAS] Definiciones · Comparabilidad · Cobertura · Pares · IA

[FICHA]
Nombre / definición / universo / año / fuente
Cálculo / cobertura / comparabilidad / limitación
[Abrir fuente oficial] [Descargar diccionario]

[GLOSARIO]
Sin dato ≠ 0 · Parcial ≠ ausente · Asociación ≠ causa
```

## Estados imprescindibles

- Cargando: esqueleto con territorio visible.
- Sin dato: explicación y fuente esperada; nunca cero.
- Parcial: dato bloqueado o mostrado solo si la metodología lo permite.
- Sin pares: motivos de elegibilidad y retorno al perfil.
- Error de fuente: mensaje operativo separado de ausencia estadística.
