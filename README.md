# Medellín en movimiento

Aplicación local para explorar registros oficiales de siniestralidad y mortalidad vial en Medellín. Las cifras describen filas de las fuentes disponibles; no son tasas de riesgo ni conclusiones causales.

## Requisitos

- Python 3.10 o posterior (biblioteca estándar; no instala paquetes).
- Navegador moderno.
- Acceso a internet solo para descargar las fuentes oficiales en la primera adquisición.

La interfaz usa HTML/CSS/JavaScript y SVG nativos; no necesita Node, npm, servidor externo, tiles de mapa ni librerías de terceros. El servidor local de datos usa `http.server` de Python.

## Puesta en marcha

Desde la raíz del repositorio, en PowerShell:

```powershell
python scripts/acquire.py
python scripts/audit.py
python scripts/prepare.py
python scripts/eda.py
python scripts/serve.py
```

Abre `http://127.0.0.1:8000`. `Ctrl+C` detiene el servidor.

`acquire.py` usa ArcGIS REST con páginas limitadas, verifica IDs y solicita solo campos analíticos. Excluye ID/RADICADO y direcciones. Para víctimas y bicicleta descarga únicamente los diccionarios: sus CSV por persona no se almacenan. Raw nunca se sobrescribe; las instantáneas bajo `data/raw/` y agregados bajo `data/processed/` están excluidos de Git.

## Pruebas

```powershell
python scripts/test_data_model.py
python scripts/test_api.py
node --check web/app.js
python -m py_compile scripts/acquire.py scripts/audit.py scripts/prepare.py scripts/eda.py scripts/data_model.py scripts/serve.py
```

Las pruebas de API usan archivos locales reales si existen. Las pruebas pequeñas de modelo usan fixtures manuales rotulados como fixtures, no son hallazgos del proyecto.

## Modos

- **Story:** narrativa y conteos reproducibles a partir de la instantánea descargada.
- **Explore:** filtros globales coordinan mapa agregado, comuna, clase, gravedad, serie mensual y heatmap día-hora con escala de color dinámica mínimo/máximo; Restablecer limpia el estado.

En móvil se apilan los paneles. Hay estados de carga/error/vacío, etiquetas y operación por teclado en selecciones SVG.

## Estado del QA visual

QA reanudado el 3 de noviembre de 2026: las capturas reales `reports/screenshots/story-desktop.png` y `explore-desktop.png` muestran Story y Explore con datos locales. La suite del modelo pasó 5 pruebas y la API pasó 7 pruebas con permiso de loopback; `node --check`, `py_compile` y `git diff --check` pasaron. Se cotejaron los hashes raw contra el manifiesto y no se volvió a adquirir ni escribir `data/raw/`. La captura llamada `tooltip-example.png` no muestra un tooltip abierto; no se cuenta como prueba. El intento de crear capturas de Método/móvil con Chrome headless no produjo archivos. Siguen pendientes la evidencia Método/móvil/tooltip/vacío, la repetición del recorrido completo, matriz responsive completa, estado de error/vacío visible, lector de pantalla/WCAG/contraste, tacto físico y rendimiento en equipos objetivo. Definition of Done: OPEN. Ver alcance y distinción de estados en `docs/TESTING.md`, `docs/EXECUTION_CHECKLIST.md` y `docs/EXECUTION_LOG.md`.

## Documentación y artefactos

- `docs/MASTER_AUTONOMOUS_EXECUTION.md`: instrucciones rectoras.
- `docs/DATA_SOURCES.md`, `DATA_DICTIONARIES.md`, `DATA_VALIDATION_PLAN.md`: fuentes, unidades, esquemas y auditoría.
- `docs/VISUALIZATION_DESIGN.md`, `GESTALT_RATIONALE.md`: decisiones visuales y perceptuales.
- `docs/FINAL_REPORT.md` y `reports/medellin_en_movimiento_informe_academico.pdf`: informe académico editable y versión de entrega; `TESTING.md` y `KNOWN_LIMITATIONS.md`: pruebas y cautelas.
- `docs/EXECUTION_LOG.md`, `DECISIONS.md`: bitácora y decisiones.
- `reports/acquisition_manifest.json`: fechas UTC, estado, URL, tamaños y SHA-256.
- `reports/audit_report.md` / `.json`: perfilado empírico.
- `reports/eda_summary.md`, `eda_*.svg`: tablas y gráficos EDA.

## Reproducibilidad

Las adquisiciones son instantáneas, no feeds en tiempo real. Los servicios fuente se actualizan; la fecha, respuestas y hashes de esta ejecución están en el manifiesto. Consulte la licencia/condiciones del servicio ArcGIS antes de redistribuir sus datos; no se identificó una licencia abierta explícita en esos metadatos.
