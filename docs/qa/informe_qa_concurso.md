# Informe QA para concurso

## Cobertura funcional

Las seis vistas renderizaron sin excepciones mediante Streamlit AppTest: Inicio, Perfil territorial, Historia, Comparables/contraste, Dónde mirar y Metodología. El arranque local de Streamlit fue correcto.

Tiempos orientativos en el entorno local: primer render de Inicio 2,64 s; Perfil 0,10 s; Historia 1,12 s; Comparables 0,13 s. Son mediciones simples, no un benchmark de producción.

Se comprobaron los casos Pocito, Ramón Lista, Trenel, Comuna 1, Vicente López y Coronel de Marina Leonardo Rosales, además de bordes de cobertura: Comuna 1 sin señales prioritarias; Coronel Rosales con cobertura baja, sin pares y sin trayectoria completa; Aprender completo, parcial y ausente.

## Integridad

- 529 perfiles y claves territoriales únicas.
- 751 señales para 462 territorios.
- 4.975 relaciones de pares: 2.520 nacionales y 2.455 provinciales.
- 504 territorios con al menos un par y 25 sin vecinos elegibles.
- Cobertura de perfil: 478 alta, 43 media, 8 baja.
- Aprender Lengua: 480 completo, 19 parcial, 30 ausente.
- Aprender Matemática: 145 completo, 354 parcial, 30 ausente.
- Serie RA: 2011–2025, 510 territorios identificables.

No aparecen literales NaN, None, <NA>, inf o -inf en campos de texto, ni infinitos numéricos en el perfil. La UI consume artefactos procesados y no recalcula indicadores.

## Correcciones

- Se redujo la altura del mapa de 650 a 540 px para evitar dominancia y overflow vertical.
- La portada explicita que 2022, 2024 y 2025 no forman una fotografía simultánea.
- Se completó la fecha y alcance del registro de IA.

## Advertencias

Los avisos visibles en Pocito corresponden a cobertura parcial de Aprender y son intencionales. Los mensajes de deprecación de Plotly observados en consola no se muestran al usuario. Falta una prueba manual formal con navegador real para click geográfico, teclado y dispositivos físicos.
