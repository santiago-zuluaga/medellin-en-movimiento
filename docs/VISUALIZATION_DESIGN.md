# Diseño preliminar de visualizaciones

## Principio de diseño
Cada vista debe responder una pregunta concreta. La forma visual no se elige por decoración sino por el tipo de dato, la tarea y la precisión perceptual necesaria.

## Matriz de abstracción
| Atributo | Tipo | Tarea | Canal/representación candidata |
|---|---|---|---|
| Fecha/hora | Temporal ordenado | Tendencia/ciclo | Posición en eje temporal |
| Comuna/barrio | Categórico/espacial | Comparar/ubicar | Posición geográfica y barras ordenadas |
| Clase de incidente | Categórico | Comparar composición | Color categórico o posición en barras |
| Gravedad | Categórico ordenado, si la definición lo respalda | Comparar severidad | Posición en barras; color redundante |
| Conteo de registros | Cuantitativo | Comparar magnitudes | Longitud/posición |
| Coordenadas | Espacial | Ubicar | Posición en mapa |

## Vistas
### A. Mapa editorial
- Escala ciudad: hexbin o clusters.
- Escala barrio: clusters pequeños.
- Escala calle: puntos individuales solo cuando la densidad lo permita.
- Tooltip con fecha, clase, gravedad y geografía; evitar información personal.
- Leyenda visible y explicación de qué representa el tamaño/color.
- Selección de comuna filtra vistas B y C.

### B. Ritmos de la ciudad
- Heatmap: eje X = hora; eje Y = día de semana; color = número o tasa correctamente definida.
- Serie temporal mensual para tendencia.
- Si se comparan años incompletos, mostrar cobertura y evitar comparar periodos desiguales sin normalización.

### C. Composición de incidentes
- Barras horizontales ordenadas por clase o gravedad.
- Barras apiladas solo cuando la comparación de composición sea relevante.
- Evitar pastel/donut con muchas categorías.

### D. Víctimas
- Barras por condición de actor vial, edad agrupada o gravedad.
- Denominador y unidad explícitos: número de víctimas, no número de incidentes.
- Suprimir o agrupar celdas pequeñas cuando exista riesgo de identificación.

## Coordinación
- Filtros globales: rango temporal, comuna, clase y gravedad (solo si el campo existe).
- Selección en mapa resalta subconjunto en gráficos.
- Selección de categoría en gráfico resalta mapa.
- Estado de filtros visible, botón de limpiar y opción de comparar.
- No mantener filtros incompatibles ocultos.

## Complejidad
- Reduce: agregación y filtros.
- Select: selección y resaltado.
- Change: rango temporal, geografía, categoría.
- Zoom semántico: celdas → clusters → puntos.
- Consultas del servidor para grandes volúmenes; no descargar/renderizar todo el dataset en el navegador.

## Documentación por gráfico
Registrar: pregunta, unidad de análisis, atributos, marca, canales, escalas, transformaciones, agregación, interacción, Gestalt, accesibilidad y limitaciones.
