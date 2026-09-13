# Accesibilidad básica

Fecha de revisión: 2026-09-13. Esta lista no constituye una declaración de conformidad WCAG.

| Criterio | Estado | Evidencia o pendiente |
|---|---|---|
| Contraste de texto | Revisado | Tinta oscura sobre papel/superficie clara; ocre no se usa solo como texto. |
| Tamaño mínimo | Revisado | Cuerpo desde 1 rem; metadatos desde 0,72 rem. |
| Labels de controles | Cumple | Provincia, unidad territorial, recorrido, indicador y filtros tienen etiqueta. |
| Alternativa al mapa | Cumple | Selector Provincia → Departamento siempre disponible. |
| Significado no solo por color | Cumple | Leyenda textual y estados “Dato disponible”, “Cobertura parcial” y “Sin dato”. |
| Orden de lectura | Revisado | Territorio → señal → dimensión → metodología; comparación estructura → resultados. |
| Gráficos | Parcial | Títulos de ejes y leyendas presentes; falta auditoría con lector de pantalla. |
| Teclado | Pendiente | Requiere prueba manual formal sobre mapa Plotly y popovers. |
| Texto alternativo | Parcial | El mapa tiene tooltip y selector alternativo; falta descripción accesible equivalente completa. |
| Móvil | Revisado | Grillas adaptables; mapa reducido a 540 px. Requiere prueba en dispositivos reales. |

No se detectaron controles cuyo significado dependa exclusivamente de iconos. Se recomienda una auditoría posterior con NVDA/VoiceOver, teclado y contraste automatizado.
