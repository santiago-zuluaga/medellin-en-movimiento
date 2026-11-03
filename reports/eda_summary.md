# EDA reproducible

Las tablas y gráficos se regeneran con `python scripts/eda.py`. Son conteos de registros, no estimaciones de riesgo.

## siniestralidad

- Unidad: registro de evento según fila fuente.
- Filas: 235,820; fechas no parseables: 0.
- Periodo observado: 2019-01 a 2025-12.
- Registros por año: `{"2019": 46551, "2020": 31755, "2021": 40655, "2022": 38642, "2023": 24957, "2024": 23041, "2025": 30219}`.
- Categorías: `{"DAÑOS": 65069, "HERIDOS": 170751}`.
- Cobertura y clasificación pueden cambiar con revisiones de la fuente; los conteos no son tasas.

## mortalidad

- Unidad: registro de la capa de mortalidad; equivalencia a persona fallecida/evento pendiente.
- Filas: 1,541; fechas no parseables: 0.
- Periodo observado: 2019-01 a 2024-12.
- Registros por año: `{"2019": 251, "2020": 200, "2021": 253, "2022": 247, "2023": 277, "2024": 313}`.
- Categorías: `{"Atropello": 658, "Caída Ocupante": 40, "Choque": 819, "Incendio": 1, "Otros": 3, "Sin dato": 9, "Sumersión": 2, "Volcamiento": 9}`.
- Cobertura y clasificación pueden cambiar con revisiones de la fuente; los conteos no son tasas.
