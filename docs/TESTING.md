# Pruebas y verificación

## Comandos ejecutados

| Comando | Resultado |
|---|---|
| `scripts/audit.py` | Ejecutado con 3 archivos reales; genera auditoría JSON/Markdown. Datasets analíticos quedan WARN por duplicados potenciales, unidad de mortalidad y outliers; no se ocultan. |
| `scripts/prepare.py` | PASS para dos fuentes, 235.820 y 1.541 filas; agregado CSV por mes, comuna, categoría y redondeo espacial, con celdas espaciales <5 suprimidas. |
| `scripts/eda.py` | PASS para dos fuentes; tablas reproducibles y SVG de registros por año. |
| `scripts/test_data_model.py` | 5 pruebas unitarias OK: filtros, coherencia de totales, clase/gravedad separadas, día/hora, unidad separada de mortalidad. |
| `scripts/test_api.py` | 7 pruebas de integración OK con datos reales: cross-filter, filtros espaciales y día/hora, agregados requeridos por Explore y coherencia de totales, HTTP 400 para dataset desconocido y entrega HTML/JS. Requiere permiso de loopback. |
| `node --check web/app.js` | PASS; sintaxis JavaScript válida. |
| `python -m py_compile ...` | PASS para scripts del pipeline/app/pruebas. |
| `git diff --check` | PASS en la última verificación. |

## Qué cubren las pruebas

- Los filtros por año, comuna, clase, gravedad, día-hora y grupo espacial se aplican antes de agregar; los totales por mes/comuna/categoría/gravedad coinciden con filas filtradas.
- La API solo devuelve celdas con cinco o más filas y coordenadas redondeadas; no devuelve ObjectID/RADICADO.
- Mortalidad carece de filtro de gravedad porque el esquema del extracto no ofrece una gravedad comparable; los registros no se suman a siniestralidad.
- En desarrollo normal, `test_api.py` omite casos dependientes de archivos si no se ha ejecutado adquisición.

## QA manual de navegador — 2026-11-02

- Story se inspeccionó desde el hero hasta el capítulo de metodología y las fuentes; carga datos de la instantánea local. El formato corregido separa etiquetas y valores y representa conteos con separador de miles `es-CO`.
- Explore renderizó mapa agregado, barras por comuna/clase/gravedad, serie mensual y heatmap día-hora. El árbol accesible expone nombres/valores de sus marcas y filtros.
- Cambiar el año a 2022 fue visible en el control y alteró los agregados. Seleccionar La Candelaria desde la barra fijó el filtro compartido; las restantes vistas reflejaron la selección. `Restablecer` limpió año/comuna y volvió a las cifras agregadas.
- Vistas de Story y Explore fueron observadas mediante capturas de pantalla durante esta sesión; la interfaz de Computer Use mostró las imágenes, pero no ofreció una ruta de salida para guardarlas en `reports/` ni en el repositorio. Por ello el criterio de capturas persistidas sigue pendiente.
- `scripts/test_data_model.py`: 5 OK; `scripts/test_api.py`: 6 OK en 23,029 s. `node --check web/app.js`, `py_compile` de `scripts/*.py` y `git diff --check`: OK. Los hashes de los tres GeoJSON raw coinciden con el manifiesto; no se ejecutó adquisición ni se modificó `data/raw/`.
- Interacción ampliada con CDP/Playwright en navegador: una selección por teclado en mapa, serie y heatmap actualizó el filtro; reset lo limpió. Clic de mapa/serie/heatmap y barra de comuna también actualiza selección coordinada; año 2022 más comuna La Candelaria recalculó todas las vistas y reset restauró todo.
- A 375×812 px el documento y body quedaron en 375 px sin desbordamiento de página; seis paneles se midieron en ~330 px, con scroll local en gráficos que lo requieren. Se restauró el viewport al finalizar.
- Consola error/warn vacía. No se registró evento `Network.loadingFailed`; los recursos y API locales respondieron 200 o 304. Solicitud agregada inicial de siniestralidad: 200 en ~6,38 s (19.947 bytes); no se conoce un SLO del proyecto. La comprobación de red fue sobre esta recarga local, no sobre una auditoría de tráfico de terceros.

## Límites de verificación

- No hay compilador React/TypeScript ni bundle: se eligió una app nativa sin dependencias, de acuerdo con que no había stack existente y con el objetivo de ejecución reproducible sin instalación.
- No existe suite de navegador Playwright persistida en el repositorio; se usó el Playwright del navegador conectado para QA manual asistido. No se ejecutó axe ni otro escáner WCAG automatizado. Se verificaron foco, etiquetas y activación de tres tipos de marcas por teclado; queda pendiente lector de pantalla y evaluación WCAG/contraste.
- El QA anterior que no pudo confirmar Story se supera para la inspección manual actual de Story y el render de Explore. La verificación visual se realizó en el viewport de escritorio disponible.
- Pendiente: navegación completa/repetida Método↔Story↔Explore; tablet y más tamaños móviles; estados forzados de carga/error/vacío; lector de pantalla, auditoría WCAG/contraste automatizados; rendimiento en equipos objetivo y umbral acordado; capturas de Story y Explore guardadas como archivos. Las interacciones se probaron con muestras de marcas, no exhaustivamente para cada punto/celda.
- No hay presupuesto de latencia/FPS medido en diferentes equipos. El servidor mantiene los registros en memoria y re-agrega al filtrar; volumen actual: 235.820 filas de siniestralidad.

## Pulido visual, motion y QA — 2026-11-03

### Cambios revisados en navegador

- Story muestra capítulos con entrada escalonada y animación breve de cifras. Explore revela marcas/paneles en la primera carga y anima el ancho de barras al cambiar filtros; el feedback de actualización es visual y no bloquea los controles.
- Tooltips específicos en mapa agrupado, barras, puntos mensuales y celdas día-hora informan categoría/periodo, conteo `es-CO`, unidad y filtros aplicables. El mapa usa el rótulo de celda aproximada de 0,01°; el tooltip no muestra coordenadas ni identificadores.
- El listener de scroll oculta tooltips anclados al cursor para que no queden flotando sobre otra vista; los de foco conservan anclaje al elemento. Posicionamiento probado dentro del viewport en muestras observadas previamente.
- La recarga observada muestra Story completo con datos reales (235.820 registros de siniestralidad; 1.541 registros de la capa separada de mortalidad). Método y fuentes cargan. El texto “Instantánea descargada el 2 de noviembre de 2026…” no aparece en HTML/UI/footer; la información metodológica importante sigue en Método y documentación.
- La inspección previa de Explore verificó seis vistas, filtro combinado, selección coordinada en mapa/barras/serie/heatmap, reset y teclado para marcas de muestra. En esta iteración se inspeccionaron los nuevos tooltips de mapa y barra bajo filtros. No se repitió exhaustivamente cada combinación de filtro tras el pulido.
- Responsive medido previamente a 375×812 y 768×1024: sin overflow horizontal de página; los gráficos anchos mantienen desplazamiento local.
- Emulación `prefers-reduced-motion`: animaciones deshabilitadas y duración de transiciones reducida a 0,01 ms para cifras, barras, mapa, revelado y tooltip. Emulación restaurada después de la prueba.
- Consola error/warn vacía y sin `Network.loadingFailed` en la última recarga local observada. Recursos y agregados locales contestaron correctamente; no se evaluaron servicios externos.
- No se guardaron capturas como archivos. La herramienta permitió inspección visual en sesión, pero no una ruta de exportación al repositorio. La interacción táctil real tampoco pudo verificarse: el navegador conectado no admite despacho de eventos táctiles CDP; no se marca PASS por emulación de puntero.

### Verificaciones de código y datos

- `scripts/test_data_model.py`: 5 pruebas OK.
- `scripts/test_api.py`: 6 pruebas OK con datos locales (ejecución reportada en la pasada de QA anterior; esta iteración fue de CSS/JS visual y no cambió el modelo/API).
- `node --check web/app.js` y `git diff --check`: ejecutados en esta iteración, PASS. `python -m py_compile` y ambas suites se intentaron volver a ejecutar, pero el alias de WindowsApps no pudo iniciar Python; los PASS de suites son los de la pasada de QA anterior, no una repetición de esta fecha.
- No se ejecutó adquisición ni pipeline de transformación. `data/raw/` permanece sin modificaciones; los tres SHA-256 se recalcularon y coinciden con el manifiesto.

### Pendiente

Capturas persistidas; prueba táctil real; lector de pantalla y auditoría WCAG automatizada/contraste; estados de error y vacío forzados visualmente; recorrido completo repetido Story↔Explore↔Método; rendimiento/FPS y presupuesto acordado en equipos objetivo. La Definition of Done sigue abierta.

## Reanudación QA final — 2026-11-03

- **PASS actual:** `scripts/test_data_model.py` (5/5); `node --check web/app.js`; `py_compile` para los ocho scripts Python; `git diff --check`.
- **PASS actual:** `scripts/test_api.py` (7/7, 36,297 s) con permiso loopback. Una ejecución sin elevación falló en los siete casos por `WinError 10013`; no se cuenta como PASS.
- **PASS actual:** se inspeccionaron `reports/screenshots/story-desktop.png` y `explore-desktop.png`: PNG de la aplicación real, con Story completo y seis visualizaciones de Explore respectivamente. `tooltip-example.png` también es real, pero no presenta un tooltip visible y no cuenta como evidencia de tooltip.
- **PASS previo:** endpoint de estado vacío real `2019 · Aranjuez · ATROPELLO · DAÑOS` con cero filas; no se capturó esa condición en pantalla en esta reanudación. Navegación e interacciones coordinadas constan en la bitácora previa, sin repetición completa actual.
- **BLOCKED:** intento de capturas adicionales de Método/Story móvil con Chrome headless no produjo archivos nuevos.
- **NOT TESTED actual:** matriz de los cinco tamaños solicitados completa; Explore móvil; error API y vacío visibles en UI; navegación completa repetida; lector de pantalla/WCAG/contraste; dispositivo táctil real; rendimiento/FPS en dispositivos objetivo.
- Archivos de captura existentes: `story-desktop.png` (304.832 bytes), `explore-desktop.png` (503.430 bytes), `tooltip-example.png` (122.471 bytes). No se afirman capturas adicionales.
- `data/raw/` no se adquirió ni escribió. Hashes cotejados con el manifiesto: siniestralidad `EE18CDE382F201A036EC668F7D92839F36D889685473AA7E81A8C194F6C42068`, mortalidad `4B7C7319DB29ECC8FC177C8FB3399C1BD582E78029FDA99A62E86A6C0409468E`, límite municipal `AD0769A044D5CCA1B4F0195394B8B90E7020359EEE2AF3EB27F7E445A4096A36`.

## Escala dinámica del heatmap — 2026-11-05

- **PASS actual:** `node --check web/app.js` y `scripts/test_data_model.py` (5/5).
- **PASS actual:** un chequeo JavaScript temporal llamó la función de render con agregados de los datos locales reales. La escala reportó mínimo/máximo `111–2.561` para la fuente completa y `8–629` al filtrar 2019; verificó etiquetas visibles, nombre accesible y que el máximo cambiara con la selección. No se añadieron fixtures ni archivos de prueba persistentes.
- **PASS actual:** `git diff --check` (sin errores de whitespace; puede advertir conversión LF/CRLF de Windows).
- **NOT TESTED:** inspección de la interfaz en navegador, matriz móvil/tablet, lector de pantalla y actualización visual al manipular controles en pantalla. CUA no pudo inicializarse por error de ruta de assets del kernel; la consulta HTTP local falló por permiso de socket. El render de la función se comprobó en JavaScript, no como captura de navegador.
- La API y el modelo no cambiaron, por lo que no se repitió la suite API. El smoke check invocó directamente la función del heatmap con agregados del modelo y no verifica peticiones de red.
