# Streamlit Community Cloud

Configuración validada el 2026-09-13 contra la documentación oficial.

## Publicación

1. Subir el repositorio a GitHub y confirmar que master contiene código, data/public, requirements.txt y .streamlit/config.toml.
2. Entrar a https://share.streamlit.io y conectar la cuenta GitHub con permisos sobre el repositorio.
3. Elegir **Create app** y seleccionar el repositorio.
4. Elegir rama **master**.
5. Indicar **app/app.py** como archivo principal.
6. Abrir **Advanced settings** y elegir Python **3.12**.
7. No cargar secrets: la aplicación no los usa.
8. No hace falta definir APP_ALLOW_PIPELINE_REBUILD: su valor seguro por defecto es 0. Si la plataforma permite variables ordinarias, puede fijarse explícitamente en 0 como defensa adicional; no debe cargarse como secreto sensible.
9. Iniciar Deploy y observar instalación y arranque en los logs.
10. Cuando abra, validar Inicio, mapa, Perfil, Historia, Comparables, Dónde mirar y Metodología.

## Validación posterior

- abrir la URL en una ventana incógnita;
- comprobar Ramón Lista, Quebrachos, Trenel, Comuna 1 y Coronel Rosales;
- verificar selección por mapa y selector;
- confirmar cobertura parcial/ausente;
- revisar logs por excepciones;
- probar móvil real;
- registrar URL final sin inventarla previamente.

Community Cloud ejecuta desde la raíz del repositorio. La configuración debe permanecer en .streamlit/config.toml y el requirements puede estar en la raíz. Cambiar Python después de desplegar exige recrear la aplicación, por lo que se selecciona 3.12 desde el inicio.
