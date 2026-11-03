# Protocolo de auditoría

1. Registrar URL, organismo, licencia indicada, fechas de consulta/descarga y checksum SHA-256 en `reports/acquisition_manifest.json`.
2. Mantener cada unidad por separado: evento de siniestralidad, registro de mortalidad, víctima, persona aforada y medición vehicular.
3. Verificar esquema actual antes de consultar. Solicitar solo campos analíticos; excluir identificadores personales, radicados y direcciones exactas.
4. Para ArcGIS: obtener la lista de ObjectIDs, paginar según `maxRecordCount`, registrar CRS de origen/solicitado y comprobar igualdad de conjuntos de IDs.
5. Auditar por archivo filas, columnas, tipos, faltantes, claves candidatas, duplicados excluyendo IDs técnicos, categorías, parseabilidad temporal, geometrías y consistencia atributo/geometría.
6. Comparar coordenadas contra límite administrativo oficial cuando esté disponible. La prueba de envolvente rectangular es preliminar y no sustituye punto-en-polígono.
7. No unir fuentes por proximidad; `radicado` no está disponible en los extractos. No calcular tasas sin denominadores de exposición compatibles.
8. Cada regla de transformación debe ser reproducible, idempotente y acompañada del número de filas/celdas afectadas.
9. Los registros menores al umbral de privacidad no se exponen como puntos o celdas; todo agregado conserva su unidad y base de conteo.
10. Clasificar PASS/WARN/FAIL con razón. Un resultado WARN requiere evaluación humana documentada; no se interpreta como “datos correctos”.
