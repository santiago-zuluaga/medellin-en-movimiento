# Fuentes de datos

Última consulta: 2026-11-02, America/Bogota. Las fechas de adquisición exactas están en `reports/acquisition_manifest.json`.

| Fuente | URL oficial | Unidad conocida | Periodo publicado | Licencia/uso | Decisión |
|---|---|---|---|---|---|
| Siniestralidad — Secretaría de Movilidad | [Capa ArcGIS VM_Accidentes](https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Accidentes/MapServer/0) | Fila de siniestralidad registrada; incluye registros HERIDOS y DAÑOS | 2019–2025 (metadatos) | Servicio público con crédito a Alcaldía/Secretaría/Observatorio; la capa consultada no expone una licencia abierta explícita. Verificar condiciones antes de redistribuir. | Fuente núcleo; extracto no identificable de fechas, clase/gravedad, comuna/barrio y coordenadas WGS84. Raw local ignorado por Git. |
| Mortalidad — Secretaría de Movilidad | [Capa ArcGIS VM_Mortalidad](https://www.medellin.gov.co/servidormapas/rest/services/transporte/VM_Mortalidad/MapServer/0) | Registro de la capa de mortalidad; no se ha demostrado que sea igual a persona fallecida o incidente | 2019–2024 (metadatos) | Servicio público; verificar licencia/condiciones de reutilización. | Complemento separado; se excluyeron ID, direcciones, sexo y edad de la descarga. No unir con siniestralidad. |
| Víctimas en incidentes viales — MEData | [Ficha y descargas](https://medata.app.medellin.gov.co/node/16692) | Víctima; ficha indica que procede de reportes de víctimas entregados por UNE | Desde 2014; ficha modificada 2025 | CC BY-SA 4.0, indicada en ficha | No se descargó el CSV individual. El diccionario confirma `RADICADO` como consecutivo de expediente y `DIRECCION_INCIDENTE`; se descargó solo el diccionario. |
| Caracterización/uso de bicicleta — MEData | [Ficha y descargas](https://medata.gov.co/node/16523) | Persona ciclista aforada en estación | Metadato desde 2018 | CC BY-SA 4.0, indicada en ficha | No se descargó el CSV individual. El diccionario confirma un ID por persona aforada y atributos demográficos junto a fecha/hora/estación, con riesgo de reidentificación por combinación. |
| Límite municipal — Alcaldía de Medellín | [Capa ArcGIS de límite municipal](https://www.medellin.gov.co/servidormapas/rest/services/mapas_nacionales/VC_Limite_Politico_Admtivo/MapServer/2) | Geometría administrativa municipal | Versión publicada por el servicio en fecha de adquisición | Crédito Alcaldía; licencia explícita pendiente | Contexto y control espacial; consultar CRS de origen y transformación anotados en manifiesto. |

## Esquema de extractos locales

`data/raw/siniestralidad_2019_2025.geojson`: `objectid`, `fecha_siniestro`, `hora_siniestro`, `dia`, `mes`, `anio`, `clase_siniestro`, `gravedad_siniestro`, `barrio`, `num_comuna`, `nom_comuna`, `latitud`, `longitud`, geometría solicitada en EPSG:4326. Se omitieron `radicado` y `direccion`.

`data/raw/mortalidad_2019_2024.geojson`: `objectid`, `fecha_ocurrencia`, `hora_ocurrencia`, `clase`, `nom_comuna`, `latitud`, `longitud`, geometría solicitada en EPSG:4326. Se omitieron `id`, direcciones, sexo y edad para reducir granularidad identificable.

`data/raw/limite_municipal.geojson`: geometría administrativa minimizada a ObjectID y geometría.

Los archivos bajo `data/raw/` son respuestas guardadas de extracciones de campos limitados, no copias completas de todos los atributos publicados por los portales. Son inmutables localmente y no se versionan en Git.
