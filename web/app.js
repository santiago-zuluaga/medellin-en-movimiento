const filters = { dataset: 'incidents', year: '', community: '', category: '', severity: '', hour: '', weekday: '', cell: '' };
const controls = Object.fromEntries(['dataset', 'year', 'community', 'category', 'severity'].map((id) => [id, document.getElementById(id)]));
const jsonCache = new Map();
let boundary = null;
let storyRendered = false;
let exploreRequestId = 0;
let revealObserver = null;
let tooltipHideTimer = null;
const fmt = new Intl.NumberFormat('es-CO', { useGrouping: true, maximumFractionDigits: 0 });
const percentFmt = new Intl.NumberFormat('es-CO', { style: 'percent', maximumFractionDigits: 1 });
const coordinateFmt = new Intl.NumberFormat('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const esc = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const endpoint = (path, params = {}) => `${path}?${new URLSearchParams(params)}`;

async function fetchJSON(url) {
  const parsedUrl = new URL(url, window.location.href);
  parsedUrl.searchParams.sort();
  for (const [key, value] of [...parsedUrl.searchParams]) if (!value) parsedUrl.searchParams.delete(key);
  const cacheKey = `${parsedUrl.pathname}?${parsedUrl.searchParams}`;
  if (jsonCache.has(cacheKey)) return jsonCache.get(cacheKey);
  const request = (async () => {
    const response = await fetch(url);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Error HTTP ${response.status}`);
    return data;
  })();
  jsonCache.set(cacheKey, request);
  try {
    return await request;
  } catch (error) {
    jsonCache.delete(cacheKey);
    throw error;
  }
}

function chartShell(title, unit, content, className = '') {
  return `<article class="chart-panel reveal ${className}"><div class="chart-head"><div><p class="eyebrow">Exploración coordinada</p><h3>${title}</h3></div><span class="unit-tag">${unit}</span></div>${content}</article>`;
}

function barChart(entries, aria, keyName, selectedKey, unit) {
  const data = entries.slice().sort((a, b) => b[1] - a[1]);
  if (!data.length) return '<p class="empty">No hay registros para esta selección.</p>';
  const max = Math.max(...data.map((d) => d[1]), 1);
  const bars = data.map(([label, value]) => {
    const selected = filters[selectedKey] === label;
    return `<button type="button" class="bar-row${selected ? ' is-selected' : ''}" aria-label="Filtrar ${esc(keyName)}: ${esc(label)}, ${fmt.format(value)} ${esc(unit)}" aria-pressed="${selected}" data-filter="${selectedKey}" data-value="${esc(label)}" data-viz-title="${esc(label)}" data-viz-value="${fmt.format(value)}" data-viz-unit="${esc(unit)}" aria-describedby="viz-tooltip"><span class="bar-label">${esc(label)}</span><span class="bar-track" aria-hidden="true"><span class="bar-fill" style="--bar-width:${(value / max * 100).toFixed(2)}%"></span></span><strong class="bar-value">${fmt.format(value)}</strong></button>`;
  }).join('');
  return `<div class="bar-chart" role="group" aria-label="${aria}">${bars}</div><p class="caption">Barras ordenadas por número de registros. Selecciona una barra para filtrar todas las vistas.</p>`;
}

function timeChart(data, unit) {
  const coverage = data.coverage_months || Object.keys(data.months || {});
  let domain = coverage;
  if (filters.year) domain = domain.filter((month) => month.startsWith(filters.year));
  const entries = domain.map((month) => [month, data.months[month] || 0]);
  if (!entries.length) return '<p class="empty">No hay meses con cobertura registrada.</p>';
  const width = 760, height = 250, left = 52, top = 15, bottom = 45, plotH = height - top - bottom, plotW = width - left - 15;
  const max = Math.max(...entries.map(([, count]) => count), 1), step = plotW / Math.max(entries.length - 1, 1);
  const coordinates = entries.map(([, count], index) => [left + index * step, top + plotH - count / max * plotH]);
  const monthIndex = (label) => { const [year, month] = label.split('-').map(Number); return year * 12 + month; };
  const segments = entries.slice(1).map(([month], index) => monthIndex(month) - monthIndex(entries[index][0]) === 1 ? `<line x1="${coordinates[index][0]}" y1="${coordinates[index][1]}" x2="${coordinates[index + 1][0]}" y2="${coordinates[index + 1][1]}" stroke="#b9492f" stroke-width="2.5"/>` : '').join('');
  const labelIndices = new Set([0, Math.floor((entries.length - 1) / 3), Math.floor(2 * (entries.length - 1) / 3), entries.length - 1]);
  const labels = entries.map(([month], index) => {
    if (!labelIndices.has(index)) return '';
    const first = index === 0;
    const last = index === entries.length - 1;
    const x = first ? left : last ? width - 5 : left + index * step;
    const anchor = first ? 'start' : last ? 'end' : 'middle';
    return `<text x="${x}" y="${height - 12}" text-anchor="${anchor}">${esc(month)}</text>`;
  }).join('');
  const pointsMarks = entries.map(([month, count], index) => {
    const selected = filters.year === month.slice(0, 4);
    return `<circle class="time-point${selected ? ' is-selected' : ''}" cx="${left + index * step}" cy="${top + plotH - count / max * plotH}" r="${selected ? 6 : 4}" fill="#b9492f" tabindex="0" role="button" aria-pressed="${selected}" aria-label="${esc(month)}, ${fmt.format(count)} ${esc(unit)}" data-filter="year" data-value="${month.slice(0, 4)}" data-viz-title="${esc(month)}" data-viz-value="${fmt.format(count)}" data-viz-unit="${esc(unit)}" aria-describedby="viz-tooltip"></circle>`;
  }).join('');
  const grid = [0, .5, 1].map((ratio) => `<line class="grid" x1="${left}" x2="${width - 15}" y1="${top + plotH * ratio}" y2="${top + plotH * ratio}"/><text x="${left - 8}" y="${top + plotH * ratio + 4}" text-anchor="end">${fmt.format(Math.round(max * (1 - ratio)))}</text>`).join('');
  return `<div class="chart-scroll" tabindex="0" role="region" aria-label="Serie mensual desplazable"><svg class="chart-svg time-chart" viewBox="0 0 ${width} ${height}" role="group" aria-label="Registros por mes; serie temporal descriptiva"><title>Registros por mes</title>${grid}${segments}${pointsMarks}${labels}</svg></div><p class="caption">Meses sin registros para los filtros activos aparecen como cero solo cuando la fuente tuvo al menos un registro ese mes. La serie muestra filas registradas, sin normalizar por exposición; la ausencia total de registros no prueba que no ocurrieran siniestros.</p>`;
}

function weekdayHeatmap(data, unit) {
  const counts = new Map(data.weekday_hours.map((d) => [`${d.weekday}-${d.hour}`, d.count]));
  const max = Math.max(...counts.values(), 1), days = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom'];
  const x0 = 58, y0 = 20, cellW = 24, cellH = 27;
  const fullDays = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  const cells = days.map((day, d) => `<text x="${x0 - 8}" y="${y0 + d * cellH + 16}" text-anchor="end">${day}</text>${Array.from({ length: 24 }, (_, hour) => {
    const count = counts.get(`${d}-${hour}`) || 0, alpha = count ? .15 + .8 * count / max : .04;
    const selected = filters.weekday === String(d) && filters.hour === String(hour);
    return `<rect class="cell heat-cell${selected ? ' is-selected' : ''}" x="${x0 + hour * cellW}" y="${y0 + d * cellH}" width="${cellW - 2}" height="${cellH - 2}" rx="2" fill="rgba(185,73,47,${alpha})" tabindex="0" role="button" aria-pressed="${selected}" aria-label="Filtrar ${fullDays[d]}, ${hour}:00; ${fmt.format(count)} ${esc(unit)}" data-filter="weekday_hour" data-value="${d}-${hour}" data-viz-title="${fullDays[d]}, ${String(hour).padStart(2, '0')}:00" data-viz-value="${fmt.format(count)}" data-viz-unit="${esc(unit)}" aria-describedby="viz-tooltip"></rect>`;
  }).join('')}`).join('');
  const hourLabels = Array.from({ length: 24 }, (_, h) => h % 3 === 0 ? `<text x="${x0 + h * cellW + 10}" y="${y0 + 7 * cellH + 15}" text-anchor="middle">${h}</text>` : '').join('');
  return `<div class="chart-scroll heatmap-scroll" tabindex="0" role="region" aria-label="Heatmap desplazable por día y hora"><svg class="chart-svg heatmap-svg" viewBox="0 0 660 250" role="group" aria-label="Heatmap de registros por día de semana y hora"><title>Día de semana por hora</title>${cells}${hourLabels}</svg></div><p class="chart-legend">Escala de color: 0 registros (sin relleno) a ${fmt.format(max)} registros (tono más intenso).</p><p class="caption">Color más intenso indica mayor conteo en esta selección; las horas sin registro se conservan como celdas vacías. Usa Tab y Enter para filtrar por día y hora.</p>`;
}

function flattenRings(coords, result = []) {
  if (!Array.isArray(coords)) return result;
  if (coords.length >= 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') result.push(coords);
  else coords.forEach((part) => flattenRings(part, result));
  return result;
}

function geometryRings(geometry, result = []) {
  if (!geometry) return result;
  if (geometry.type === 'Polygon') result.push(...geometry.coordinates);
  if (geometry.type === 'MultiPolygon') geometry.coordinates.forEach((poly) => result.push(...poly));
  return result;
}

function mapChart(data, unit) {
  const rings = (boundary?.features || []).flatMap((feature) => geometryRings(feature.geometry));
  const all = [
    ...rings.flat(),
    ...data.cells.map((cell) => [cell.longitude, cell.latitude]),
  ];
  if (!data.cells.length) return '<p class="empty">No hay suficientes grupos espaciales para dibujar el mapa.</p>';
  const xs = all.map((p) => p[0]), ys = all.map((p) => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const w = 700, h = 440, pad = 28;
  const px = (x) => pad + (x - minX) / (maxX - minX || 1) * (w - 2 * pad);
  const py = (y) => h - pad - (y - minY) / (maxY - minY || 1) * (h - 2 * pad);
  const outlines = rings.map((ring) => `<path class="map-outline" d="${ring.map(([x,y], index) => `${index ? 'L' : 'M'}${px(x).toFixed(1)},${py(y).toFixed(1)}`).join(' ')} Z"/>`).join('');
  const max = Math.max(...data.cells.map((cell) => cell.count), 1);
  const cells = data.cells.map((cell) => {
    const radius = 2 + Math.sqrt(cell.count / max) * 12;
    const cellKey = `${cell.longitude.toFixed(2)},${cell.latitude.toFixed(2)}`;
    const selected = filters.cell === cellKey;
    return `<circle class="cell map-cell${selected ? ' is-selected' : ''}" cx="${px(cell.longitude)}" cy="${py(cell.latitude)}" r="${radius}" fill="#b9492f" fill-opacity=".75" stroke="#fbf9f3" stroke-width="1" tabindex="0" role="button" aria-pressed="${selected}" aria-label="Grupo espacial aproximado, ${fmt.format(cell.count)} ${esc(unit)}" data-filter="cell" data-value="${cellKey}" data-viz-title="Grupo espacial aproximado · celda de 0,01°" data-viz-value="${fmt.format(cell.count)}" data-viz-unit="${esc(unit)}" aria-describedby="viz-tooltip"></circle>`;
  }).join('');
  return `<div class="map-wrap"><svg class="chart-svg map-svg" viewBox="0 0 ${w} ${h}" role="group" aria-label="Grupos de registros sobre el límite municipal de Medellín">${outlines}${cells}</svg></div><p class="chart-legend">Cada círculo resume registros cuyas coordenadas se redondean a la misma celda de 0,01°. El área crece con el conteo de ${esc(unit)}. Las celdas con menos de 5 registros se suprimen. El centro representa un grupo aproximado, no la ubicación exacta de registros; los conteos no expresan riesgo.</p>`;
}

function attachSelectionHandlers() {
  document.querySelectorAll('[data-filter]').forEach((node) => {
    const activate = () => {
      const name = node.dataset.filter;
      if (name === 'cell') {
        filters.cell = filters.cell === node.dataset.value ? '' : node.dataset.value;
      } else if (name === 'weekday_hour') {
        const [weekday, hour] = node.dataset.value.split('-');
        const same = filters.weekday === weekday && filters.hour === hour;
        filters.weekday = same ? '' : weekday;
        filters.hour = same ? '' : hour;
      } else {
        filters[name] = filters[name] === node.dataset.value ? '' : node.dataset.value;
        if (name === 'year') filters.cell = '';
      }
      render();
    };
    node.addEventListener('click', activate);
    if (node.tagName.toLowerCase() !== 'button') {
      node.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); } });
    }
  });
}

function observeRevealElements() {
  const elements = document.querySelectorAll('.reveal:not(.is-visible)');
  if (!('IntersectionObserver' in window)) {
    elements.forEach((element) => element.classList.add('is-visible'));
    return;
  }
  if (!revealObserver) {
    revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
  }
  elements.forEach((element) => revealObserver.observe(element));
}

function setupTooltips() {
  const tooltip = document.getElementById('viz-tooltip');
  const title = tooltip.querySelector('[data-tooltip-title]');
  const value = tooltip.querySelector('[data-tooltip-value]');
  const unit = tooltip.querySelector('[data-tooltip-unit]');
  const context = tooltip.querySelector('[data-tooltip-context]');
  let activeElement = null;
  let pointerPosition = null;

  const filterContext = (excludedFilter) => {
    const active = [];
    if (excludedFilter !== 'dataset') active.push(`Fuente: ${filters.dataset === 'incidents' ? 'Siniestros registrados' : 'Registros de mortalidad'}`);
    if (filters.year && excludedFilter !== 'year') active.push(`Año: ${filters.year}`);
    if (filters.community && excludedFilter !== 'community') active.push(`Comuna: ${filters.community}`);
    if (filters.category && excludedFilter !== 'category') active.push(`Clase: ${filters.category}`);
    if (filters.severity && excludedFilter !== 'severity') active.push(`Gravedad: ${filters.severity}`);
    if (filters.hour !== '' && excludedFilter !== 'weekday_hour') active.push(`Día y hora: ${['lunes','martes','miércoles','jueves','viernes','sábado','domingo'][Number(filters.weekday)]}, ${filters.hour}:00`);
    if (filters.cell && excludedFilter !== 'cell') active.push('Grupo espacial aproximado seleccionado');
    return active.length ? `Filtros activos · ${active.join(' · ')}` : 'Sin otros filtros activos';
  };

  const place = (x, y) => {
    const gap = 14;
    const bounds = tooltip.getBoundingClientRect();
    let left = x + gap;
    let top = y + gap;
    if (left + bounds.width > window.innerWidth - 8) left = x - bounds.width - gap;
    if (top + bounds.height > window.innerHeight - 8) top = y - bounds.height - gap;
    tooltip.style.left = `${Math.max(8, Math.min(left, window.innerWidth - bounds.width - 8))}px`;
    tooltip.style.top = `${Math.max(8, Math.min(top, window.innerHeight - bounds.height - 8))}px`;
  };
  const show = (element, x, y) => {
    if (!element?.dataset.vizTitle) return;
    activeElement = element;
    title.textContent = element.dataset.vizTitle;
    value.textContent = element.dataset.vizValue || '';
    unit.textContent = element.dataset.vizUnit || '';
    context.textContent = filterContext(element.dataset.filter);
    tooltip.setAttribute('aria-hidden', 'false');
    tooltip.classList.add('is-visible');
    place(x, y);
  };
  const hide = () => {
    clearTimeout(tooltipHideTimer);
    activeElement = null;
    pointerPosition = null;
    tooltip.classList.remove('is-visible');
    tooltip.setAttribute('aria-hidden', 'true');
  };
  const datumElement = (target) => target instanceof Element ? target.closest('[data-viz-title]') : null;

  document.addEventListener('pointerover', (event) => {
    if (event.pointerType === 'touch') return;
    const element = datumElement(event.target);
    if (element) {
      pointerPosition = { x: event.clientX, y: event.clientY };
      show(element, pointerPosition.x, pointerPosition.y);
    }
  });
  document.addEventListener('pointermove', (event) => {
    if (activeElement && event.pointerType !== 'touch') {
      pointerPosition = { x: event.clientX, y: event.clientY };
      place(pointerPosition.x, pointerPosition.y);
    }
  });
  document.addEventListener('pointerout', (event) => {
    if (event.pointerType === 'touch') return;
    const element = datumElement(event.target);
    if (element && (!event.relatedTarget || !element.contains(event.relatedTarget))) hide();
  });
  document.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'touch') return;
    const element = datumElement(event.target);
    if (!element) return;
    clearTimeout(tooltipHideTimer);
    pointerPosition = { x: event.clientX, y: event.clientY };
    show(element, event.clientX, event.clientY);
    tooltipHideTimer = setTimeout(hide, 2800);
  }, { passive: true });
  document.addEventListener('focusin', (event) => {
    const element = datumElement(event.target);
    if (!element) return;
    const rect = element.getBoundingClientRect();
    pointerPosition = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    show(element, pointerPosition.x, pointerPosition.y);
  });
  document.addEventListener('focusout', (event) => {
    if (datumElement(event.target)) hide();
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') hide(); });
  window.addEventListener('resize', () => {
    if (activeElement && pointerPosition) place(pointerPosition.x, pointerPosition.y);
  });
  document.addEventListener('scroll', () => {
    if (!activeElement) return;
    if (document.activeElement !== activeElement) {
      hide();
      return;
    }
    const rect = activeElement.getBoundingClientRect();
    place(rect.left + rect.width / 2, rect.top + rect.height / 2);
  }, { capture: true, passive: true });
}

function updateOptions(data) {
  const previous = { ...filters };
  const setOptions = (control, values, allLabel) => {
    const options = Object.keys(values).sort((a,b) => a.localeCompare(b, 'es'));
    control.innerHTML = `<option value="">${allLabel}</option>${options.map((value) => `<option value="${esc(value)}">${esc(value)}</option>`).join('')}`;
    control.value = options.includes(previous[control.id]) ? previous[control.id] : '';
    filters[control.id === 'year' ? 'year' : control.id] = control.value;
  };
  setOptions(controls.year, data.years, 'Todos');
  setOptions(controls.community, data.communities, 'Todas');
  setOptions(controls.category, data.categories, 'Todas');
  setOptions(controls.severity, data.severities, 'Todas');
  controls.severity.disabled = filters.dataset === 'mortality';
  controls.severity.setAttribute('aria-label', filters.dataset === 'mortality' ? 'Gravedad no disponible para esta fuente' : 'Gravedad');
}

function filterParams() {
  return { dataset: filters.dataset, year: filters.year, community: filters.community, category: filters.category, severity: filters.severity, hour: filters.hour, weekday: filters.weekday, cell: filters.cell || '' };
}

function updateActiveState() {
  const labels = [];
  if (filters.year) labels.push(`año ${filters.year}`);
  if (filters.community) labels.push(filters.community);
  if (filters.category) labels.push(filters.category);
  if (filters.severity) labels.push(filters.severity);
  if (filters.hour !== '') labels.push(`${['lunes','martes','miércoles','jueves','viernes','sábado','domingo'][Number(filters.weekday)]}, ${filters.hour}:00`);
  if (filters.cell) labels.push(`grupo ${filters.cell.split(',').map((coordinate) => coordinateFmt.format(Number(coordinate))).join(', ')}`);
  document.getElementById('active-state').textContent = labels.length ? `Filtros activos: ${labels.join(' · ')}` : 'Sin filtros activos';
}

async function renderExplore() {
  const requestId = ++exploreRequestId;
  const target = document.getElementById('explore-content');
  const hasCharts = Boolean(target.querySelector('.chart-panel'));
  const previousDataset = target.dataset.dataset;
  const previousBarWidths = new Map([...target.querySelectorAll('.bar-row')].map((row) => {
    const fill = row.querySelector('.bar-fill');
    return [`${previousDataset}:${row.dataset.filter}:${row.dataset.value}`, fill?.style.getPropertyValue('--bar-width') || ''];
  }));
  if (hasCharts) target.classList.remove('is-entering');
  target.setAttribute('aria-busy', 'true');
  target.classList.add('is-updating');
  if (!hasCharts) target.innerHTML = '<p class="loading" role="status">Cargando las vistas de Explore…</p>';
  try {
    const data = await fetchJSON(endpoint('/api/data', filterParams()));
    if (requestId !== exploreRequestId) return;
    updateOptions(data);
    const unit = filters.dataset === 'incidents' ? 'filas de siniestralidad' : 'filas de mortalidad';
    const categories = Object.entries(data.categories).sort((a,b) => b[1] - a[1]);
    target.innerHTML = `
      <article class="chart-panel reveal map-panel wide"><div class="chart-head"><div><p class="eyebrow">Ubicación agregada</p><h3>La geografía de los registros</h3></div><span class="unit-tag">${unit}</span></div>${mapChart(data, unit)}</article>
      ${chartShell('Comuna', unit, barChart(Object.entries(data.communities), 'Registros por comuna', 'comuna', 'community', unit), 'community-panel wide')}
      ${chartShell('Clase de siniestro', unit, barChart(categories, 'Registros por clase', 'clase', 'category', unit))}
      ${chartShell(filters.dataset === 'incidents' ? 'Gravedad del registro' : 'Gravedad', unit, Object.keys(data.severities).length ? barChart(Object.entries(data.severities), 'Registros por gravedad', 'gravedad', 'severity', unit) : '<p class="empty">Esta capa no contiene un campo de gravedad compatible.</p>')}
      ${chartShell('El tiempo, mes a mes', unit, timeChart(data, unit), 'wide')}
      ${chartShell('Día y hora', unit, weekdayHeatmap(data, unit), 'wide')}
      <p class="source-note wide">Fuente: ${filters.dataset === 'incidents' ? 'Secretaría de Movilidad, capa Siniestralidad (2019–2025).' : 'Secretaría de Movilidad, capa Mortalidad (2019–2024).'} El total representa ${unit}. No se mezclan unidades entre fuentes.</p>`;
    target.dataset.dataset = filters.dataset;
    if (hasCharts && previousDataset === filters.dataset) {
      target.querySelectorAll('.bar-row').forEach((row) => {
        const fill = row.querySelector('.bar-fill');
        const key = `${filters.dataset}:${row.dataset.filter}:${row.dataset.value}`;
        const previousWidth = previousBarWidths.get(key);
        const nextWidth = fill?.style.getPropertyValue('--bar-width');
        if (!fill || !previousWidth || !nextWidth || previousWidth === nextWidth) return;
        fill.style.transition = 'none';
        fill.style.setProperty('--bar-width', previousWidth);
        fill.getBoundingClientRect();
        fill.style.removeProperty('transition');
        window.requestAnimationFrame(() => {
          if (fill.isConnected) fill.style.setProperty('--bar-width', nextWidth);
        });
      });
    }
    if (hasCharts) target.querySelectorAll('.reveal').forEach((element) => element.classList.add('is-visible'));
    else target.classList.add('is-entering');
    attachSelectionHandlers();
    updateActiveState();
    observeRevealElements();
  } catch (error) {
    if (requestId === exploreRequestId) target.innerHTML = `<p class="error wide" role="alert">No se pudieron cargar los datos: ${esc(error.message)}. Revisa que el servidor local y los datos estén disponibles.</p>`;
  } finally {
    if (requestId === exploreRequestId) {
      target.setAttribute('aria-busy', 'false');
      target.classList.remove('is-updating');
      if (!hasCharts) window.setTimeout(() => target.classList.remove('is-entering'), 360);
      updateActiveState();
    }
  }
}

async function renderStory() {
  if (storyRendered) return;
  const target = document.getElementById('story-content');
  try {
    const incidents = await fetchJSON('/api/data?dataset=incidents');
    const deaths = await fetchJSON('/api/data?dataset=mortality');
    const severity = Object.entries(incidents.severities).sort((a,b) => b[1] - a[1]);
    const communities = Object.entries(incidents.communities).sort((a,b) => b[1] - a[1]).slice(0, 3);
    const years = Object.entries(incidents.years).sort((a,b) => a[0].localeCompare(b[0]));
    const share = severity.map(([name, count]) => `<li><span class="story-label">${esc(name)} <small>${percentFmt.format(count / incidents.records)}</small></span><strong class="story-value">${fmt.format(count)}</strong></li>`).join('');
    const yearList = years.map(([year, count]) => `<li><span class="story-label">${esc(year)}</span><strong class="story-value">${fmt.format(count)}</strong></li>`).join('');
    const communityList = communities.map(([name, count]) => `<li><span class="story-label">${esc(name)}</span><strong class="story-value">${fmt.format(count)}</strong></li>`).join('');
    target.innerHTML = `
      <article class="story-card reveal"><p class="eyebrow">La fuente principal</p><div class="big-number">${fmt.format(incidents.records)}</div><p class="metric-label">registros de siniestralidad, 2019–2025</p><p>La capa distingue registros con heridos y solo daños. La cifra resume filas de la fuente; no cuenta víctimas ni mide exposición vial.</p></article>
      <article class="story-card reveal"><p class="eyebrow">Una unidad distinta</p><div class="big-number">${fmt.format(deaths.records)}</div><p class="metric-label">registros en la capa de mortalidad, 2019–2024</p><p>Se presenta aparte: sus reglas de consolidación y su equivalencia con personas fallecidas o hechos requieren confirmación del Observatorio.</p></article>
      <article class="story-card reveal"><p class="eyebrow">Composición de la capa principal</p><h3>Dos categorías publicadas</h3><ul>${share}</ul><p>Porcentajes calculados sobre las filas descargadas de esta capa. No se mezclan con la tabla por víctimas.</p></article>
      <article class="story-card reveal"><p class="eyebrow">Geografía descriptiva</p><h3>Registros por comuna</h3><ul>${communityList}</ul><p>Los conteos dependen de dónde se reporta y geocodifica cada hecho. No indican que una comuna tenga mayor riesgo.</p></article>
      <article class="story-card wide reveal"><p class="eyebrow">Tiempo y comparabilidad</p><h3>La serie cubre siete años de registros</h3><ul>${yearList}</ul><p>Las diferencias entre años son descriptivas. La fuente se actualiza y puede sufrir ajustes; sin una evaluación de completitud y cambios de captura, no se atribuye una tendencia a causas ni se interpreta como cambio de riesgo.</p><button class="reset" type="button" id="story-explore">Explorar con filtros compartidos →</button></article>
      <article class="story-card wide reveal"><p class="eyebrow">Nota de método</p><h3>Una pregunta, varias capas; ninguna suma automática</h3><p>Las fuentes de víctimas y bicicleta se dejaron fuera de esta aplicación: sus CSV contienen identificadores/localización fina o filas por persona aforada combinadas con atributos temporales y demográficos. El producto no expone esos registros individuales.</p><p>Fuentes, esquemas, checksums, auditoría y decisiones están en la documentación del proyecto.</p></article>`;
    document.getElementById('story-explore').addEventListener('click', () => setView('explore'));
    observeRevealElements();
    storyRendered = true;
  } catch (error) {
    target.innerHTML = `<p class="error" role="alert">No se pudieron leer las fuentes locales: ${esc(error.message)}. La narrativa permanece vacía hasta que estén disponibles los datos reales.</p>`;
  }
}

async function render() {
  controls.dataset.value = filters.dataset;
  await Promise.all([renderExplore(), renderStory()]);
}

function setView(view) {
  document.querySelectorAll('.nav-button').forEach((button) => button.classList.toggle('active', button.dataset.view === view));
  document.getElementById('story-view').classList.toggle('hidden', view !== 'story');
  document.getElementById('explore-view').classList.toggle('hidden', view !== 'explore');
  if (view === 'explore') document.getElementById('explore-view').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.querySelectorAll('.nav-button').forEach((button) => button.addEventListener('click', () => setView(button.dataset.view)));
Object.entries(controls).forEach(([key, control]) => control.addEventListener('change', () => {
  filters[key] = control.value;
  filters.cell = '';
  if (key === 'dataset') { filters.year = ''; filters.community = ''; filters.category = ''; filters.severity = ''; filters.hour = ''; filters.weekday = ''; }
  render();
}));
document.getElementById('reset').addEventListener('click', () => {
  filters.year = filters.community = filters.category = filters.severity = '';
  filters.hour = '';
  filters.weekday = '';
  filters.cell = '';
  render();
});
setupTooltips();
observeRevealElements();
// Charts and narrative do not depend on the municipal outline. Render them as
// soon as the app starts, then redraw the map when its optional boundary loads.
render();
fetchJSON('/api/boundary').then((value) => { boundary = value; render(); }).catch(() => { boundary = null; });
