---
name: dashboard-performance
description: Optimiza dashboards interactivos con grandes datasets, consultas, agregación, caché y renderizado eficiente.
---
# Dashboard Performance

- Mide primero: tamaño, latencia, memoria, FPS y coste de renderizado.
- No descargues todo el dataset al navegador si el volumen no lo permite.
- Implementa filtros, agregaciones y paginación en backend.
- Usa índices/columnar query engine (DuckDB) cuando sea apropiado.
- Aplica caché a consultas repetidas con claves que incluyan filtros completos.
- Evita recalcular escalas y geometrías en cada render.
- Usa clustering/hexbin/LOD para mapas; Canvas/WebGL solo si hay evidencia de necesidad.
- Implementa cancelación/debounce para consultas de filtros.
- Establece presupuestos de rendimiento y prueba con volumen real.
- Nunca sacrifiques exactitud estadística por velocidad; documenta aproximaciones.
