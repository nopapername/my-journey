(() => {
  const {data, views, places, prefix, version} = window.JOURNEY_MAP;
  const {viewForViewport, dayName} = window.JourneyMapContext;
  const el = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const categories = {food:'吃', tea:'茶', shop:'逛'};
  const parkLabels = {disney:'入口', tron:'极速', mine:'矿车', hot:'热力', pirate:'海盗', soar:'飞越', rapids:'漂流', peter:'小飞', rex:'抱龙', castle:'城堡', storm:'剧场', buzz:'巴斯'};
  const search = (name, location) => 'https://uri.amap.com/search?keyword=' + encodeURIComponent(name + ' ' + location) + '&city=' + encodeURIComponent('上海') + '&view=map';
  let current = Number(new URLSearchParams(location.search).get('day')) || window.JOURNEY_MAP.initial;
  const requestedParkVariant = new URLSearchParams(location.search).get('variant');
  let parkVariant = ['tron','mine','hot'].includes(requestedParkVariant) ? requestedParkVariant : 'tron';
  let map, routes, placeLayer, baseOffline, detailOffline, online, currentPins = [], suppressAuto = false;
  const selectedView = id => views.find(v => v.id === (id === 10 ? {tron:10,mine:11,hot:12}[parkVariant] : id));

  if (typeof L !== 'undefined') {
    map = L.map('map', {zoomSnap:.25,inertia:false});
    routes = L.layerGroup().addTo(map);
    placeLayer = L.layerGroup().addTo(map);
    L.control.scale({imperial:false}).addTo(map);
    const complete = views.find(v => v.id === 0);
    baseOffline = L.imageOverlay(prefix + complete.background + '?v=' + version,
      complete.bounds, {pane:'tilePane',attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
    online = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
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
      el('list').innerHTML = days.map(d => '<li><a href="#" data-day="' + d.id + '">' + dayName(d.id) + ' · ' + esc(d.date) + ' · ' + esc(d.title) + '</a></li>').join('');
      return;
    }
    const route = [...new Set(view.description.route)];
    el('list').innerHTML = route.map(k => {
      const p = data.points[k];
      const url = p.coordinate_source.includes('amap.com/place') ? p.coordinate_source : search(p.name, '');
      return '<li><a target="_blank" rel="noopener" href="' + esc(url) + '">' + esc(p.name) + '</a><br><span class="muted">' + esc(p.tip) + '</span></li>';
    }).join('');
  }

  function updatePlaces(view) {
    const selected = new Set([...document.querySelectorAll('[data-kind]:checked')].map(input => input.dataset.kind));
    currentPins = places.filter(p => (view.id === 9 ? p.days.some(d => d >= 2 && d <= 5 || d === 9) : p.days.includes(view.id)) && selected.has(p.kind));
    el('place-count').textContent = '· ' + currentPins.length + '处候选';
    el('places-panel').hidden = currentPins.length === 0;
    el('places-list').innerHTML = currentPins.map((p, i) =>
      '<li><button type="button" data-poi="' + i + '"><span class="key ' + p.kind + '">' + categories[p.kind] + '</span> ' +
      esc(p.name) + '<small>' + esc(p.location) + (p.approximate ? ' · 街区位置' : '') + '</small></button></li>').join('');
  }

  // Labels may move a few screen pixels in dense streets. The short leader line
  // still ends at the mapped coordinate; the route itself never moves.
  function labelLayout(view) {
    const occupied = [], size = map.getSize(), margin = 8;
    const northwest = map.latLngToContainerPoint([view.bounds[1][0],view.bounds[0][1]]);
    const southeast = map.latLngToContainerPoint([view.bounds[0][0],view.bounds[1][1]]);
    const limits = {left:Math.max(margin,northwest.x+4),top:Math.max(margin,northwest.y+4),
      right:Math.min(size.x-margin,southeast.x-4),bottom:Math.min(size.y-margin,southeast.y-4)};
    return (lat, lon, width, height) => {
      const anchor = map.latLngToContainerPoint([lat, lon]);
      const step = Math.max(width, height) + 7;
      const offsets = [];
      for (let gx = -4; gx <= 4; gx++) for (let gy = -4; gy <= 4; gy++)
        offsets.push([gx*step,gy*step]);
      offsets.sort((a,b) => Math.hypot(...a)-Math.hypot(...b));
      let choice, lowest = Infinity;
      for (const [dx,dy] of offsets) {
        const x = anchor.x + dx, y = anchor.y + dy;
        const rect = {left:x-width/2-4,right:x+width/2+4,top:y-height/2-4,bottom:y+height/2+4};
        const overlap = occupied.reduce((sum, other) => sum +
          Math.max(0,Math.min(rect.right,other.right)-Math.max(rect.left,other.left)) *
          Math.max(0,Math.min(rect.bottom,other.bottom)-Math.max(rect.top,other.top)),0);
        const edge = Math.max(0,limits.left-rect.left)+Math.max(0,rect.right-limits.right)+
          Math.max(0,limits.top-rect.top)+Math.max(0,rect.bottom-limits.bottom);
        const score = overlap * 10000 + edge * 1000 + Math.hypot(dx,dy);
        if (score < lowest) {lowest=score;choice={x,y,rect,shifted:dx!==0||dy!==0};}
        if (overlap === 0 && edge === 0) break;
      }
      occupied.push(choice.rect);
      return {position:map.containerPointToLatLng([choice.x,choice.y]),shifted:choice.shifted};
    };
  }

  function leader(group, actual, placed, color) {
    if (placed.shifted) L.polyline([actual,placed.position],
      {color,weight:1.5,opacity:.82,interactive:false}).addTo(group);
  }

  function routeMarker(point, index, optional, color, placed, lodging = false) {
    const html = lodging ? '<div class="lodging-pin">住 · 海友</div>' : current > 0 && current < 9
      ? '<div class="route-pin' + (optional ? ' optional' : '') + '" style="' + (optional ? '' : 'background:' + color) + '">D' + current + '<b>' + index + '</b></div>'
      : '<div class="overview-pin' + (current === 0 && index === 2 ? ' city-base' : '') + (current === 10 && optional ? ' park-optional' : '') + '">' + (current === 10
        ? (optional || point.id === 'disney' || point.id === 'castle' ? '' : index - 1) + parkLabels[point.id]
        : ['D1','D2–5','D6','D7'][index-1]) + '</div>';
    const dims = lodging ? [72,30] : current > 0 && current < 9 ? [42,38]
      : current === 0 && index === 2 ? [50,28] : [36,28];
    return L.marker(placed.position, {zIndexOffset:1000,icon:L.divIcon({className:'',html,iconSize:dims,iconAnchor:[dims[0]/2,dims[1]/2]})})
      .bindTooltip(point.name,{direction:'top',className:'map-caption'})
      .bindPopup('<b>' + esc(point.name) + '</b><br>' + esc(point.tip) + '<br><small>' + esc(point.coordinate_status) + '</small>' +
        (placed.shifted ? '<br>编号略作偏移，细线指向景点位置。' : '') +
        '<br><a target="_blank" rel="noopener" href="' + esc(search(point.name,'')) + '">高德搜索</a>');
  }

  function groupedPins() {
    if (!matchMedia('(max-width:520px)').matches)
      return currentPins.map(p => [p]);
    const groups = [];
    currentPins.forEach(p => {
      const point = map.latLngToContainerPoint([p.lat,p.lon]);
      const near = groups.find(group => group[0].kind === p.kind && group.some(q => {
        const other = map.latLngToContainerPoint([q.lat,q.lon]);
        return point.distanceTo(other) < 46;
      }));
      if (near) near.push(p); else groups.push([p]);
    });
    return groups;
  }

  function singlePlacePopup(p) {
    return '<b>' + esc(p.name) + '</b><br>' + esc(p.location) + '<br>' + esc(p.tip) +
      (p.approximate ? '<br><b>街区位置，非店门口</b>' : '<br>地图POI近似转换；入口按导航') +
      '<br><a target="_blank" rel="noopener" href="' + esc(search(p.name,p.location)) + '">高德搜索门店</a>' +
      ' · <a target="_blank" rel="noopener" href="' + esc(p.source) + '">位置来源</a>';
  }

  function renderMarkers(view) {
    if (!map) return;
    routes.clearLayers();
    placeLayer.clearLayers();
    const place = labelLayout(view);
    view.routes.forEach(line => L.polyline(line.route.map(k => [data.points[k].lat,data.points[k].lon]),
      {color:line.color,weight:4,dashArray:'8 6',opacity:.88}).addTo(routes));
    if (view.id === 9) view.routes.forEach((line,i) => {
      const p = data.points[line.route[0]], placed = place(p.lat,p.lon,36,26);
      leader(routes,[p.lat,p.lon],placed,line.color);
      L.marker(placed.position,{zIndexOffset:1000,icon:L.divIcon({className:'',
        html:'<div class="day-label">D'+(i+2)+'</div>',iconSize:[36,26],iconAnchor:[18,13]})}).addTo(routes);
    });
    const keys = view.id === 0 ? ['sha','hotel','b','disney'] : view.id === 8 ? ['b'] : view.id === 9 ? ['hotel'] : view.keys;
    const main = new Set(view.routes.flatMap(r => r.route));
    keys.forEach((key,i) => {
      const lodging = key === 'hotel';
      const p = data.points[key], dims = lodging ? [72,30]
        : view.id === 0 ? [36,28] : [42,38];
      const placed = place(p.lat,p.lon,...dims), color = view.id >= 1 && view.id <= 8 ? data.colors[view.id-1] : '#0f766e';
      leader(routes,[p.lat,p.lon],placed,lodging ? '#64748b' : color);
      const ordinal = view.id >= 1 && view.id <= 5 ? keys.slice(0,i+1).filter(item => item !== 'hotel').length : i+1;
      routeMarker(p,lodging ? 0 : ordinal,
        !main.has(key),color,placed,lodging).addTo(routes);
    });
    groupedPins().forEach(group => {
      const p = group[0], count = group.length;
      const actual = [group.reduce((sum,item) => sum+item.lat,0)/count,
        group.reduce((sum,item) => sum+item.lon,0)/count];
      const width = count > 1 ? 38 : 28;
      const placed = place(actual[0],actual[1],width,28);
      leader(placeLayer,actual,placed,'#69756f');
      const label = count > 1 ? categories[p.kind] + count : categories[p.kind];
      const name = count > 1 ? '附近'+count+'家'+({food:'餐饮',tea:'茶饮',shop:'买手店'}[p.kind]) : p.name;
      const marker = L.marker(placed.position,{title:name,alt:name,icon:L.divIcon({
        className:'', html:'<div class="category-pin ' + p.kind + (count > 1 ? ' cluster' : '') + (group.some(item => item.approximate) ? ' approx' : '') + '">' + label + '</div>',
        iconSize:[width,28], iconAnchor:[width/2,14]})});
      const popup = count > 1
        ? '<b>' + esc(name) + '</b><br>放大地图可逐步拆分；清单可查看单店详情。<ul>' + group.map(item =>
          '<li><a target="_blank" rel="noopener" href="' + esc(search(item.name,item.location)) + '">' + esc(item.name) + '</a> · ' + esc(item.location) + '</li>').join('') + '</ul>'
        : singlePlacePopup(p);
      marker.bindPopup(popup + (placed.shifted ? '<br>图标略作偏移，细线指向标注位置。' : ''));
      marker.addTo(placeLayer);
      group.forEach(item => {item.marker = marker;});
    });
  }

  function draw(viewId, {fit = true} = {}) {
    current = viewId;
    document.body.classList.toggle('park-view', viewId === 10);
    const view = selectedView(viewId), day = view.description;
    el('day-select').value = viewId === 10 ? '7' : viewId >= 1 && viewId <= 8 ? String(viewId) : '';
    document.querySelectorAll('[data-view]').forEach(b => b.classList.toggle('active', Number(b.dataset.view) === viewId));
    const date = data.days.find(d => d.id === (viewId === 10 ? 7 : viewId))?.date;
    el('title').textContent = viewId === 10 ? '迪士尼乐园内 · ' + (date ? date + ' · ' : '') + view.title.replace(/^迪士尼园内·/, '')
      : day ? dayName(viewId) + ' · ' + (date ? date + ' · ' : '') + view.title
      : viewId === 9 ? '市区 · 第二天到第五天' : '全程 · 10月21日至27日';
    el('pace').textContent = day ? day.pace : viewId === 9 ? '第二天到第五天分街区走，每天只选一片。' : '缩放或拖动地图，自动查看市区与迪士尼乐园内路线。';
    el('mode').textContent = day ? day.mode : viewId === 9
      ? '四种颜色各是一天的街区游览线；住宿到首站、末站回程另乘车。'
      : '虚线只表示游玩顺序；「住·海友」为已定市区酒店位置，乐园附近住宿待定。';
    el('meal').textContent = day ? '吃逛建议：' + day.meal : '';
    el('optional').textContent = viewId !== 10 && day?.optional?.length ? '可选替换：' + day.optional.map(k => data.points[k].name).join('；') : '';
    el('park-plan').hidden = viewId !== 10;
    document.querySelectorAll('[data-park-variant]').forEach(button => {
      const active = button.dataset.parkVariant === parkVariant;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    document.querySelectorAll('[data-park-content]').forEach(panel => {
      panel.hidden = panel.dataset.parkContent !== parkVariant;
    });
    el('list').hidden = viewId === 10;
    el('source').innerHTML = day ? day.source.map(code => '<a target="_blank" rel="noopener" href="' + esc(data.sources[code]) + '">' + code + '</a>').join('') : '地图与地点取舍见首页研究依据。';
    el('static').href = prefix + view.static + '?v=' + version;
    el('fallback').src = prefix + view.static + '?v=' + version;
    routeList(view);
    updatePlaces(view);
    if (map) {
      if (detailOffline) map.removeLayer(detailOffline);
      detailOffline = view.id === 0 ? null : L.imageOverlay(prefix + view.background + '?v=' + version,
        view.bounds, {pane:'tilePane',attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'}).addTo(map);
      if (el('online').checked) {
        if (!map.hasLayer(online)) online.addTo(map);
        online.bringToFront();
      }
      if (fit) {
        suppressAuto = true;
        map.fitBounds(view.bounds,{padding:[12,12],animate:false});
        suppressAuto = false;
      }
      requestAnimationFrame(() => {if (current === viewId) {map.invalidateSize();renderMarkers(view);}});
    } else {
      el('fallback').style.display = 'block';
    }
  }

  el('buttons').innerHTML = [[0,'全程'],[9,'市区 · 第2–5天'],[10,'迪士尼乐园内']].map(([id,title]) =>
    '<button type="button" data-view="' + id + '">' + title + '</button>').join('');
  el('buttons').addEventListener('click',event => {
    const button = event.target.closest('[data-view]');
    if (button) draw(Number(button.dataset.view));
  });
  el('day-select').addEventListener('change',event => {
    if (event.target.value) draw(event.target.value === '7' ? 10 : Number(event.target.value));
  });
  el('park-plan').addEventListener('click',event => {
    const button = event.target.closest('[data-park-variant]');
    if (!button) return;
    parkVariant = button.dataset.parkVariant;
    const nextUrl = new URL(location.href);
    if (parkVariant !== 'tron') nextUrl.searchParams.set('variant',parkVariant);
    else nextUrl.searchParams.delete('variant');
    history.replaceState(null,'',nextUrl);
    draw(10,{fit:false});
  });
  el('list').addEventListener('click',event => {
    const link = event.target.closest('[data-day]');
    if (link) {
      event.preventDefault();
      const day = Number(link.dataset.day);
      draw(day === 7 ? 10 : day);
    }
  });
  el('places-list').addEventListener('click',event => {
    const button = event.target.closest('[data-poi]');
    if (!button) return;
    const item = currentPins[Number(button.dataset.poi)];
    if (map) {
      const zoom = Math.max(map.getZoom(),15);
      map.setView([item.lat,item.lon],zoom);
      L.popup().setLatLng([item.lat,item.lon]).setContent(singlePlacePopup(item)).openOn(map);
    }
  });
  document.querySelectorAll('[data-kind]').forEach(input => input.addEventListener('change',() => {
    const view = views.find(v => v.id === current);
    updatePlaces(view);renderMarkers(view);
  }));
  el('online').addEventListener('change',event => {if (map) event.target.checked ? online.addTo(map) : map.removeLayer(online);});
  if (map) {
    map.on('moveend',() => {
      if (suppressAuto) return;
      const center = map.getCenter();
      const next = viewForViewport({zoom:map.getZoom(),lat:center.lat,lon:center.lng,current});
      if (next !== current) draw(next,{fit:false});
      else renderMarkers(selectedView(current));
    });
    map.on('resize',() => renderMarkers(selectedView(current)));
  }
  draw(current);
})();
