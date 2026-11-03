# Requisitos de pipeline

Codex debe crear scripts funcionales en `scripts/`:

- `acquire.py`: ArcGIS metadata + objectIds + batches, verificación de IDs; MEData CSV/dictionaries via enlaces actuales del portal. Retry/backoff, timeout, logs, manifest con UTC, URL final, Content-Type, tamaño, SHA-256 y errores.
- `audit.py`: rows/columns/types, nulos y %, exact duplicates, candidate keys, cardinalidad, fechas parseables/periodo observado, coordinate pairs/outliers, categorías y warnings.
- `prepare.py`: idempotente, preserva raw inmutable, mantiene columnas originales, limpia con trazabilidad y crea agregados/Parquet.
- `profile.py` o notebooks: EDA reproducible, tablas y gráficos.

Estructura: `data/raw/`, `data/processed/`, `data/metadata/`, `reports/`. Raw/processed grandes no deben entrar a Git. Outputs: acquisition manifest, diccionario consolidado, audit report Markdown/JSON. Detectar HTML de error como respuesta CSV. Si falla una fuente, continuar con las demás y documentar el bloqueo. No usar datos simulados como si fueran reales.
