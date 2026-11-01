---
name: geospatial-data-engineering
description: Procesa datos geoespaciales, GeoJSON, coordenadas, sistemas de referencia, clustering, hexbin y mapas interactivos.
---
# Geospatial Data Engineering

- Inspecciona CRS y unidades antes de transformar coordenadas.
- Distingue WGS84 lon/lat de coordenadas proyectadas.
- Comprueba latitud/longitud, geometrías vacías, inválidas y puntos fuera del área de estudio.
- Conserva coordenadas originales y registra cualquier reproyección.
- No calcula distancias en grados; reproyecta a CRS métrico apropiado.
- Usa clustering/hexbin para overview; puntos individuales solo a escalas adecuadas.
- Documenta método de agregación, tamaño de celda, zoom y denominador.
- No uses choropleth de conteos absolutos sin discutir población/exposición.
- Nunca infieras causalidad o riesgo a partir de densidad de puntos.
- Valida resultados espaciales con muestras y mapas de control.
