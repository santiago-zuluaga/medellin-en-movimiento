# Registro de decisiones

| ID | Decisión | Motivo/evidencia | Estado |
|---|---|---|---|
| D-001 | Mantener unidades separadas para incidente, víctima, registro de mortalidad, persona ciclista aforada y medición de tránsito. | Definiciones y granularidad diferentes según propuesta y fichas oficiales. | Adoptada |
| D-002 | Usar capas de siniestralidad y mortalidad ArcGIS como fuentes centrales separadas; diagnosticar solapamiento antes de cualquier relación. | Endpoints oficiales activos y esquemas distintos; la mortalidad tiene cobertura y proceso de clasificación separados. | Adoptada, pendiente de auditoría empírica |
| D-003 | Excluir dirección, `radicado`, `id` y otros identificadores del producto y de las extracciones persistidas cuando no sean necesarios. | Minimización de datos y riesgo de identificación/localización precisa. | Adoptada |
| D-004 | No usar aforos de bicicleta, velocidad o intensidad como denominadores de riesgo sin compatibilidad temporal, espacial y metodológica demostrada. | La cobertura es localizada/de estaciones y no representa automáticamente exposición total. | Adoptada |
| D-005 | No mostrar narración cuantitativa como hallazgo hasta que exista cálculo reproducible sobre datos auditados. | Requisito de no inventar resultados y trazabilidad de Story. | Adoptada |
| D-006 | No incluir datos descargados en Git; conservar adquisición local con checksum y metadatos. | Protección de datos, reproducibilidad y tamaño de archivos. | Adoptada; `data/raw/` y `data/processed/` ignorados |
| D-007 | Acotar la app a dos capas ArcGIS y dejar microdatos de víctimas/bicicleta fuera. | Diccionarios oficiales revelan RADICADO/dirección para víctimas y fila por persona aforada con estación/hora/demografía para bicicleta. | Adoptada |
| D-008 | Usar HTML/CSS/ES modules/SVG nativos y servidor Python estándar, sin React/D3/MapLibre. | No existía stack ni paquetes; mantiene funcionamiento reproducible sin instalación ni llamadas a terceros. Se conserva la semántica de marcas, escalas e interacciones documentada. | Adoptada para esta entrega |
| D-009 | Mantener duplicados por firmas de atributos sin deduplicar. | No se verificó si firmas idénticas representan duplicación administrativa o registros legítimamente repetidos; ObjectID es técnico, no criterio suficiente para descartar. | Adoptada |
