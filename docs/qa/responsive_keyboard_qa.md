# QA responsive, teclado y navegación

Fecha: 2026-09-24.

## Verificaciones reproducibles realizadas

- Revisión estática de reglas responsive, ausencia de anchos mínimos globales y tratamiento de mapas, tarjetas, tablas y navegación.
- Compilación de `app`, `src`, `scripts` y `tests` con `python -m compileall`.
- Ejecución funcional de vistas mediante la suite de pruebas de Streamlit.
- Revisión de que enlaces, botones y controles con rol de botón tengan foco visible.
- Revisión de que la navegación incluya vuelta a Inicio y accesos explícitos al caso guiado.

## Intento de prueba visual

Se intentaron capturas headless en 1366×768, 1920×1080, 390×844 y 412×915 contra una instancia local de Streamlit. El navegador sólo capturó el esqueleto inicial de Streamlit: la sesión WebSocket no llegó a un estado estable en ese entorno headless. Esas imágenes no se consideran evidencia visual válida y no se incluyen como resultado.

## Pendiente manual antes de presentar

Debe realizarse una prueba visual real en los cuatro tamaños solicitados, en el mismo navegador o plataforma que verá el jurado, verificando:

- overflow horizontal y legibilidad del CTA;
- navegación, sidebar y regreso a Inicio;
- mapas, tooltips y tablas;
- tarjetas y gráficos;
- orden completo de tabulación;
- activación por teclado de enlaces, selects, radios y botones;
- persistencia y contraste del foco visible;
- menú y elementos propios de la plataforma Streamlit.

La auditoría no declara esta fase visual como cerrada: las pruebas automáticas reducen el riesgo funcional, pero no sustituyen la inspección manual de renderizado y teclado.
