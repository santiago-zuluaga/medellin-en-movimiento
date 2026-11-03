# Plan de validación de datasets

## Estado inicial
La inspección documental en fuentes oficiales permite confirmar la existencia y los metadatos de varias fuentes. **Todavía no equivale a una validación empírica de los archivos completos**: faltan descarga, perfilado, comprobación de duplicados, nulos, formatos y cobertura efectiva.

## Inventario y decisión preliminar

| Fuente | Unidad de análisis | Cobertura publicada | Campos/atributos conocidos | Decisión |
|---|---|---|---|---|
| Capa geográfica de siniestralidad (Secretaría de Movilidad) | Evento de siniestralidad con heridos o solo daños | 2019–2025 | fecha_siniestro, hora_siniestro, dia, mes, anio, clase_siniestro, gravedad_siniestro, direccion, barrio, num_comuna, nom_comuna, latitud, longitud | Dataset núcleo |
| Capa geográfica de mortalidad | Registro de mortalidad vial | 2019–2024 | id, fecha_ocurrencia, hora_ocurrencia, fecha_levantamiento, dirección, clase, sexo_fallecido, edad_fallecido, comuna, latitud, longitud | Complemento separado |
| Víctimas en incidentes viales (MEData) | Víctima | Desde 2014; ficha actualizada 2025 | gravedad_victima, fecha/hora incidente, clase, sexo, edad, condición/actor vial, comuna, barrio, latitud/longitud, radicado | Complemento, no sumar como incidentes |
| Uso de bicicleta (MEData) | Persona ciclista observada en aforo | Metadato temporal desde 2018; actualizado 2025 | estación, fecha, ubicación, sentido, costado, sexo, hora, grupo edad, tipo bicicleta, casco, día/mes/año, latitud/longitud | Contexto exploratorio; no asumir representatividad ciudadana |
| Velocidad e intensidad (SIMM) | Medición en punto/cámara y momento | Según tablero/ficheros publicados | Debe inspeccionarse diccionario y ficheros por periodo | Fase posterior |
| Histórico Total Incidentes Tránsito 2015 (Geomedellín) | Registro histórico de incidente | Descripción indica 2014–2021 | Debe inspeccionarse archivo y diccionario | Solo para ampliar serie tras comparar metodología |

## Advertencias importantes
1. La capa de siniestralidad 2019–2025 describe expresamente heridos y solo daños; no sustituye a la capa de mortalidad.
2. La capa de mortalidad 2019–2024 advierte cambios metodológicos y cuatro registros identificados sin coordenadas. No eliminar silenciosamente esos registros.
3. El dataset de víctimas tiene una fila por víctima, por tanto varios registros pueden corresponder a un mismo incidente.
4. La fuente de bicicletas registra aforos en estaciones; la ficha describe una persona observada y hora de inicio de un cuarto de hora aforado. No extrapolar a toda la ciudad sin diseño muestral.
5. El histórico 2014–2021 se solapa con 2019–2021 con la capa nueva. Comparar definiciones, campos, duplicados y métodos antes de unir.
6. Los datos de velocidad/intensidad se recogen mediante dispositivos en puntos específicos; no representan automáticamente toda la red vial.

## Perfilado obligatorio
Para cada fichero:
- nombre, URL, fecha de descarga, fecha de actualización, licencia y responsable;
- número de filas/columnas y tipos;
- rango temporal real y fechas inválidas;
- nulos por campo;
- duplicados exactos y duplicados por clave candidata;
- cardinalidad de categorías;
- coordenadas fuera del área de estudio y registros sin geometría;
- valores imposibles/inconsistentes;
- distribución de registros por año/mes;
- reglas de limpieza reproducibles;
- checksum del archivo original.

## Reglas de integración
- No unir incidentes con víctimas por proximidad espacial solamente.
- Usar `radicado` u otra clave únicamente tras verificar semántica, unicidad y cobertura.
- Mantener tablas de incidentes y víctimas separadas; crear una relación uno-a-muchos si la clave es válida.
- Para fuentes sin clave compatible, comparar agregados por periodo y geografía, indicando que son comparaciones contextuales y no un join a nivel de registro.
- Documentar las diferencias de definiciones y metodología.

## Criterios para aprobar un dataset
- Descarga reproducible.
- Licencia/condiciones de uso identificadas.
- Diccionario disponible o campos documentados.
- Cobertura y unidad de análisis entendidas.
- Calidad espacial y temporal cuantificada.
- Solapamientos y cambios metodológicos documentados.
- Preguntas analíticas compatibles con los atributos.

## Ejecución empírica inicial — 2026-11-02

La ejecución actual descargó extractos minimizados y diccionarios con hashes en `reports/acquisition_manifest.json`. La adquisición de siniestralidad y mortalidad comprobó ObjectIDs solicitados/recibidos, consultó por páginas de 2.000 y solicitó EPSG:4326. Se añadieron el límite municipal oficial y los diccionarios MEData.

| Fuente local | Filas adquiridas | Periodo parseable | Duplicados por atributos excluyendo ObjectID | Calidad espacial | Decisión |
|---|---:|---|---:|---|---|
| Siniestralidad | 235.820 | 2019-01 a 2025-12; 0 fechas no parseables | 175 | 0 coordenadas inválidas; 0 discrepancias atributo/geometría; 7 fuera de la envolvente y 237 fuera del polígono municipal | PASS con WARN; conservar todo y revisar los duplicados/outliers. |
| Mortalidad | 1.541 | 2019-01 a 2024-12; 0 fechas no parseables | 33 | 4 geometrías/coordenadas faltantes; 0 discrepancias de coordenadas presentes; 4 puntos fuera del polígono municipal | WARN; unidad semántica por fila requiere confirmación; conservar registros. |
| Límite municipal | 1 geometría | N/A | 0 | EPSG:4326 solicitado; se usó como referencia espacial | PASS para contexto/QA. |

Los duplicados anteriores son firmas idénticas de atributos no técnicos, no registros que se hayan eliminado. ObjectID es único en ambos servicios, pero solo se considera clave técnica. La prueba punto-en-polígono usa el polígono oficial WGS84 y un índice de segmentos por latitud; se contrastó con el recorrido completo de vértices para 1.000 puntos de siniestralidad, con 0 discrepancias. No se removió ni transformó ningún punto.

MEData entregó ambos diccionarios (19 campos de víctimas y 22 de bicicleta). Los CSV individuales se excluyeron: víctima contiene consecutivo RADICADO y dirección exacta; bicicleta contiene ID de persona aforada junto a estación, hora y atributos demográficos.

El detalle de nulos, categorías, claves, hashes, límites y advertencias está en `reports/audit_report.md` y `.json`; agregados y conteos por año/mes están en `reports/eda_summary.md`, `reports/eda_*.svg` y `data/processed/eda_*.json`. Los estados WARN son abiertos y requieren resolución/documentación; no se deduplicaron filas automáticamente.
