---
name: d3-interactive-visualization
description: Implementa gráficos D3 integrados con React, escalas, ejes, brush, zoom, tooltips y vistas coordinadas.
---
# D3 Interactive Visualization

- Usa D3 para escalas, layouts, shapes, ejes y cálculos; deja que React controle el ciclo de vida del componente.
- Evita que React y D3 muten el mismo subárbol DOM.
- Define dimensiones responsivas y márgenes explícitos.
- Implementa tooltip accesible y estados hover/focus/selected.
- Brush/zoom debe actualizar el estado compartido, no crear filtros paralelos ocultos.
- Usa transiciones breves y respeta `prefers-reduced-motion`.
- Limpia listeners y timers al desmontar.
- Para datos grandes, agrega en servidor o usa Canvas/WebGL cuando la prueba de rendimiento lo justifique.
- Escribe pruebas para escalas, dominios, agregaciones y selección.
- Incluye unidad, fuente, leyenda y explicación de codificación.
