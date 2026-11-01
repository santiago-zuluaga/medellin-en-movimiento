# Medellín en movimiento
## Propuesta académica — Information Visualization & Data Storytelling

### 1. Título
**Medellín en movimiento: exploración visual de la siniestralidad vial y los patrones de movilidad urbana.**

### 2. Resumen
El proyecto propone una aplicación web interactiva para explorar la distribución espacial y temporal de los incidentes viales registrados en Medellín, así como sus características y consecuencias. El sistema combinará un modo narrativo (*Story*) y un modo exploratorio (*Explore*). Las visualizaciones permitirán examinar patrones por periodo, comuna, barrio, clase y gravedad, siempre que los atributos estén presentes y validados en las fuentes seleccionadas.

El proyecto no pretende inferir causalidad ni evaluar el riesgo individual de circular por una zona. Sus resultados describirán los registros disponibles y sus limitaciones.

### 3. WHAT — ¿Qué se representa?
El fenómeno central es la siniestralidad vial registrada en Medellín. Se estudiarán:
- distribución geográfica de incidentes;
- evolución temporal por año, mes, día y hora;
- composición por clase y gravedad;
- características de las víctimas, únicamente cuando la fuente y el nivel de agregación lo permitan;
- contexto complementario de movilidad (aforos de bicicleta, velocidad e intensidad) si se valida la compatibilidad metodológica.

Unidades de análisis que deben mantenerse separadas:
- incidente vial;
- víctima asociada a un incidente;
- registro de mortalidad;
- ciclista observado en un aforo;
- medición de velocidad/intensidad.

### 4. WHY — ¿Por qué y para quién?
**Público objetivo:** estudiantes, ciudadanía interesada en movilidad urbana, periodistas de datos y personas que trabajan con planificación o seguridad vial. La interfaz debe ser accesible a no especialistas sin ocultar definiciones ni limitaciones.

**Preguntas analíticas iniciales:**
1. ¿Cómo se distribuyen espacialmente los incidentes registrados?
2. ¿Cómo varían los registros por hora y día de la semana?
3. ¿Cómo ha cambiado el número de registros a lo largo del tiempo?
4. ¿Qué clases y niveles de gravedad aparecen en los datos?
5. ¿Qué diferencias descriptivas se observan entre comunas y barrios?
6. ¿Qué características de las víctimas pueden describirse con la fuente de víctimas?
7. ¿Qué información contextual de movilidad puede compararse de forma metodológicamente válida?

Las preguntas se revisarán después del EDA. Solo se conservarán aquellas que los datos permitan responder.

### 5. HOW — ¿Cómo se representa?
| Tarea | Representación candidata | Justificación y cautela |
|---|---|---|
| Localizar concentraciones | Mapa de puntos con clustering y/o hexbin | Evita sobretrazado; explicar que la densidad de registros no equivale por sí sola a riesgo |
| Comparar hora y día | Heatmap hora × día | Hace visibles patrones cíclicos; normalizar si se comparan periodos de distinta duración |
| Observar evolución | Serie temporal de líneas | Adecuada para variable temporal ordenada; mostrar cobertura y posibles cambios de registro |
| Comparar clases/gravedad | Barras agrupadas o apiladas | Comparación de categorías; usar proporciones cuando los tamaños de grupo difieran |
| Comparar comunas | Barras ordenadas y mapa contextual | Evitar usar solo áreas geográficas para comparar conteos |
| Explorar distribución de edad | Histograma o bandas de edad | Solo si hay calidad y granularidad suficientes |
| Narrar hallazgos | Secuencia de anotaciones y gráficos | Cada afirmación debe enlazar a métrica, periodo, filtro y fuente |

### 6. Vistas previstas
- **Vista A — Mapa:** puntos agregados a escala ciudad y puntos individuales al acercarse; selección de comuna/barrio.
- **Vista B — Ritmos temporales:** heatmap hora × día y serie temporal.
- **Vista C — Gravedad y clases:** barras comparativas y composición.
- **Vista D — Víctimas:** características agregadas, solo con dataset de víctimas y reglas de privacidad.
- **Story mode:** capítulos cortos basados en hallazgos validados.
- **Explore mode:** filtros globales, selección coordinada y detalles bajo demanda.

### 7. Principios perceptuales y Gestalt
- Proximidad: agrupar controles y métricas relacionadas.
- Similitud: mantener codificación semántica consistente.
- Región común: agrupar paneles por tarea.
- Conexión: enlazar selección entre mapa y gráficos.
- Continuidad: facilitar seguimiento de tendencias temporales.
- Figura-fondo: mapa base neutro y datos protagonistas.
- Cierre: simplificar contornos y agrupaciones sin ocultar información relevante.

La aplicación de cada principio se documentará junto con una decisión de diseño concreta, el beneficio esperado y una captura de pantalla.

### 8. Manejo de complejidad
- Reduce: agregación temporal/espacial, filtros y agrupación.
- Select: selección de subconjuntos y elementos.
- Change: cambio de periodo, comuna, clase y gravedad.
- Zoom semántico: cambiar de hexbin/clusters a puntos individuales.
- Paginación para tablas y consultas; no renderizar todos los registros a la vez.

### 9. Alcance y exclusiones
Incluye análisis descriptivo de los datos disponibles, visualizaciones coordinadas, documentación metodológica y demostración. No incluye predicción de accidentes, causalidad, evaluación de riesgo por exposición ni recomendaciones de ingeniería vial sin datos adicionales.

### 10. Criterios de aceptación
- Cada dataset tiene ficha técnica y procedencia.
- Cada vista responde a una tarea explícita.
- Todas las métricas tienen fórmula y unidad.
- Los filtros compartidos producen resultados consistentes.
- Se muestran cobertura, actualización y limitaciones.
- No se confunden incidentes con víctimas.
- Story mode solo presenta afirmaciones reproducibles.
