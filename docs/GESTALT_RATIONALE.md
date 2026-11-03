# Matriz de principios Gestalt

| Principio | Implementación | Evidencia en interfaz | Riesgo a evitar |
|---|---|---|---|
| Proximidad | Agrupar filtros relacionados y sus etiquetas | Paneles de controles con espaciado consistente | Agrupar controles de tareas distintas |
| Similitud | Color/forma consistentes por categoría entre vistas | La misma categoría mantiene codificación en mapa y gráficos | Usar el mismo color para significados distintos |
| Región común | Paneles con contenedor y título por tarea | Mapa, tiempo y composición separados | Exceso de cajas que fragmente el layout |
| Conexión | Líneas de referencia/resaltado y selección coordinada | Seleccionar comuna resalta la misma comuna en otras vistas | Confundir asociación visual con relación causal |
| Continuidad | Ejes y líneas temporales alineadas | Lectura de tendencias y continuidad entre periodos | Unir periodos con datos faltantes como si fueran continuos |
| Figura-fondo | Fondo cartográfico de bajo contraste; datos destacados | Capas temáticas legibles sobre mapa neutro | Contraste insuficiente o exceso de saturación |
| Cierre | Simplificación de contornos y límites | Regiones reconocibles sin detalle superfluo | Ocultar fronteras o límites necesarios |

Cada principio debe tener captura y una breve explicación de qué problema de percepción resuelve. Los principios no se añaden como adornos: se aplican solo cuando ayudan a la tarea.

## Evidencia en la implementación

- **Proximidad:** cada leyenda, unidad y nota está dentro del panel del gráfico. Los filtros globales se mantienen encima de las vistas coordinadas.
- **Similitud:** una sola paleta categórica semántica distingue el total temático; comparaciones cuantitativas usan longitud/posición y etiquetas.
- **Región común:** Story, Explore y metodología tienen secciones diferenciadas; los gráficos viven en paneles con pregunta y fuente/unidad.
- **Conexión:** elegir comuna, clase, gravedad, año, celda o combinación día-hora recalcula mapa, barras, serie y heatmap desde los mismos filtros compartidos.
- **Continuidad:** la serie ordena meses y corta el trazo ante una brecha del periodo observado; no dibuja puntos exactos cuando cambia cobertura.
- **Figura-fondo:** mapa de fondo neutro con límite oficial discreto; agrupaciones temáticas en acento terracota.
- **Cierre:** límite administrativo permite reconocer el municipio sin etiquetas de calles o predios que compitan con los datos.

Capturas de la aplicación se guardarán bajo `reports/screenshots/` solo si se obtiene una captura real del navegador en esta ejecución; no se generan mockups para simular evidencia.
