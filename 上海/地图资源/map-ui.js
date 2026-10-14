(() => {
  const {data, views, places, prefix} = window.JOURNEY_MAP;
  const el = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const categories = {food:'吃', tea:'茶', shop:'逛'};
  const search = (name, location) => 'https://uri.amap.com/search?keyword=' + encodeURIComponent(name + ' ' + location) + '&city=' + encodeURIComponent('上海') + '&view=map';
  let current = Number(new URLSearchParams(location.search).get('day')) || window.JOURNEY_MAP.initial;
  let map, routes, placeLayer, offline, online, currentPins = [];

  if (typeof L !== 'undefined') {
    map = L.map('map', {zoomSnap:.25});
    routes = L.layerGroup().addTo(map);
    placeLayer = L.layerGroup().addTo(map);
    L.control.scale({imperial:false}).addTo(map);
    online = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.jpg',
      {maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'});
  }
  const embedded = new URLSearchParams(location.search).get('embed') === '1';
  if (embedded) {
    document.body.classList.add('embedded');
    const reportHeight = () => {
      if (matchMedia('(max-width:800px)').matches)
        parent.postMessage({journeyMapHeight:Math.ceil(document.body.scrollHeight)}, location.origin);
    };
    new ResizeObserver(reportHeight).observe(document.body);
    addEventListener('load', reportHeight);
    addEventListener('resize', reportHeight);
  }

  function routeList(view) {
    if (view.id === 0 || view.id === 9) {
      const days = data.days.filter(d => view.id === 0 || d.id >= 2 && d.id <= 5);
      el('list').innerHTML = days.map(d => '<li><a href="#" data-day="' + d.id + '">D' + d.id + ' · ' + esc(d.title) + '</a></li>').join('');
      return;
    }
    const route = [...new Set(view.description.route)];
    el('list').innerHTML = route.map(k => {
      const p = data.points[k];
      const url = p.coordinate_source.includes('amap.com/place') ? p.coordinate_source : search(p.name, '');
      return '<li><a target="_blank" rel="noopener" href="' + esc(url) + '">' + esc(p.name) + '</a><br><span class="muted">' + esc(p.tip) + '</span></li>';
    }).join('');
  }

  function drawPlaces(view) {
    const selected = new Set([...document.querySelectorAll('[data-kind]:checked')].map(input => input.dataset.kind));
    currentPins = places.filter(p => (view.id === 9 ? p.days.some(d => d >= 2 && d <= 5) : p.days.includes(view.id)) && selected.has(p.kind));
    el('place-count').textContent = '· ' + currentPins.length + '处候选';
    el('places-panel').hidden = currentPins.length === 0;
    el('places-list').innerHTML = currentPins.map((p, i) =>
      '<li><button type="button" data-poi="' + i + '"><span class="key ' + p.kind + '">' + categories[p.kind] + '</span> ' +
      esc(p.name) + '<small>' + esc(p.location) + (p.approximate ? ' · 街区位置' : '') + '</small></button></li>').join('');
    if (!map) return;
    placeLayer.clearLayers();
    currentPins.forEach((p, i) => {
      const marker = L.marker([p.lat,p.lon], {icon:L.divIcon({
        className:'', html:'<div class="category-pin ' + p.kind + (p.approximate ? ' approx' : '') + '">' + categories[p.kind] + '</div>',
        iconSize:[28,28], iconAnchor:[14,14]})});
      marker.bindPopup('<b>' + esc(p.name) + '</b><br>' + esc(p.location) + '<br>' + esc(p.tip) +
        (p.approximate ? '<br><b>街区位置，非店门口</b>' : '<br>地图POI近似转换；入口按导航') +
        '<br><a target="_blank" rel="noopener" href="' + esc(search(p.name,p.location)) + '">高德搜索门店</a>' +
        ' · <a target="_blank" rel="noopener" href="' + esc(p.source) + '">位置来源</a>');
      marker.addTo(placeLayer);
      p.marker = marker;
    });
  }

  function routeMarker(point, index, optional, color) {
    const html = current > 0 && current < 9
      ? '<div class="route-pin' + (optional ? ' optional' : '') + '" style="' + (optional ? '' : 'background:' + color) + '">D' + current + '<b>' + index + '</b></div>'
      : '<div class="overview-pin">' + ['D1','住','D6','D7','D8'][index-1] + '</div>';
    return L.marker([point.lat,point.lon], {icon:L.divIcon({className:'',html,iconSize:[42,38],iconAnchor:[21,19]})})
      .bindTooltip(point.name,{direction:'top',className:'map-caption'})
      .bindPopup('<b>' + esc(point.name) + '</b><br>' + esc(point.tip) + '<br><small>' + esc(point.coordinate_status) + '</small><br><a target="_blank" rel="noopener" href="' + esc(search(point.name,'')) + '">高德搜索</a>');
  }

  function draw(viewId) {
    current = viewId;
    const view = views.find(v => v.id === viewId), day = view.description;
    el('day-select').value = viewId >= 1 && viewId <= 8 ? String(viewId) : '';
    document.querySelectorAll('[data-view]').forEach(b => b.classList.toggle('active', Number(b.dataset.view) === viewId));
    el('title').textContent = day ? 'D' + viewId + ' · ' + view.title : view.title;
    el('pace').textContent = day ? day.pace : viewId === 9 ? 'D2–D5分街区走，每天只选一片。' : '选择日期，查看当天路线与顺路吃逛。';
    el('mode').textContent = day ? day.mode : '虚线只表示游玩顺序，跨区乘车；A/B为待选住宿区域。';
    el('meal').textContent = day ? '吃逛建议：' + day.meal : '';
    el('optional').textContent = day?.optional?.length ? '可选替换：' + day.optional.map(k => data.points[k].name).join('；') : '';
    el('source').innerHTML = day ? day.source.map(code => '<a target="_blank" rel="noopener" href="' + esc(data.sources[code]) + '">' + code + '</a>').join('') : '地图与地点取舍见首页研究依据。';
    el('static').href = prefix + view.static;
    el('fallback').src = prefix + view.static;
    routeList(view);
    if (map) {
      routes.clearLayers();
      if (offline) map.removeLayer(offline);
      offline = L.imageOverlay(prefix + view.background, view.bounds, {attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
      if (el('online').checked) online.bringToFront();
      view.routes.forEach((line, i) => {
        L.polyline(line.route.map(k => [data.points[k].lat,data.points[k].lon]),
          {color:line.color,weight:4,dashArray:'8 6',opacity:.88}).addTo(routes);
        if (viewId === 9 || viewId === 0) {
          const d = viewId === 9 ? i + 2 : [1,6,7,8][i];
          if (viewId === 9) {
            const p = data.points[line.route[1]];
            L.marker([p.lat,p.lon], {icon:L.divIcon({className:'',html:'<div class="day-label">D' + d + '</div>',iconSize:[36,26],iconAnchor:[18,13]})}).addTo(routes);
          }
        }
      });
      const keys = viewId === 0 ? ['sha','hotel','b','disney','pvg'] : viewId === 9 ? [] : view.keys;
      const main = new Set(view.routes.flatMap(r => r.route));
      keys.forEach((k, i) => routeMarker(data.points[k], i + 1,
        !main.has(k), viewId >= 1 && viewId <= 8 ? data.colors[viewId-1] : '#0f766e').addTo(routes));
      map.fitBounds(view.bounds,{padding:[12,12]});
      requestAnimationFrame(() => map.invalidateSize());
    } else {
      el('fallback').style.display = 'block';
    }
    drawPlaces(view);
  }

  el('buttons').innerHTML = [[0,'全程'],[9,'市区 D2–D5'],[10,'园内']].map(([id,title]) =>
    '<button type="button" data-view="' + id + '">' + title + '</button>').join('');
  el('buttons').addEventListener('click',event => {
    const button = event.target.closest('[data-view]');
    if (button) draw(Number(button.dataset.view));
  });
  el('day-select').addEventListener('change',event => {if (event.target.value) draw(Number(event.target.value));});
  el('list').addEventListener('click',event => {
    const link = event.target.closest('[data-day]');
    if (link) {event.preventDefault();draw(Number(link.dataset.day));}
  });
  el('places-list').addEventListener('click',event => {
    const button = event.target.closest('[data-poi]');
    if (!button) return;
    const item = currentPins[Number(button.dataset.poi)];
    if (map) {map.setView([item.lat,item.lon],Math.max(map.getZoom(),15));item.marker.openPopup();}
  });
  document.querySelectorAll('[data-kind]').forEach(input => input.addEventListener('change',() => drawPlaces(views.find(v => v.id === current))));
  el('online').addEventListener('change',event => {if (map) event.target.checked ? online.addTo(map) : map.removeLayer(online);});
  draw(current);
})();
