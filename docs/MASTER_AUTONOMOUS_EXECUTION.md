# Medellín en movimiento — Instrucciones maestras para ejecución autónoma en Codex

## Misión
Completar de principio a fin el proyecto universitario de Visualización y Data Storytelling **Medellín en movimiento: exploración visual de la siniestralidad vial y los patrones de movilidad urbana**. No entregues solo una propuesta, wireframe o tutorial: trabaja en el repositorio, implementa, ejecuta, prueba y documenta. Continúa entre fases sin preguntar “¿sigo?”; solo solicita intervención por credenciales, consentimiento, decisiones irreversibles o bloqueos reales que no puedan resolverse con alternativas seguras.

## Primeros pasos obligatorios
1. Inspecciona el repositorio, Git status, branch, archivos existentes y stack actual. No reemplaces trabajo sin entenderlo.
2. Lee `AGENTS.md`, todos los documentos `docs/` y skills relevantes de `.agents/skills/`.
3. Crea `docs/EXECUTION_LOG.md`, `docs/DECISIONS.md` y checklist de ejecución.
4. Ejecuta una baseline de tests/lint/build si existe antes de modificar.
5. Empieza por fase 0 y continúa hasta Definition of Done o bloqueo.

## Reglas de seguridad/autonomía
- No inventes datasets, conteos, hallazgos, citas, licencias ni métricas.
- No borres archivos/datasets de usuario; no ejecutes `git reset --hard`, `git clean -fd`, force-push ni acciones destructivas.
- No publiques/despliegues ni subas datos a terceros sin permiso.
- No expongas datos personales, direcciones exactas ni radicados en la interfaz. Usa agregados.
- Raw data debe quedar inmutable y excluida de Git cuando sea grande o sensible.
- Registra comandos, versiones, errores, decisiones y artefactos. No digas que una prueba pasó si no se ejecutó.
- Si falla Computer Use, no repitas intentos indefinidamente: usa API/CLI/terminal o documenta bloqueo.
- Mantén idioma español, salvo código/terminología.
- No te detengas para pedir aprobación en tareas rutinarias, no destructivas.

## Tema, objetivo y público
Pregunta guía: **¿Qué patrones espaciales, temporales y de composición se pueden observar en los registros oficiales de siniestralidad y movilidad de Medellín, y cómo puede una exploración visual ayudar a comprenderlos sin confundir conteos con riesgo ni atribuir causalidad?**

Audiencia: ciudadanía, estudiantes/investigadores, periodistas de datos y personas interesadas en movilidad/seguridad vial.

Objetivos: explorar localización, distribución temporal, clase/gravedad, víctimas y, si es metodológicamente compatible, contexto de aforos de bicicleta. Visibilizar cobertura, incertidumbre, sesgos y límites.

## Fuentes primarias principales
1. Siniestralidad ArcGIS: `https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Accidentes/MapServer/0` (metadatos previos: 2019–2025, heridos y solo daños).
2. Mortalidad ArcGIS: `https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Mortalidad/MapServer/0` (metadatos previos: 2019–2024).
3. Víctimas MEData: `https://medata.app.medellin.gov.co/node/16692` (unidad: víctima; datos reportados por UNE).
4. Bicicletas MEData: `https://medata.gov.co/node/16523` (caracterización/aforos en estaciones, no censo de todos los viajes).

Verifica links y diccionarios actuales antes de descargar. Los nombres de campos descritos en los documentos del kit son esquema esperado, no garantía de esquema actualizado.

### Reglas semánticas críticas
- incidente ≠ víctima ≠ persona fallecida ≠ observación de aforo.
- No sumar filas entre datasets como si fueran la misma unidad.
- No asumir que `radicado` y `RADICADO` equivalen. Auditar significado, cardinalidad, nulos, duplicados y cobertura antes de unir; si no está probado, no hacer join.
- No llamar “riesgo” a un conteo. Para tasas se requieren denominadores de exposición (viajes, km, tráfico, población expuesta).
- No inferir causalidad.
- No comparar años incompletos con años completos sin advertencia/normalización.
- No eliminar nulos/outliers silenciosamente; conservar originales y documentar decisiones.
- La fuente de bicicletas representa estaciones/ubicaciones y periodicidad, no movilidad total de la ciudad.

## Stack preferido (respetar repo si ya hay una buena solución)
React + TypeScript + Vite; D3.js para gráficos; MapLibre GL JS para mapas; Python/pandas/GeoPandas para ETL; DuckDB/Parquet para volúmenes grandes; FastAPI solo si aporta; Vitest/Testing Library/Playwright; pytest; ESLint/Prettier/Ruff. No añadir tecnología innecesaria.

## Pipeline de datos requerido
Implementa scripts reproducibles en `scripts/`:
- `acquire.py`: descarga metadata ArcGIS, consulta IDs, obtiene registros por lotes (maxRecordCount), compara IDs solicitados vs descargados; pide WGS84/EPSG:4326. MEData: sigue enlaces de ficha actual (no asumir CSV URL permanente). Usa timeout/retry/backoff.
- `audit.py`: columnas/tipos, filas, nulos y %, duplicados exactos, candidate keys, cardinalidad, fechas parseables y periodo real, coordenadas, outliers espaciales, categorías, unidades y compatibilidad.
- `prepare.py`: transformaciones idempotentes, conserva columnas originales, exporta Parquet/CSV agregados a `data/processed`, sin sobrescribir `data/raw`.
- `profile.py`/EDA notebooks: resúmenes y plots reproducibles.
- Manifiesto: `reports/acquisition_manifest.json` con UTC timestamp, URL final, content type, status, bytes, SHA-256, version/metadatos y errores.
- Diccionario: `data/metadata/data_dictionary.json` y diccionarios originales.
- Informes: `reports/audit_report.md` y `.json`.

Detecta HTML/JSON de error guardado como CSV. Si un dataset falla, reporta la causa y continúa con los demás. No declare éxito si no se descargaron datos reales. Usa clasificación PASS/WARN/FAIL con razones.

## EDA y narrativa
Primero analiza los datos; después escribe hallazgos/narrativa. No forzar story beats que los datos no soporten. Genera tablas y visualizaciones de EDA, comprueba consistencia temporal/espacial y redacta un outline basado en evidencia. Cada afirmación de resultado debe tener una consulta/tabla reproducible detrás.

## App: Story + Explore
**Story**: narrativa guiada por capítulos (ajustables tras EDA):
1. Una ciudad en movimiento.
2. La geografía de los registros.
3. El tiempo también importa.
4. Las personas detrás de los datos.
5. Otras formas de moverse.
6. Lo que los datos no pueden decir.

Cada capítulo: pregunta, contexto, gráfico, interpretación basada en resultado real, nota metodológica/limitación, fuente y navegación.

**Explore**: exploración libre con filtros globales (fecha/año, comuna, clase, gravedad, día/hora, actor vial si aplica), selección coordinada, estado activo, botón reset, tooltips, leyendas, estados loading/error/empty, metodología y fuentes.

Vistas recomendadas:
- mapa con clustering/hexbin/heatmap según zoom y agregación/LOD;
- heatmap día × hora;
- series temporales por mes/año;
- barras clase/gravedad;
- víctimas por actor vial/edad/gravedad;
- bicicletas por estación/periodo/hora, separado de siniestros y con caveat.

No implementes un gráfico si la calidad o semántica no lo soporta. No renderices decenas de miles de elementos DOM. Usa agregación/Parquet/DuckDB/vector tiles si lo justifica el perfil.

## Diseño editorial / data journalism
No dashboard SaaS genérico ni tarjetas KPI sin propósito. Hero editorial, título/bajada, tipografía con jerarquía, anotaciones, fuentes, fechas, unidades y leyendas. Paleta semántica accesible, no rainbow, no 3D. Responsive, keyboard navigation, focus, aria labels, contrast WCAG AA cuando sea posible, reduced motion. Color no debe ser único canal para distinguir categorías.

## Gestáltica: documentar cada visualización
Aplicar según corresponda:
- proximidad (filtros/leyenda cerca del gráfico);
- similitud (encoding consistente);
- región común (paneles/selección);
- conexión (cross-filter/selection);
- continuidad (series y orden);
- figura-fondo (selección vs contexto);
- cierre (grupos/contornos legibles).

Para cada view documenta: pregunta, tarea abstracta (compare/locate/summarize/identify/filter), marks/channels, Gestalt, justificación, interacción, limitación y alternativa descartada.

## Informe académico obligatorio
Crear `docs/FINAL_REPORT.md` o equivalente con:
1. Basic info.
2. Overview (What/Why/How, contexto, objetivo, público).
3. Data (origen, acceso, cobertura, unidad, diccionario, calidad, licencia/atribución, limitaciones).
4. Tasks (domain language, user tasks, abstract tasks).
5. Visualizations (marks/channels, Gestalt, coordinación, complejidad, alternativas).
6. Usage scenario (walkthrough Story/Explore).
7. Reflections (hallazgos reales, limitaciones, evaluación, futuro).
8. Work breakdown & schedule (fases y contribución; no inventar horas/personas).
9. Credits (datasets, librerías, inspiración, IA y aportes).

Inspirarse en estructura del informe UBC CPSC 447, pero no copiar texto. Debe incluir método, EDA, visual rationale, Gestalt, performance, tests, resultados verificables, sesgos, bibliografía/citas, capturas si existen. Si un dato no se obtuvo, marcar `PENDIENTE DE VALIDACIÓN`.

## Archivos a mantener
- README.md (setup, scripts, demo, data setup)
- AGENTS.md
- docs/PROJECT_PROPOSAL.md
- docs/DATA_DICTIONARIES.md
- docs/DATA_VALIDATION_PLAN.md
- docs/AUDIT_PROTOCOL.md
- docs/VISUALIZATION_DESIGN.md
- docs/GESTALT_RATIONALE.md
- docs/EXECUTION_LOG.md
- docs/DECISIONS.md
- docs/FINAL_REPORT.md
- docs/TESTING.md
- docs/DATA_SOURCES.md
- docs/KNOWN_LIMITATIONS.md
- `.env.example` si aplica; nunca secretos.

## Fases — ejecuta en orden y continúa autónomamente
0. Reconocer repo, baseline, plan/log.
1. Adquisición de fuentes, diccionarios y auditoría real.
2. EDA, tablas/gráficos y narrativa basada en resultados.
3. Diseño de información, wireframes, sistema editorial y Gestalt.
4. Implementar data layer, Story, Explore, mapa, charts y filtros coordinados.
5. Tests, accessibility, performance, lint/typecheck/build.
6. Informe académico, README, créditos, fuentes, limitaciones.
7. Entrega: verificar comandos reproducibles, screenshots, guion demo 5–8 min, resumen de bloqueos.

## Definition of Done
- adquisición reproducible o fallo bien documentado;
- auditoría empírica ejecutada sobre registros reales;
- ninguna estadística inventada;
- app corre localmente según README;
- Story y Explore navegables;
- filtros y cross-filter funcionan/reset;
- mapa/charts con fuente, unidad, leyenda;
- unidades de análisis respetadas;
- Gestalt rationale por vista;
- responsive/accessibility esenciales;
- tests, lint, typecheck y build ejecutados;
- informe académico completo y basado en evidencia;
- limitaciones, licencia, créditos, demo y reproducibilidad listos.

## Reporte final
Entrega resumen de implementación, estructura, comandos, fuentes/unidades/limitaciones, pruebas con resultados, hallazgos reales, pendientes/manuales y rutas de documentación. **Empieza ahora en fase 0 y sigue hasta Definition of Done.**
