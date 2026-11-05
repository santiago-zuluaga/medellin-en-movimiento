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

## Fichas implementadas

### Mapa municipal agregado
- **Pregunta/tarea:** ¿dónde se agrupan los registros seleccionados? Localizar y filtrar.
- **Unidad:** fila de la capa de siniestralidad o fila de la capa de mortalidad, nunca combinadas.
- **Marcas/canales:** círculo por grupo de coordenadas redondeado a 0,01°; posición = longitud/latitud en EPSG:4326; área = conteo; color uniforme redundante como capa temática. Límite municipal oficial como región de contexto.
- **Escala/agregación:** círculo con radio proporcional a raíz cuadrada del conteo (área proporcional); grupos con menos de cinco filas omitidos. No es una malla de área igual ni un hexbin; longitud y latitud no representan la misma distancia.
- **Interacción:** seleccionar celda filtra las otras vistas; el estado aparece arriba y Restablecer lo limpia.
- **Gestalt/accesibilidad:** región común del límite, figura-fondo neutro, foco visible, etiqueta accesible, activación por Enter/Espacio; el círculo no depende solo del color.
- **Límite:** concentración de registros no equivale a riesgo; no se dibujan puntos exactos, direcciones o identificadores. Outliers no se eliminan.
- **Alternativa descartada:** puntos individuales y coropleta de conteos sin exposición.

### Serie temporal mensual
- **Pregunta/tarea:** ¿cómo varía el conteo mensual de filas? Tendencia descriptiva.
- **Marcas/canales:** segmentos y puntos; eje horizontal = mes ordenado; vertical = conteo.
- **Agregación:** número de filas de la fuente; meses sin filas de los filtros aparecen como cero solo dentro de meses con cobertura observada. Huecos de cobertura cortan la línea.
- **Interacción:** punto filtra año en el resto de vistas.
- **Límite:** no normaliza por exposición, ni iguala completitud/revisión de captura entre años.

### Barras de comuna y categorías
- **Pregunta/tarea:** comparar magnitudes entre categorías geográficas/nominales.
- **Marcas/canales:** barras horizontales, longitud = número de filas; etiquetas textuales conservan identidad si se imprime en blanco y negro.
- **Interacción:** seleccionar barra aplica filtro coordinado.
- **Límite:** conteos brutos describen registros, no riesgo o desempeño relativo.
- **Alternativa descartada:** mapa de área coloreado por conteo como comparación principal.

### Heatmap de día × hora
- **Pregunta/tarea:** reconocer ciclos por día de semana y hora; seleccionar un intervalo.
- **Marcas/canales:** rectángulos; X = hora 0–23, Y = lunes–domingo, intensidad de color = filas. Una barra vertical contigua muestra el mínimo y el máximo de los 168 valores de la selección actual; su gradiente usa los mismos extremos de intensidad que las celdas. Etiquetas, tooltip y nombre accesible repiten el conteo.
- **Interacción:** seleccionar una celda filtra por día y hora a todas las vistas.
- **Límite:** una celda vacía expresa cero filas en la selección; no demuestra ausencia de siniestros reales.
