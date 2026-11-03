# Medellín en movimiento

## 1. Información básica

Proyecto académico de Visualización de Información y Data Storytelling. Instantánea de datos adquirida el 2 de noviembre de 2026. Equipo/horas/curso: **PENDIENTE DE COMPLETAR POR EL EQUIPO**; no se infieren nombres ni tiempos.

## 2. Overview

El proyecto explora cómo se distribuyen espacial, temporal y categóricamente los registros oficiales de siniestralidad vial de Medellín. La audiencia incluye ciudadanía, estudiantes, periodistas de datos y personas interesadas en seguridad vial. La app separa una lectura guiada (**Story**) de una exploración con filtros coordinados (**Explore**).

El alcance es descriptivo. La posición o densidad de un registro no mide por sí sola riesgo, y la visualización no atribuye causas. Las capas y unidades se mantienen separadas.

## 3. Datos

### Fuentes y unidades

| Fuente | Unidad | Cobertura de la instantánea | Filas adquiridas | Licencia / límite |
|---|---|---|---:|---|
| Capa ArcGIS Siniestralidad, Secretaría de Movilidad | Fila de evento registrado con categoría HERIDOS o DAÑOS | 2019-01 a 2025-12 | 235.820 | Metadatos identifican copyright institucional, no una licencia abierta explícita; confirmar antes de redistribuir. |
| Capa ArcGIS Mortalidad, Secretaría de Movilidad | Fila de la capa de mortalidad; equivalencia semántica de fila a persona fallecida/evento por confirmar | 2019-01 a 2024-12 | 1.541 | Servicio actualizable; consolidación técnica puede cambiar. Licencia no explícita en metadatos consultados. |
| MEData víctimas | Víctima individual | Ficha desde 2014 | No descargada | CC BY-SA 4.0 indicado en ficha; CSV se excluyó por RADICADO y dirección exacta. |
| MEData bicicleta | Persona ciclista aforada en estación | Ficha desde 2018 | No descargada | CC BY-SA 4.0 indicado en ficha; CSV excluido por ID de persona y combinación estación/hora/atributos. |

Los endpoints, diccionarios, campos, hashes y condiciones están en `DATA_SOURCES.md`, `DATA_DICTIONARIES.md` y `reports/acquisition_manifest.json`. Las extracciones ArcGIS solicitaron solo atributos analíticos y coordenadas; se omitieron ID/radicado, direcciones, sexo y edad. Los raw no se versionan en Git.

### Calidad observada

- Siniestralidad: fechas parseables 100%; nulos de barrio 0,10%, número de comuna 0,109%; ObjectID único; 175 firmas repetidas en atributos analíticos excluyendo ObjectID. Se conservan sin deduplicar.
- Mortalidad: fechas parseables 100%; geometría/latitud/longitud ausente en 4 de 1.541 filas (0,26%); clase ausente en 9 (0,58%); ObjectID único; 33 firmas repetidas excluyendo ObjectID. Se conservan sin deduplicar.
- Los atributos latitud/longitud de coordenadas presentes coinciden con geometría GeoJSON en la tolerancia auditada. Se detectaron 237 puntos de siniestralidad y 4 de mortalidad fuera del polígono administrativo, además de 7 siniestralidad fuera de la envolvente rectangular. No se eliminaron ni corrigieron.
- La comprobación poligonal emplea la geometría municipal oficial transformada a WGS84; un índice espacial se comparó en 1.000 puntos con el algoritmo de recorrido completo (cero discrepancias).

## 4. Tareas analíticas

- Localizar registros agrupados en contexto municipal.
- Comparar conteos brutos de registros por comuna, clase y gravedad publicada.
- Resumir ritmos por mes y por día de semana/hora.
- Cambiar filtros y comparar vistas de la misma fuente seleccionada.
- Leer mortalidad separada, con una etiqueta que conserva la incertidumbre de la unidad.

## 5. Visualizaciones

- **Mapa agregado:** límite municipal + círculos, área proporcional al conteo en celdas por redondeo 0,01°; omite celdas <5. No es hexbin, métrica de área igual ni estimación de riesgo.
- **Serie mensual:** segmentos/puntos con mes en X y filas en Y; los filtros muestran meses con cobertura observada y cortan brechas.
- **Barras:** longitud = conteo de filas por comuna, clase o gravedad.
- **Heatmap:** posición X hora, Y día, tono terracota = conteo; la celda tiene tooltip, etiqueta y activación por teclado.

El fundamento de marcas, canales, Gestalt, escalas e interacciones está en `VISUALIZATION_DESIGN.md` y `GESTALT_RATIONALE.md`.

## 6. Escenario de uso

Una persona abre Story, lee el total por fuente y su unidad, observa composición y cobertura con cautelas. En Explore selecciona un año, una comuna o una barra, y después una celda día-hora; mapa, serie y gráficos se recalculan con el mismo filtro. Puede restablecer la selección. Al cambiar a mortalidad, la gravedad se desactiva y se conserva la fuente separada.

## 7. Reflexiones, resultados y límites

La instantánea contiene 235.820 filas de siniestralidad: 170.751 con HERIDOS (72,4%) y 65.069 con DAÑOS (27,6%). La mayor categoría geográfica por conteo es La Candelaria, con 47.471 filas. Estos resultados son conteos de los registros adquiridos, no denominadores de exposición ni riesgos comparables.

La distribución anual observada fue: 2019 46.551; 2020 31.755; 2021 40.655; 2022 38.642; 2023 24.957; 2024 23.041; 2025 30.219. La capa se actualiza continuamente y pueden cambiar cobertura/captura/clasificación; no se interpreta esta secuencia como efecto de una política, tendencia causal ni cambio del riesgo.

QA final reanudado el 3 de noviembre de 2026. Las capturas reales existentes `reports/screenshots/story-desktop.png` y `explore-desktop.png` fueron inspeccionadas: Story muestra cifras legibles con formato español; Explore presenta seis vistas. `tooltip-example.png` no muestra un tooltip abierto y no acredita ese criterio. La suite de modelo pasó 5/5, la API 7/7 con loopback autorizado, JS y compilación Python pasaron; `git diff --check` pasó. Se cotejaron los SHA-256 de los tres archivos de `data/raw/` contra el manifiesto, sin adquisición ni cambios. La combinación real `2019 · Aranjuez · ATROPELLO · DAÑOS` devolvió cero filas en API en una verificación previa, pero no se capturó visualmente como estado vacío en esta reanudación. La creación headless de capturas de Método/móvil no generó archivos. DoD sigue OPEN: faltan evidencia Método/móvil/tooltip/vacío, repetición del flujo completo, matriz responsive completa, estado de error visible, auditoría con lector de pantalla/WCAG/contraste, tacto físico y rendimiento acordado en equipo objetivo. No se declara conformidad WCAG ni soporte táctil completo. El alcance detallado está en `TESTING.md` y `EXECUTION_LOG.md`.

La capa de mortalidad tiene 1.541 filas por separado, pero no se presenta como número de víctimas mortales hasta confirmar unidad y metodología. Los microdatos de víctimas y bicicleta quedan fuera por privacidad. Los conteos repetidos y outliers están documentados; no se aplicó deduplicación ni imputación.

## 8. Trabajo y calendario

Se documentan fases, decisiones y comandos en `EXECUTION_LOG.md`; contribución y horas reales quedan pendientes del equipo. No se inventan estimaciones ni reparto de personas.

## 9. Créditos

- Secretaría de Movilidad y Observatorio de Movilidad de Medellín: capas oficiales ArcGIS de siniestralidad, mortalidad y límite municipal.
- MEData: diccionarios de víctimas y caracterización del uso de bicicleta.
- La aplicación y pipeline fueron implementados en este proyecto con Python estándar, HTML, CSS, JavaScript y SVG nativos. No hay dependencias frontend de terceros.
- Citar las páginas/fichas indicadas en `DATA_SOURCES.md`; verificar condiciones ArcGIS antes de redistribución.

## 10. Reproducibilidad

Seguir pasos en `README.md`; los informes producidos se encuentran en `reports/`. Las celdas espaciales redondeadas, no los registros individuales, son lo único que la API de la app devuelve para el mapa.
