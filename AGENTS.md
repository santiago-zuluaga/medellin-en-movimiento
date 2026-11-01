# Medellín en movimiento — instrucciones para Codex

## Misión
Construir una aplicación de visualización de datos y data storytelling sobre movilidad y seguridad vial en Medellín. La aplicación debe permitir exploración analítica y lectura narrativa, con datos trazables, visualizaciones justificadas y rendimiento adecuado para datos geoespaciales y temporales.

## Reglas no negociables
1. No inventar datos, estadísticas, citas, fuentes, resultados ni hallazgos.
2. No presentar una asociación como causalidad.
3. Distinguir siempre las unidades de análisis: incidente, víctima, persona fallecida, aforo ciclista, observación de velocidad y conteo vehicular.
4. No combinar datasets hasta comprobar definiciones, granularidad, cobertura temporal, claves y duplicados.
5. Conservar los datos originales sin modificaciones en `data/raw/`; escribir transformaciones reproducibles hacia `data/processed/`.
6. Toda métrica publicada debe tener definición, fórmula, unidad, filtros y fuente documentados.
7. Toda visualización debe responder a una tarea analítica y documentar marcas, canales, escalas, agregación, limitaciones y justificación.
8. No usar color como único canal para comunicar una categoría.
9. Evitar gráficos 3D decorativos, ejes truncados engañosos y mapas coropléticos de conteos absolutos sin contextualización.
10. No descargar ni incorporar datos personales identificables. Minimizar campos sensibles y agregar cuando corresponda.
11. No afirmar que un dato es representativo de toda la ciudad si su método de recolección no lo respalda.
12. Antes de modificar archivos, inspeccionar el repositorio y explicar brevemente el plan.

## Flujo de trabajo por fases
- Fase 0: inspección del repositorio y lectura de skills.
- Fase 1: propuesta y definición de tareas analíticas.
- Fase 2: adquisición, inventario y validación de datos.
- Fase 3: EDA y diccionario definitivo.
- Fase 4: abstracción, selección de gráficos y prototipos.
- Fase 5: sistema visual editorial y arquitectura.
- Fase 6: implementación vertical por funcionalidad.
- Fase 7: pruebas de datos, interacción, accesibilidad y rendimiento.
- Fase 8: informe académico, demo y reflexión.

No avanzar a una fase posterior si hay criterios de aceptación pendientes. Si falta información, registrar la incertidumbre y proponer cómo resolverla; no rellenarla con suposiciones.

## Dirección visual
Identidad editorial de data journalism: tipografía expresiva para titulares, tipografía legible para datos, jerarquía marcada, espacio en blanco, paleta sobria y acentos semánticos consistentes. Evitar el aspecto genérico de plantilla SaaS. La visualización y la lectura de datos son protagonistas.

## Modos de producto
- Story: narrativa guiada con afirmaciones respaldadas por datos y metodología visible.
- Explore: exploración libre con filtros compartidos, selección coordinada y posibilidad de restablecer el estado.

## Definición de terminado
Una funcionalidad se considera terminada solo si:
- funciona con datos reales o muestra claramente que usa datos de muestra;
- sus cálculos tienen pruebas;
- estados de carga, vacío y error están resueltos;
- filtros y selecciones son coherentes entre vistas;
- es accesible por teclado cuando aplique;
- no presenta resultados no verificados;
- está documentada.
