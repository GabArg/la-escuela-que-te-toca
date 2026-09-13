# Checklist de deployment

## Aplicación

- [x] Entrypoint: app/app.py.
- [x] Ejecución: streamlit run app/app.py.
- [x] Rutas construidas con pathlib desde la raíz; no se detectaron rutas absolutas.
- [x] Sin secrets requeridos por la aplicación actual.
- [ ] Definir URL pública y health check manual.

## Dependencias

- [x] requirements.txt no contiene rutas locales.
- [x] Incluye Streamlit, Plotly, pandas y pyarrow.
- [ ] Probar instalación limpia en Linux.
- [ ] Congelar versiones tras validar el entorno objetivo; hoy están sin pin.

## Datos

- [ ] Publicar bundle procesado versionado.
- [ ] Verificar hashes al construir.
- [ ] Confirmar que los seis artefactos esenciales y el GeoJSON estén presentes.
- [ ] Medir tamaño de descarga y memoria en hosting.
- [ ] Probar un arranque sin caché y otro con caché.

## Operación

- [ ] Abrir enlace en sesión anónima.
- [ ] Probar mapa, cambio de territorio, Historia y Comparables.
- [ ] Comprobar tiempo de arranque y reinicio.
- [ ] Registrar versión de datos visible.
- [ ] Revisar logs sin exponer rutas o datos sensibles.

Streamlit Community Cloud es viable si el bundle cabe en sus límites efectivos y puede obtenerse durante build. Si no, conviene un contenedor con almacenamiento de objetos o artefactos incluidos.
