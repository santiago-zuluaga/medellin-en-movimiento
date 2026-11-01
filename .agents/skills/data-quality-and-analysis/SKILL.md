---
name: data-quality-and-analysis
description: Audita fuentes, perfila datos, detecta nulos/duplicados, documenta limpieza y valida métricas reproducibles.
---
# Data Quality and Analysis

Por dataset:
1. Registra URL, organismo, fecha de descarga, actualización, licencia y checksum.
2. Identifica unidad de análisis, clave primaria candidata, granularidad y cobertura.
3. Perfila tipos, nulos, duplicados, cardinalidad, rangos y valores inválidos.
4. Revisa discontinuidades temporales, categorías inconsistentes y coordenadas.
5. Mantén raw inmutable; transforma de forma reproducible.
6. Documenta cada regla de limpieza y número de filas afectadas.
7. Crea pruebas para invariantes y agregaciones.
8. Distingue incidentes, víctimas, fallecimientos, aforos y mediciones.
No combines fuentes por proximidad espacial sin justificación. No imputes ni elimines sin registrar. Nunca inventes resultados para completar un gráfico.
