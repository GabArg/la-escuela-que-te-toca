# Auditoría visual del MVP

Fecha: 2026-09-13.

El MVP resolvía navegación, selección territorial y estados incompletos, pero su presentación se acercaba a un tablero tradicional. La portada no ofrecía una entrada territorial visual; el perfil repartía indicadores en muchas tarjetas equivalentes; la tabla de señales interrumpía la narrativa; y detalles técnicos aparecían antes de que el usuario entendiera la pregunta.

Problemas observados:

- jerarquía débil entre territorio, señales, dimensiones y metadatos;
- cuatro columnas repetidas poco legibles en anchos intermedios;
- CSS inline dependiente de un selector interno de Streamlit;
- números con protagonismo similar aunque cumplan funciones distintas;
- “Dónde mirar” como tabla administrativa;
- distancia numérica demasiado visible en Comparables;
- lenguaje inconsistente para completo, parcial y sin dato.

Se prioriza el territorio como puerta de entrada, lectura vertical y bloques editoriales. Las señales anteceden a los indicadores y los detalles técnicos quedan bajo demanda. No se modificaron indicadores, reglas, fuentes, joins ni criterios metodológicos.
