# Informe de auditoría de datos

El estado WARN señala aspectos que requieren lectura metodológica; no equivale automáticamente a datos inválidos.

## limite_municipal.geojson — PASS

- Filas: 1 | columnas: 3
- Duplicados exactos excluyendo IDs técnicos: 0
- Claves candidatas completas y únicas: objectid
- Coberturas temporales parseables: {}
- Extensión de coordenadas WGS84: null
- Diferencias entre atributos y geometría > 1e-5°: 0
- Nulos por campo (%): `{"_coordinates": 0.0, "_geometry_type": 0.0, "objectid": 0.0}`

## mortalidad_2019_2024.geojson — WARN

- Filas: 1541 | columnas: 9
- Duplicados exactos excluyendo IDs técnicos: 33
- Claves candidatas completas y únicas: objectid
- Coberturas temporales parseables: {"fecha_ocurrencia": {"parseable": 1541, "unparseable_nonempty": 0, "minimum": "2019-01-01T00:00:00", "maximum": "2024-12-31T00:00:00"}}
- Extensión de coordenadas WGS84: {"longitude_min": -75.71755800985335, "longitude_max": -75.47562810011665, "latitude_min": 6.170341000561267, "latitude_max": 6.371369000542211}
- Puntos fuera de envolvente municipal: 0
- Puntos fuera del polígono municipal (pantalla simplificada): 4
- Diferencias entre atributos y geometría > 1e-5°: 0
- Nulos por campo (%): `{"_coordinates": 0.2596, "_geometry_type": 0.2596, "clase": 0.584, "fecha_ocurrencia": 0.0, "hora_ocurrencia": 0.0, "latitud": 0.2596, "longitud": 0.2596, "nom_comuna": 0.0, "objectid": 0.0}`
- Advertencia: 33 duplicados exactos
- Advertencia: La unidad exacta (persona fallecida/evento/registro) requiere definición oficial y validación
- Advertencia: 4 puntos fuera del límite municipal en prueba punto-en-polígono simplificada

## siniestralidad_2019_2025.geojson — WARN

- Filas: 235820 | columnas: 15
- Duplicados exactos excluyendo IDs técnicos: 175
- Claves candidatas completas y únicas: objectid
- Coberturas temporales parseables: {"fecha_siniestro": {"parseable": 235820, "unparseable_nonempty": 0, "minimum": "2019-01-01T00:00:00", "maximum": "2025-12-31T00:00:00"}}
- Extensión de coordenadas WGS84: {"longitude_min": -75.71373199062734, "longitude_max": -75.48130861991213, "latitude_min": 6.130034000572345, "latitude_max": 6.438240000038774}
- Puntos fuera de envolvente municipal: 7
- Puntos fuera del polígono municipal (pantalla simplificada): 237
- Diferencias entre atributos y geometría > 1e-5°: 0
- Nulos por campo (%): `{"_coordinates": 0.0, "_geometry_type": 0.0, "anio": 0.0, "barrio": 0.1001, "clase_siniestro": 0.0, "dia": 0.0, "fecha_siniestro": 0.0, "gravedad_siniestro": 0.0, "hora_siniestro": 0.0, "latitud": 0.0, "longitud": 0.0, "mes": 0.0, "nom_comuna": 0.0, "num_comuna": 0.109, "objectid": 0.0}`
- Advertencia: 175 duplicados exactos
- Advertencia: Conteos son eventos registrados; no expresan riesgo ni exposición
- Advertencia: 7 puntos fuera de la envolvente rectangular del límite municipal (no equivale a prueba punto-en-polígono)
- Advertencia: 237 puntos fuera del límite municipal en prueba punto-en-polígono simplificada
