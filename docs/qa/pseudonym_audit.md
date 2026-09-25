# Auditoría de seudónimo y superficie pública

Fecha: 2026-09-24.

## Resultado

La interfaz controlada por el proyecto no muestra nombres personales, correos, créditos individuales, usuarios de redes ni enlaces al repositorio o a perfiles de autor. El título, sidebar, storytelling, metodología, metadatos de página y bundle público usan únicamente el nombre del proyecto y fuentes institucionales.

El repositorio Git conserva legalmente su historial y autoría. El remoto local apunta a `github.com/GabArg/la-escuela-que-te-toca` y el commit base contiene nombre/correo de autor. No se modificaron `.git`, `LICENSE`, commits, remotos ni documentación histórica para ocultar esos datos.

## Superficie revisada

| Superficie | Hallazgo | Acción |
|---|---|---|
| Portada y storytelling | Sin identidad personal ni vínculo al autor | Sin cambio |
| Sidebar y navegación | Solo marca del proyecto y descripción metodológica | Sin cambio |
| Footer | No existe footer con créditos personales | Sin cambio |
| Metadatos Streamlit | `page_title` y `page_icon` no identifican autor | Sin cambio |
| Links salientes de la app | La versión auditada no contiene links personales ni a GitHub | Sin cambio |
| Sección Metodología | No contiene autoría personal | Sin cambio |
| Bundle `data/public` | Manifiesto técnico sin nombre/correo/usuario | Sin cambio |
| Configuración Streamlit | El toolbar estaba en modo automático | Se fijó `client.toolbarMode = "minimal"` para reducir controles de plataforma no necesarios |
| README y documentación local | No enlazan al perfil del autor desde la app | Sin cambio |
| Git/GitHub | Remoto y commits conservan autoría real | No modificar |

## Límite de control

La configuración `toolbarMode = "minimal"` reduce opciones visibles del toolbar de Streamlit, pero no garantiza anonimato de la infraestructura. Streamlit Community Cloud puede exponer datos fuera del HTML de la app, por ejemplo:

- dominio o URL de despliegue asociado a una cuenta;
- identidad del workspace o propietario en pantallas de compartir/administración;
- vínculo al repositorio configurado por la plataforma;
- información accesible si el jurado recibe además la URL pública de GitHub.

Esos elementos dependen de la cuenta, visibilidad y configuración del despliegue, no del código auditado. Deben verificarse manualmente en una sesión anónima con la URL final del concurso.

## Decisión

La superficie controlada por la app es compatible con un seudónimo y no revela innecesariamente identidad. El requisito completo **requiere revisión manual del deployment final**; no se declara resuelto mientras la URL y los controles reales de la plataforma no se prueben desde un navegador sin sesión.
