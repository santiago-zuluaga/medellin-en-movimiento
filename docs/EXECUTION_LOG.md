# Registro de ejecución

Fecha de inicio: 2026-11-02 (America/Bogota)
Estado: en curso

Este registro distingue verificaciones ejecutadas de planes. No se anotará una fase como terminada hasta comprobar sus criterios.

## Fase 0 — Reconocimiento y baseline

### Inspección
- Leídos `AGENTS.md`, `START_HERE_CODEX.md`, `docs/MASTER_AUTONOMOUS_EXECUTION.md`, `docs/EXECUTION_CHECKLIST.md`, `docs/DATA_PIPELINE_REQUIREMENTS.md`, los documentos existentes de `docs/` y las ocho skills de `.agents/skills/`.
- Rama observada: `main`.
- Archivos existentes: documentación de propuesta/datos/diseño, `scripts/profile_local_data.py`, README y skills; no se encontró aplicación, datos locales, manifiesto de dependencias ni suite de pruebas.
- El estado inicial ya contenía `AGENTS.md` modificado y cuatro documentos nuevos sin seguimiento (`START_HERE_CODEX.md` y tres documentos de ejecución). Se preservan; no son cambios atribuibles a esta ejecución.
- Node.js/npm están disponibles. El alias de Python apunta a WindowsApps y falló con “El sistema no tiene acceso al archivo”; no se pudo ejecutar la baseline Python. No había comandos de test/lint/build configurados.

### Fuentes verificadas (metadatos, no archivos de datos)
- ArcGIS `VM_Accidentes/MapServer/0`: endpoint responde. Metadatos describen puntos de siniestralidad con heridos/solo daños de 2019–2025, CRS EPSG:9377, `maxRecordCount=2000`, campos `radicado` y `direccion` junto a atributos temporales/espaciales. La capa declara actualización constante.
- ArcGIS `VM_Mortalidad/MapServer/0`: endpoint responde. Metadatos describen mortalidad 2019–2024, CRS EPSG:9377, `maxRecordCount=2000`, e incluyen `id`, dirección, sexo/edad y atributos espaciales.
- MEData mantiene ficha de víctimas con descargas CSV/diccionario, temporalidad desde 2014 y licencia CC BY-SA 4.0; la ficha dice que los registros proceden de reportes de víctimas entregados por UNE. Falta revisar los ficheros actuales y el contenido del diccionario antes de descargar el CSV.
- Ficha de bicicleta identificada en MEData; su archivo actual no se descargó ni perfiló.
- Las verificaciones web confirman metadatos/endpoints, no disponibilidad integral, calidad empírica ni compatibilidad entre fuentes.

### Comandos y resultados
- `git branch --show-current`: `main`.
- `git status --short`: cambios preexistentes descritos arriba.
- Inspección de archivos (`rg --files`, `git ls-files`): completada.
- Baseline `python --version` y comprobación de imports: falló porque el ejecutable WindowsApps no está accesible.
- Baseline Node/npm: Node v24.19.0 y npm 11.17.0.

### Baseline completada y resultado de adquisición
- `python`/`python3` de WindowsApps no ejecutables; se encontró Python 3.12.14 en el runtime integrado de Codex. Imports disponibles comprobados: pandas sí; GeoPandas, PyArrow, DuckDB, requests, pytest y matplotlib no. Se eligió biblioteca estándar y no se instaló nada.
- `node --version`: v24.19.0; `npm --version`: 11.17.0. No hay `package.json` ni stack instalado.
- El primer intento ArcGIS usó la lista completa de ObjectIDs en una URL y recibió HTTP 414. Se corrigió a paginación por `resultOffset`/`resultRecordCount` y comprobación del conjunto de ObjectIDs. La descarga posterior resultó en PASS.
- Red DNS bloqueada en sandbox; ejecución de descarga aprobada explícitamente por permiso de escalamiento para fuentes oficiales. No se subieron datos.
- La invocación inicial `--only municipality_boundary` reemplazó temporalmente el manifiesto de fuentes anterior. Se corrigió el script para mergear ejecuciones y recuperar entradas de raw inmutable; el siguiente manifiesto consolidado registra cinco fuentes y todas las rutas/hash. Se anotará esta incidencia para transparencia.
- `scripts/acquire.py`: 5/5 fuentes con PASS en la ejecución consolidada: siniestralidad 235.820 filas, mortalidad 1.541, límite municipal 1 geometría y dos diccionarios. Las respuestas ArcGIS comprobaron ObjectIDs solicitados/recibidos y se solicitó EPSG:4326. Los CSV individuales de víctimas/bicicleta se omitieron por privacidad; diccionarios adquiridos.
- Checksums observados en la descarga original: siniestralidad `ee18cde382f201a036ec668f7d92839f36d889685473aa7e81a8c194f6c42068`; mortalidad `4b7c7319db29ecc8fc177c8fb3399c1bd582e78029fda99a62e86a6c0409468e`; diccionario víctimas `d8940ccc1982d401283e0c95830ac1e59e0de5958205f3b9e7c9c41e0768108d`; bicicleta `a81c5d649c9fa5952649302e8c9184eaa2677ab570d18a824d6ad3946aedf348`. La geometría municipal y sus hash están en el manifiesto vigente.

## Fase 1 — Adquisición y auditoría

### Resultados
- Fechas de las dos capas parseables al 100%; siniestralidad de 2019-01 a 2025-12 y mortalidad 2019-01 a 2024-12.
- Siniestralidad: 175 firmas con atributos repetidos al excluir ObjectID; 0 coordenadas inválidas; 0 discordancias lat/lon-geometría; 7 fuera de envolvente municipal y 237 fuera del límite municipal por punto-en-polígono.
- Mortalidad: 33 firmas repetidas al excluir ObjectID; 4 coordenadas/geometrías faltantes; 0 discordancias entre atributos y geometría presentes; 4 puntos fuera del polígono.
- La capa mortalidad mantiene unidad por fila sin equivalencia confirmada a persona fallecida/incidente. No se hizo join con siniestralidad (no hay clave validada disponible sin `id`/radicado).
- Se contrastó el índice de punto-en-polígono con el algoritmo sobre todos los vértices en muestra determinista de 1.000 puntos; discrepancias 0. No se eliminaron outliers ni firmas repetidas.
- Artefactos: `reports/acquisition_manifest.json`, `reports/audit_report.md/.json`, `docs/DATA_SOURCES.md`, `docs/DATA_DICTIONARIES.md`, `docs/KNOWN_LIMITATIONS.md`. Raw y processed se ignoran por Git.
- Comandos: `python-runtime scripts/acquire.py`; `scripts/audit.py`; `scripts/prepare.py`; se verificaron hashes, rutas y archivos locales.
- Clasificación: dos fuentes analíticas PASS con WARN abiertos; límite PASS; diccionarios PASS. Las licencias ArcGIS siguen pendientes de confirmación; no redistribuir sus datos sin resolverlas.

## Fase 2 — EDA y narrativa basada en evidencia

- `scripts/eda.py` generó JSON por fuente y barras SVG por año sin bibliotecas externas.
- Conteos siniestralidad por año: 2019 46.551; 2020 31.755; 2021 40.655; 2022 38.642; 2023 24.957; 2024 23.041; 2025 30.219. Categorías: HERIDOS 170.751 y DAÑOS 65.069.
- Mortalidad por año: 2019 251; 2020 200; 2021 253; 2022 247; 2023 277; 2024 313. Se describe como filas de la capa, no número de personas fallecidas.
- No se redactan explicaciones causales. Se advierte actualización continua y falta de denominadores/captura comparable.
- `scripts/prepare.py` crea CSV agregados por mes, comuna, categoría y redondeo espacial (supresión <5); no muta raw ni combina fuentes. No es hexbin ni Parquet.

## Fase 3 — Diseño editorial

- Se definieron retícula editorial, paleta sobria, jerarquía serif/sans/mono con fuentes de sistema, filtros y paneles de mapas/gráficos, y fichas con tarea/marca/canal/unidad/limitación en `VISUALIZATION_DESIGN.md`.
- `GESTALT_RATIONALE.md` documenta proximidad, similitud, región común, conexión, continuidad, figura-fondo y cierre.
- Decisión D-008: sin React/D3/MapLibre, porque no había stack y se pudo cumplir con SVG nativo sin instalaciones/red en la UI. Los principios de las skills de visualización siguen aplicados/documentados.

## Fase 4 — Implementación app

- Se creó app local Story + Explore, API de agregación y servidor Python estándar. La API no devuelve ObjectID/radicado ni coordenadas individuales; el mapa usa grupos redondeados con supresión de celdas <5.
- Filtros compartidos por fuente, año, comuna, clase, gravedad (solo siniestralidad), día-hora y grupo espacial; selección en barras/mapa/heatmap/serie y botón de restablecer.
- Incluye estados de carga, error y vacío, foco/teclado, responsive y `prefers-reduced-motion`. No usa tiles ni fuentes remotas.
- Archivos: `web/index.html`, `web/styles.css`, `web/app.js`, `scripts/data_model.py`, `scripts/serve.py`.

## Fase 5 — Pruebas ejecutadas

- `scripts/test_data_model.py`: 5 pruebas OK.
- `scripts/test_api.py`: primera ejecución en sandbox falló con WinError 10013 al abrir loopback. Segunda ejecución con permiso aprobado: 5 pruebas OK (16,481 s), incluidos cross-filter, no exposición de IDs, unidad de mortalidad, dataset inválido y entrega de HTML/JS.
- `scripts/test_data_model.py`: repetida tras regenerar artefactos; 5 pruebas OK.
- `node --check web/app.js`, `python -m py_compile scripts/*.py` seleccionados y `git diff --check`: PASS tras los últimos cambios de adquisición.
- QA visual: el navegador cargó la portada, pero al inspeccionar la narrativa se encontró `communityList.map is not a function`; se corrigió el render y se desacopló la carga del límite municipal. La recarga posterior no permitió confirmar la narrativa actualizada en esta sesión: la vista siguió en su placeholder de carga. Se registra como verificación pendiente, no como PASS.
- Aún no hay captura de la aplicación completamente renderizada ni medición de rendimiento UI; no se afirmarán.

## Fase 6 — Documentación y entrega

- `README.md`, `DATA_SOURCES.md`, `DATA_DICTIONARIES.md`, `AUDIT_PROTOCOL.md`, `KNOWN_LIMITATIONS.md`, `TESTING.md`, `FINAL_REPORT.md` y `DEMO_SCRIPT.md` creados/actualizados.
- Manifiesto post consolidación reejecutado: cinco fuentes registradas, todas en estado PASS; extracción local reutilizada sin reescritura de raw.
- Pendiente: confirmar carga final en navegador, capturar la aplicación renderizada, ejecutar revisión de accesibilidad con herramientas/lector y medir rendimiento en equipos objetivo.

### Decisiones y bloqueos
- No se descargará al navegador ni se publicará dirección exacta, radicado, identificador individual ni coordenadas de registros sensibles. Para capas ArcGIS se solicitarán únicamente campos necesarios para agregación y coordenadas, excluyendo los identificadores/direcciones; se guardará la respuesta original de esa extracción mínima como raw con trazabilidad.
- No descargar el CSV de víctimas hasta inspeccionar diccionario y confirmar que se puede adquirir una versión minimizada sin identificadores personales. Si el portal solo ofrece CSV completo con identificadores, se documentará el bloqueo y se excluirá esa fuente o se procesará sin persistir campos sensibles, preservando trazabilidad de la excepción.
- Python no disponible constituye bloqueo de ejecución para pipeline Python. Se buscará otro runtime local instalable/ya presente sin modificar configuración global; si no existe, el pipeline se diseñará de modo verificable con Node.js o se pedirá permiso para habilitar Python.
- Ninguna fase posterior está declarada completa en esta entrada.

## Fase 1 — Propuesta y tareas analíticas

- La propuesta se acotó a preguntas descriptivas sobre cuándo, dónde y cómo se registran los siniestros, con mortalidad como capa separada de filas y cobertura temporal distinta.
- Se excluyeron del producto las filas individuales de víctimas y aforos ciclistas: el diccionario y la ficha advierten granularidad individual y/o atributos identificables/sensibles que no hacen falta para las preguntas seleccionadas.
- La propuesta, limitaciones y tareas están documentadas en `PROJECT_PROPOSAL.md`, `DATA_VALIDATION_PLAN.md`, `DATA_SOURCES.md`, `KNOWN_LIMITATIONS.md` y `FINAL_REPORT.md`.
- No se declara cerrada la Fase 1: el equipo aún debe confirmar la unidad semántica exacta de la capa de mortalidad y resolver la licencia/condiciones de redistribución de las capas ArcGIS antes de publicación externa.

## Fase 7 — Entrega (incompleta)

- Se ejecutaron nuevamente `py_compile`, `node --check`, `git diff --check`, cinco pruebas unitarias y cinco pruebas de integración con datos reales; todas terminaron correctamente. La integración API se ejecutó con permiso de loopback.
- En esta revisión inicial, el navegador local mostró un error de render en Story y luego quedó en el placeholder. La actualización posterior del equipo, registrada abajo, confirma que Story sí carga datos reales; esa inspección manual supera el resultado previo de carga fallida.
- En la verificación actual se corrigió el espaciado/formato de etiquetas y cifras de Story. No se pudo confirmar el aspecto corregido, el recorrido completo ni Explore: Computer Use se detuvo al no poder determinar la URL de Opera. Como alternativa se intentó Edge headless aislado, que salió con código 21 sin crear captura.
- No se guardó captura de Story o Explore; no se completó revisión automatizada de WCAG/lector de pantalla, no se midió rendimiento en equipos objetivo y no hay pipeline de lint/typecheck/build porque el producto no usa React/TypeScript ni un gestor de paquetes.
- El manifiesto confirma cinco fuentes PASS y las transformaciones/EDA se reprodujeron; la geometría municipal y ambos datasets se excluyen de Git. No se valida equivalencia de las filas de mortalidad con personas fallecidas ni licencia para redistribución pública.
- Estado de aceptación: el equipo verificó carga de Story y el pipeline local/tests de datos/API están verificados; la Fase 7 y Definition of Done siguen abiertas hasta confirmar el formato corregido, recorrer Explore e interacciones en navegador, guardar capturas, cerrar accesibilidad/rendimiento, y completar validaciones semánticas/licencia necesarias para la entrega prevista.

## Actualización de QA solicitada por el equipo — 2026-11-03

- El equipo informó que abrió `http://127.0.0.1:8000` y confirmó en capturas Story renderizado con datos reales. Se toma como QA manual reportado por el equipo; las capturas no se encuentran disponibles como archivos en el repositorio.
- Reproducción del defecto visual desde el código: etiquetas y valores de Story se generaban en elementos inline sin estructura ni separación explícita. Se cambiaron las listas a pares etiqueta/valor, con alineación y espacio consistente; se usa `Intl.NumberFormat('es-CO')` para enteros agrupados, porcentaje con coma decimal y coordenadas en el filtro activo con coma decimal.
- No se ejecutó `scripts/acquire.py`, no se reescribió ni modificó `data/raw/`; la auditoría, datos y reportes preexistentes se dejaron intactos.
- Computación de formato verificada en Node: `46551 → 46.551`, `0.724 → 72,4%`, `-75.61 → -75,61`.
- Se intentó obtener QA de navegador por Computer Use sobre la ventana Opera, pero la herramienta terminó la sesión porque no pudo confirmar la URL actual. De acuerdo con la instrucción del proyecto, no se repitieron acciones UI. Edge headless aislado terminó con código 21, sin captura ni evidencia DOM; se registra como intento fallido.
- `node --check web/app.js`, `python -m py_compile` para los scripts del pipeline/API/tests, `git diff --check` y `scripts/test_data_model.py`: PASS tras la corrección de formato (5 pruebas unitarias).
- `scripts/test_api.py`: PASS tras la corrección (5 pruebas de integración, 16,965 s); las peticiones de prueba observadas recibieron HTTP 200 para agregados/estáticos y HTTP 400 para dataset desconocido. Esto verifica el servidor/API; no es una inspección de la consola del navegador.
- Se añadió `test_incident_payload_supplies_each_explore_visualization` para comprobar que la API ofrece los agregados de cada vista Explore y que meses/comunas/categorías/gravedades suman el total filtrado. Reejecución: `scripts/test_api.py`, 6 pruebas OK en 22,832 s.
- Los SHA-256 actuales de los tres GeoJSON en `data/raw/` coinciden con los registrados en el manifiesto: límite municipal `ad0769a044d5cca1b4f0195394b8b90e7020359eee2af3eb27f7e445a4096a36`, mortalidad `4b7c7319db29ecc8fc177c8fb3399c1bd582e78029fda99a62e86a6c0409468e`, siniestralidad `ee18cde382f201a036ec668f7d92839f36d889685473aa7e81a8c194f6c42068`. Confirma que esta ronda no alteró raw.
- Quedan sin comprobar visualmente el resultado de formato, Story de inicio a fin, todas las vistas de Explore, interacción real de filtros/selección/reset/navegación, consola/solicitudes desde el navegador, responsive y capturas de Story y Explore.
- README e informe académico actualizados para distinguir la confirmación manual del equipo de las comprobaciones no realizadas en esta sesión. No se declara la Definition of Done.

## QA visual y funcional de seguimiento — 2026-11-02 (America/Bogota)

### Alcance y evidencia obtenida
- Se reabrió `http://127.0.0.1:8000/` en navegador. Story muestra su hero, capítulos con datos reales y termina con la sección de metodología/fuentes; la inspección de pantalla mostró espacios claros entre texto y valores. Explore mostró los controles compartidos y mapa agregado. El árbol accesible enumeró las seis vistas: mapa, comuna, clase, gravedad, serie mensual y heatmap día-hora, todas con unidad/conteos de siniestralidad.
- Filtro de año: selección 2022 realizada con teclado; control y cifras agregadas cambiaron. Selección de barra: La Candelaria se seleccionó y el estado compartido quedó `año 2022 · La Candelaria`; mapa, barras categóricas, serie mensual y heatmap actualizaron sus agregados. `Restablecer` limpió año y comuna y restauró la cobertura total. Se conserva aquí como selección por barra, no como prueba de teclado sobre todas las marcas.
- Tooltips accesibles y etiquetas en árbol: inspeccionados en versiones previas de esta sesión; el tooltip observado mostraba etiqueta, número con separador español y unidad. La serie usa borde derecho alineado para el rótulo final `2025-12`; corrección presente en código.
- Las capturas se mostraron dentro de la sesión para revisar Story y Explore, pero la interfaz de captura disponible devolvió imágenes al inspector y no una ruta de archivo ni mecanismo de escritura al workspace. No se añadieron capturas al repositorio y el criterio de evidencia persistida queda abierto.

### Pruebas y preservación de datos
- `scripts/test_data_model.py`: 5 pruebas, PASS (0,004 s).
- `scripts/test_api.py`: 6 pruebas de integración, PASS (23,029 s); incluidos GET 200 de API/HTML/JS y 400 para dataset desconocido. Esto prueba API/servidor y no equivale a inspeccionar el panel Network del navegador.
- `node --check web/app.js`: PASS; `py_compile` para todos los `.py` de `scripts/`: PASS; `git diff --check`: PASS. Advertencias de Git sólo sobre normalización futura LF/CRLF, no errores de whitespace.
- Checksums actuales (SHA-256) cotejados con manifiesto: `siniestralidad_2019_2025.geojson` EE18CDE382F201A036EC668F7D92839F36D889685473AA7E81A8C194F6C42068; `mortalidad_2019_2024.geojson` 4B7C7319DB29ECC8FC177C8FB3399C1BD582E78029FDA99A62E86A6C0409468E; `limite_municipal.geojson` AD0769A044D5CCA1B4F0195394B8B90E7020359EEE2AF3EB27F7E445A4096A36. No se ejecutó adquisición, no se regeneró processed y no se escribió en `data/raw/`.
- Comandos: `node --check web/app.js`; script Python `py_compile` para todos los scripts; `python scripts/test_data_model.py`; `python scripts/test_api.py`; `git diff --check`; `Get-FileHash` para los tres raw indicados.

### Pendiente / estado real de aceptación
- Se superó la anotación anterior de Story bloqueado: Story renderizado y Explore renderizado se observaron manualmente en escritorio. README, informe y checklist reflejan esta actualización sin borrar la historia anterior.
- Seguimiento instrumental en el mismo navegador: selección con teclado verificada en una marca del mapa (grupo espacial aprox. `-75,70, 6,22`), punto temporal (`2019-01`) y celda de heatmap (lunes 0:00); cada selección actualizó el filtro compartido y `Restablecer` lo limpió. La navegación Story ↔ Explore también se ejerció. Esto cubre una marca por clase; no una prueba exhaustiva de todas las marcas/datos posibles.
- Consola: `dev.logs({levels:["error","warn"]})` sin entradas tras recarga local. Network/CDP con `Network.responseReceived` y `Network.loadingFailed`: no hubo fallos. HTML local 200, CSS y JS 304 por caché; `/api/boundary` 200 (~86 ms, 822.526 bytes), siniestralidad agregada 200 (~6,38 s, 19.947 bytes) y mortalidad 200 (~63 ms, 13.836 bytes). Se consultaron únicamente rutas locales; no se llamó a fuentes externas ni se re-adquirió raw. La demora de la agregación inicial queda como observación, sin presupuesto/objetivo de rendimiento para compararla.
- Responsive: emulación temporal 375×812 px por CDP comprobó `innerWidth=375`, ancho de documento/body 375 (sin overflow de página) y seis paneles visibles de ~330 px; gráficos de anchura fija se conservan en scroll interno. Se retiró el override temporal. Tablet y otros anchos no comprobados.
- Se observó código de foco y nombres accesibles, y se probó activación por teclado en tres marcas. No se realizó auditoría con lector de pantalla, medición automatizada WCAG/contraste, estados visuales forzados de carga/error/vacío ni rendimiento en equipos objetivo.
- Las capturas de Story y Explore se mostraron dentro de la sesión, pero el conector de inspección solo expuso la imagen al chat y no una ruta para persistir los bytes en el workspace. No se añadieron capturas a `reports/` ni al repo; ese criterio queda pendiente.
- Por tanto, QA visual e interacciones manuales de Story/Explore, filtro, barras, mapa, serie, heatmap, reset, navegación, teclado en muestras, responsive móvil y observación de consola/red: PASS en el alcance descrito. Pruebas automáticas de modelo/API/sintaxis: PASS. Accesibilidad ampliada, performance objetivo, otros viewports/estados y capturas persistidas: PENDIENTES. No declarar Definition of Done.

## Fase final de pulido visual, motion design y QA — 2026-11-03

### Cambios realizados

- Se conserva la aplicación nativa y su sistema editorial. Story escalona la entrada de capítulos y cifras; Explore anima la primera aparición de barras/marcas, cambios de ancho de barras y feedback de actualización. Los movimientos respetan `prefers-reduced-motion`.
- Se implementaron tooltips específicos con conteo `es-CO`, unidad y contexto de filtros para mapa, barras, serie temporal y heatmap. El mapa identifica celdas agrupadas de 0,01° sin exponer coordenadas individuales. Se eliminó el CSS residual del footer-note y el HTML no contiene el texto de instantánea solicitado para retirar.
- Se corrigió el tooltip que podía quedarse sobre el contenido al desplazar la página: ahora se oculta para hover y se reubica el asociado a foco. El tooltip también presenta transición breve, límite de viewport y acceso por foco; está disponible al tocar mediante pointerdown, pero no se pudo verificar con evento táctil real.
- No se alteró lógica analítica, datos procesados ni `data/raw/`. No hubo adquisiciones ni nuevas dependencias.

### Verificación ejecutada

- Navegador in-app recargado en `http://127.0.0.1:8000/#metodo`; el árbol accesible mostró Story completo y Método/fuentes, con cifras reales y formato legible (`235.820`, `1.541`, `La Candelaria 47.471`, `HERIDOS 170.751`). El footer visible solo conserva nombre y nota descriptiva; el texto de instantánea no está presente.
- Explore/tooltips/filtros/mapa/móvil/tablet/consola y red: detalles de pruebas de esta iteración y verificaciones heredadas se registran de forma diferenciada en `docs/TESTING.md`. Prueba previa del tooltip confirmó título, valor, unidad, contexto de filtros y ubicación dentro del viewport; tras el fix, el scroll ocultó el tooltip de puntero. La interacción táctil queda pendiente por limitación del navegador conectado.
- `prefers-reduced-motion` se verificó por emulación y restauración posterior. Viewports 375×812 y 768×1024 se habían medido sin overflow de página en la pasada manual vigente.
- Pruebas existentes de la pasada tras cambios de JS: `scripts/test_data_model.py` 5 OK, `scripts/test_api.py` 6 OK. En esta entrada se intentaron repetir ambas suites y `py_compile`, pero Windows solo resolvió el alias `C:\Users\Msi\AppData\Local\Microsoft\WindowsApps\python.exe`, que no pudo iniciarse (ResourceUnavailable). No se reporta repetición como PASS. `node --check web/app.js` y `git diff --check` sí pasaron.
- Capturas fueron observadas en el navegador, pero no guardadas: no se dispuso de una API/ruta de salida al filesystem desde esta herramienta. No se informan rutas de capturas inexistentes.
- Checksums recalculados de raw y coincidentes con el manifiesto: siniestralidad `EE18CDE382F201A036EC668F7D92839F36D889685473AA7E81A8C194F6C42068`, mortalidad `4B7C7319DB29ECC8FC177C8FB3399C1BD582E78029FDA99A62E86A6C0409468E`, límite municipal `AD0769A044D5CCA1B4F0195394B8B90E7020359EEE2AF3EB27F7E445A4096A36`. No se ejecutó código que escriba a `data/raw/`.

### Estado de aceptación

La nota de Story que antes impedía confirmar el render se considera superada por la inspección actual. No se declara Definition of Done: siguen abiertos capturas persistidas, prueba táctil, lector de pantalla/WCAG automatizada y contraste, estado de error/vacío forzado, recorrido completo repetido tras los cambios, y presupuesto/medición de rendimiento en equipos objetivo. Las limitaciones y los resultados parciales están en `docs/TESTING.md`; se deja abierta la checklist.

#### Intento de repetición de verificaciones — cierre 2026-11-03

- `scripts/test_data_model.py`, `scripts/test_api.py` y `python -m py_compile ...`: bloqueados al iniciar el alias `C:\Users\Msi\AppData\Local\Microsoft\WindowsApps\python.exe` (`ResourceUnavailable`, “El sistema no tiene acceso al archivo”). No se instaló nada ni se alteró el entorno. Los resultados PASS anteriores permanecen documentados con su fecha, pero no se atribuyen a esta repetición.
- `node --check web/app.js`: PASS. `git diff --check`: PASS (avisos LF→CRLF en archivos preexistentes, no errores de whitespace).
- SHA-256 de raw recalculados y coincidentes con el manifiesto: siniestralidad `EE18CDE382F201A036EC668F7D92839F36D889685473AA7E81A8C194F6C42068`; mortalidad `4B7C7319DB29ECC8FC177C8FB3399C1BD582E78029FDA99A62E86A6C0409468E`; límite municipal `AD0769A044D5CCA1B4F0195394B8B90E7020359EEE2AF3EB27F7E445A4096A36`.
- La checklist permanece abierta; este bloqueo de ejecución de Python es concreto y reproducible en el entorno actual, además de los criterios manuales pendientes ya descritos.

## Reanudación QA final — 2026-11-03

### Inspección y verificaciones realizadas

- Continuación desde la última entrada de QA; no se repitió adquisición, no se ejecutó el pipeline y no se modificó `data/raw/`.
- Se inspeccionaron la checklist, Testing, el log y el informe. Los criterios abiertos se mantienen; capturas de Story/Explore desktop ya existen y no habían quedado reflejadas correctamente en la documentación.
- Capturas existentes revisadas visualmente: `reports/screenshots/story-desktop.png` muestra Story con cifras reales legibles; `explore-desktop.png` muestra filtros y las seis vistas; `tooltip-example.png` muestra parte de Explore, pero ningún tooltip abierto. No se cuenta esa última como prueba de tooltip.
- Se intentó crear capturas de Método y Story móvil con Chrome headless contra el servidor local. El comando no creó archivos. No se registra PASS ni se reemplaza ninguna captura existente.
- `scripts/test_data_model.py`: PASS, 5 pruebas (0,004 s).
- `scripts/test_api.py`: ejecución normal BLOCKED por `WinError 10013` en socket local; repetición con permiso de loopback PASS, 7 pruebas OK en 36,297 s. Se ejercitaron respuestas 200 de datos, filtros día/hora, celda espacial, fuente de mortalidad, contenido estático y 400 para dataset desconocido.
- `node --check web/app.js`: PASS. `py_compile` de scripts/acquire.py, audit.py, prepare.py, eda.py, data_model.py, serve.py, test_api.py y test_data_model.py: PASS con Python 3.12.14 del runtime Codex. `git diff --check`: PASS; solo avisos de conversión LF/CRLF.
- Los hashes de tres archivos raw se cotejaron contra el manifiesto y coinciden: siniestralidad `EE18CDE382F201A036EC668F7D92839F36D889685473AA7E81A8C194F6C42068`; mortalidad `4B7C7319DB29ECC8FC177C8FB3399C1BD582E78029FDA99A62E86A6C0409468E`; límite municipal `AD0769A044D5CCA1B4F0195394B8B90E7020359EEE2AF3EB27F7E445A4096A36`.

### Criterios que permanecen abiertos

- Capturas Método, Explore móvil, tooltip abierto y estado vacío visible en la aplicación.
- Verificación repetida del recorrido Story → Explore → Método → Story → Explore en esta reanudación; estado vacío real y endpoint fueron comprobados anteriormente, pero no se logró capturarlos en UI ahora.
- Matriz responsive completa 1440×900, 1280×720, 768×1024, 390×844 y 375×812, estado de error visible en UI, lector de pantalla/WCAG/contraste, dispositivo táctil físico y prueba de rendimiento con equipos/umbral acordados.
- Por lo anterior, Definition of Done permanece OPEN. No se declaran como probados los criterios pendientes ni se atribuyen las capturas existentes a Método/móvil/tooltip/estado vacío.


## Elaboración del informe académico - 2026-11-04

- Se retomó la tarea de crear el informe académico original siguiendo What/Why/How. Se verificó el borrador existente, que resultó demasiado breve, y se amplió `docs/FINAL_REPORT.md` con problema y alcance, inventario/unidades de fuentes, calidad observada, tareas, justificación de las seis vistas, codificación e interacción, escenario de uso, resultados descriptivos, límites, reproducibilidad y referencias.
- Se analizaron los cuatro PDF de referencia ya entregados. Se adaptó su estructura común (overview, datasets, tareas, vistas/marcas/canales, interacciones, escenario y reflexión) sin trasladar datos, texto ni conclusiones de esos proyectos. La referencia a Munzner incluye su obra de 2014 y página oficial.
- Se incorporaron al documento recortes de las capturas existentes de Story y Explore, generados desde `reports/screenshots/story-desktop.png` y `explore-desktop.png`. Los originales no se modificaron. No se crearon capturas nuevas de la aplicación ni se atribuye evidencia a pantallas no verificadas.
- Se generó `reports/medellin_en_movimiento_informe_academico.pdf` con ReportLab y fuente Arial embebida. El primer render detectó mojibake en el borrador; se reparó la codificación UTF-8 del Markdown y se volvió a renderizar. La inspección visual final cubrió las nueve páginas y mostró acentos legibles, tablas ajustadas, dos imágenes reales, encabezados/pies y paginación.
- Verificación de artefacto: `pypdf` abrió el PDF (9 páginas; 2 imágenes); Poppler renderizó cada página a PNG para inspección. El texto extraído contiene las secciones What, Why, How, referencias y apéndice. No se ejecutaron pruebas de aplicación en esta tarea. El PDF informa explícitamente que el QA de producto conserva criterios abiertos y que su Definition of Done sigue OPEN.
- Se actualizaron los enlaces de documentación en `README.md`. No se volvió a adquirir ni procesar datos, ni se escribieron archivos en `data/raw/`. No se recalcularon hashes en esta tarea; los últimos hashes comprobados siguen registrados en las entradas QA previas.
- Pendiente editorial: completar nombres del equipo, curso/docente/sección y contribuciones/horas; confirmar licencias y unidad semántica de la capa de mortalidad con los publicadores antes de redistribución o de formular inferencias adicionales.

## Escala dinámica del heatmap — 2026-11-05

- Se agregó una barra vertical junto al heatmap de día/hora. Presenta mínimo y máximo `es-CO` del conjunto de 168 celdas para la fuente/filtros actuales, con el gradiente ajustado a esos mismos extremos. Incluye nombre accesible con mínimo/máximo y `aria-live="polite"`; actualiza al volver a renderizar las selecciones.
- Se actualizó `docs/VISUALIZATION_DESIGN.md`, `docs/TESTING.md` y la descripción de Explore en `README.md`.
- `node --check web/app.js`: PASS. `scripts/test_data_model.py`: PASS, 5/5. Un smoke check temporal con agregados del GeoJSON local llamó la función de render y verificó etiquetas, accesibilidad y actualización: selección completa mínimo 111/máximo 2.561; año 2019 mínimo 8/máximo 629. No se añadieron datos ficticios ni tests persistentes.
- Una primera invocación de la suite como `python -m unittest scripts.test_data_model` falló al importar `data_model` por ruta de módulo; se repitió con la instrucción documentada `python scripts/test_data_model.py` y pasó 5/5. No es un fallo del modelo.
- En la segunda aserción del smoke check temporal se esperaba inicialmente la etiqueta inglesa `minimum`; se corrigió la propia aserción a la etiqueta española `mínimo`, tras lo cual el chequeo completo pasó. No fue un defecto de la visualización.
- `git diff --check`: PASS. No se cambiaron API, agregaciones, análisis ni datos raw. La interfaz real en navegador quedó NOT TESTED en esta sesión: CUA no pudo inicializar sus assets del kernel y el acceso HTTP local recibió denegación de socket. No se afirma una verificación visual de navegador.
- El usuario pidió publicar los cambios en el remoto. El remoto `origin` está configurado en GitHub; aún no se había creado commit ni enviado un push al escribir esta entrada.

### Publicación en remoto — 2026-11-05

- Commit `fff4e16` (`Add academic report and dynamic heatmap scale`) publicado con `git push origin main`: PASS. El remoto avanzó de `12b2d02` a `fff4e16`.
- Se incluyeron README, bitácora, informe académico editable/PDF, Testing, diseño de visualización y los cambios de `web/app.js`/`web/styles.css`. No se incluyó `data/raw/` ni archivos temporales.
