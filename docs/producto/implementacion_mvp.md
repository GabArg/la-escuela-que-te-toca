# Implementación del MVP Streamlit

## Arquitectura

`app/app.py` configura navegación y estado. Los componentes contienen presentación y funciones puras testeables:

- `data.py`: carga cacheada y reconstrucción delegada.
- `territorio.py`: selector provincia → territorio.
- `perfil.py`: perfil, señales, dimensiones y Aprender.
- `historia.py`: serie RA 2011–2025.
- `comparables.py`: vecinos estructurales y contraste A/B.
- `senales.py`: explorador no ordinal.
- `metodologia.py`: guía pública de interpretación.

La app no recalcula indicadores. Si falta un output, invoca `write_profiles`, `write_engine` o `write_long` del módulo analítico correspondiente. Los errores de disponibilidad se convierten en mensajes legibles.

## Estado y navegación

`st.session_state.territory_id` conserva el territorio entre Inicio, Perfil, Historia, Comparables, Dónde mirar y Metodología. El selector muestra nombres y nunca claves técnicas. Desde Dónde mirar se puede abrir un perfil conservando provincia y territorio.

## Decisiones de presentación

- Sin mapa en esta iteración: se prioriza selector accesible y narrativa estable.
- Máximo tres señales y cuatro indicadores por bloque.
- Ausencia como `Sin dato`; cero sigue siendo cero.
- Aprender parcial bloquea toda distribución.
- Historia muestra un indicador por vez y marca 2020–2022.
- Los pares muestran calidad en lenguaje y distancia solo como detalle.
- El contraste usa brechas procesadas; no decide ganador.
- Paleta sobria sin rojo/verde normativo.

## Ejecución

Desde la raíz:

```bash
python -m pip install -r requirements.txt
streamlit run app/app.py
```

Los parquets procesados están ignorados por Git. Deben generarse previamente con los pipelines documentados o estar disponibles localmente para que la reconstrucción delegada tenga sus insumos.

## Validación

Las funciones puras cubren formato, nulos, señales, selector, historia, pares, contraste y bloqueo Aprender. Los casos de aceptación son Pocito, Ramón Lista, Trenel, Comuna 1, Vicente López y Coronel de Marina Leonardo Rosales.

## Pendientes

- Pruebas de usabilidad con personas reales.
- Mapa localizador y selección espacial accesible.
- Diseño visual e identidad definitivos.
- URLs compartibles.
- Auditoría responsive, teclado y lectores de pantalla.
- Descargas públicas versionadas.
