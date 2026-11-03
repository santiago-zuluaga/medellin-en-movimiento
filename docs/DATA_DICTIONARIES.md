# Diccionarios de datos

Las definiciones provienen de metadatos ArcGIS y diccionarios oficiales MEData descargados en `data/metadata/dictionaries/`. El diccionario no implica que el campo se incluya en el extracto procesable.

## Siniestralidad

| Campo | Definición/uso | Tipo | Notas |
|---|---|---|---|
| `objectid` | Identificador técnico de objeto ArcGIS | Entero | Único en el servicio observado; no identifica persona ni constituye clave de integración. |
| `fecha_siniestro`, `hora_siniestro` | Fecha y hora del siniestro reportado | Texto | Parsear y auditar formato/cobertura antes de agregar. |
| `dia`, `mes`, `anio` | Componentes temporales publicados | Texto/numérico | Verificar consistencia contra fecha. |
| `clase_siniestro` | Clase de siniestro | Categórico | Valores se validan desde el archivo adquirido. |
| `gravedad_siniestro` | Gravedad según fuente | Categórico | No equivale a gravedad de una víctima. |
| `barrio`, `num_comuna`, `nom_comuna` | Referencias administrativas | Categórico | Revisar valores faltantes/estandarización y cambios geográficos. |
| `latitud`, `longitud`, geometría | Coordenadas publicadas y punto espacial | Numérico/geométrico | Geometría de servicio original EPSG:9377; solicitado como EPSG:4326. |

## Mortalidad

El servicio define `fecha_ocurrencia`, `hora_ocurrencia`, `clase`, `nom_comuna`, `latitud`, `longitud`; el servicio también ofrece `id`, dirección, sexo y edad, excluidos del extracto por minimización. No se dispone de definición suficiente para afirmar si cada fila es una persona fallecida, un hecho o una consolidación administrativa.

## Diccionario MEData de víctimas

El diccionario descargado enumera 19 campos. Define `GRAVEDAD_VICTIMA`, `FECHA_INCIDENTE`, `HORA_INCIDENTE`, `CLASE_INCIDENTE`, `DIRECCION_INCIDENTE`, `SEXO`, `EDAD`, `CONDICION`, `GRUPO_EDAD`, `ANNO`, `LATITUD`, `LONGITUD`, `COMUNA`, `BARRIO`, entre otros. `RADICADO` se describe como consecutivo de expediente. El CSV no se adquirió ni se incorpora a la app por los campos identificadores/localizadores y la granularidad por víctima.

## Diccionario MEData de bicicleta

El diccionario descargado enumera 22 campos: `ESTACION`, `ID` (consecutivo por persona aforada), `FECHA`, `UBICACION`, `SENTIDO`, `COSTADO`, `SEXO`, `HORA`, `EDAD` agrupada, `BICICLETA`, `CASCO`, variables de calendario y coordenadas WGS84. Fechas, estaciones, horarios y atributos personales combinados pueden generar celdas pequeñas; no se adquirió el CSV individual.

## Diccionario consolidado

El archivo `data/metadata/data_dictionary.json` se genera durante la preparación y conserva nombres, tipos observados, nulidad y clasificación de unidad. Las definiciones oficiales originales están en `data/metadata/dictionaries/`.
