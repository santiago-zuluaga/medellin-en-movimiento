---
name: visualization-testing
description: Prueba exactitud de datos, agregaciones, filtros coordinados, accesibilidad, responsividad y rendimiento.
---
# Visualization Testing

Cubre cuatro niveles:
1. Unitarias: parsing, fechas, escalas, agregaciones, denominadores y métricas.
2. Integración: API, filtros, selección compartida y sincronización entre vistas.
3. E2E: Story/Explore, filtros, reset, zoom, selección, tooltips y estados vacíos.
4. Visual/performance: responsive, contraste, layout, latencia y volumen.

- Usa fixtures pequeñas con resultados esperados calculados manualmente.
- Verifica que filtrar comuna/periodo produce los mismos totales en todas las vistas.
- Comprueba que incidente y víctima no se mezclan.
- Comprueba fechas límite, zona horaria, datos faltantes y categorías desconocidas.
- No uses snapshots como única prueba de exactitud.
- Añade pruebas de accesibilidad y teclado.
- Documenta cualquier aproximación de clustering o muestreo.
- Bloquea release si una métrica visible no puede reproducirse.
