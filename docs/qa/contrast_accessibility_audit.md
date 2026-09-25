# Auditoría de contraste y foco

Fecha: 2026-09-24.

## Contraste medido

Los cocientes se calcularon con la fórmula de luminancia relativa de WCAG 2.x.

| Uso | Primer plano | Fondo | Contraste | Resultado |
|---|---:|---:|---:|---|
| Dorado original como texto claro | `#d8a94a` | `#f7f5ee` | 1,99:1 | No cumple para texto |
| Nuevo dorado de texto | `#7a5512` | `#f7f5ee` | 6,14:1 | Cumple AA para texto normal |
| Texto claro sobre verde oscuro | `#f7f5ee` | `#173f35` | 12,08:1 | Cumple AA y AAA |
| Verde oscuro sobre celeste | `#173f35` | `#a7c8d8` | 5,46:1 | Cumple AA para texto normal |
| Texto secundario sobre papel | `#69665d` | `#f7f5ee` | 5,10:1 | Cumple AA para texto normal |

El dorado original se conserva en elementos decorativos y en usos sobre fondos oscuros donde no produce el problema medido. Para texto sobre superficies claras se incorporó `--accent-text`.

## Foco visible

Se agregó un indicador global de `:focus-visible` para enlaces, botones y controles con rol de botón. Los controles de selección y radio conservan además sus reglas específicas. La regla combina contorno y separación respecto del componente para no depender solamente de un cambio de color.

## Alcance pendiente

La revisión estática confirma la cascada y los cocientes de contraste. Queda pendiente una recorrida manual completa con teclado y tecnologías de asistencia en el entorno exacto de despliegue, porque una captura sin sesión interactiva no valida orden de tabulación, anuncios del lector de pantalla ni tooltips activados por teclado.
