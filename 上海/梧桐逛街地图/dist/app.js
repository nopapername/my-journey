(function () {
  'use strict';
  var data = window.DATA || { routes: [], shops: [], sources: [] };
  var routes = Array.isArray(data.routes) ? data.routes : [];
  var shops = Array.isArray(data.shops) ? data.shops : [];
  var sources = Array.isArray(data.sources) ? data.sources : [];
  var core = window.MapCore;
  var routeById = new Map(routes.map(function (route) { return [route.id, route]; }));
  var sourceById = new Map(sources.map(function (source) { return [source.id, source]; }));
  var palette = ['#657e56', '#ad825c', '#688992', '#9b787f', '#8c895a'];
  var numbers = new Map();
  (core ? core.selectShops(shops, routes, { routeId: 'all', status: 'all' }) : shops).forEach(function (shop) { if (!numbers.has(shop.id)) numbers.set(shop.id, numbers.size + 1); });
  var state = { routeId: 'all', query: '', coreOnly: false, status: 'all', selected: null };
  var map = null;
  var mapLayers = null;
  var markers = new Map();
  var tilesLoaded = 0;
  var tileErrors = 0;
  var mapNotice = document.getElementById('map-notice');
  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }
  function routeColor(route) {
    if (route && /^#[0-9a-f]{3,8}$/i.test(route.color || '')) return route.color;
    return palette[Math.max(0, routes.indexOf(route)) % palette.length];
  }
  function colorForShop(shop) { return routeColor(routeById.get(shop.routeId)); }
  function numberFor(shop) { return String(numbers.get(shop.id) || '').padStart(2, '0'); }
  function safeUrl(value) {
    try { var url = new URL(value); return /^https?:$/.test(url.protocol) ? url.href : null; } catch (_) { return null; }
  }
  function link(text, href, className) {
    var node = element('a', className, text);
    node.href = href;
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
    return node;
  }
  function amapLink(shop) {
    return link('搜索此店 ↗', 'https://uri.amap.com/search?keyword=' + encodeURIComponent('上海 ' + shop.name) + '&city=' + encodeURIComponent('上海') + '&view=map', 'amap-link');
  }
  function warningFor(shop) {
    var warnings = [];
    var eligibility = core.mapEligibility(shop);
    if (eligibility === 'approximate') warnings.push('参考位置，非实测入口');
    if (!eligibility) warnings.push('未定位，请先核实门牌');
    if (shop.status === 'expired') warnings.push('快闪原期限已过');
    if (shop.status === 'uncertain') warnings.push('资料待核');
    return warnings.join(' · ');
  }
  function evidenceLinks(shop, className) {
    var links = element('div', className || 'evidence-links');
    var seen = new Set();
    [['evidenceUrl', '原始地址证据 ↗'], ['anchorEvidenceUrl', '定位参照来源 ↗'], ['geocodeEvidenceUrl', '地址编码来源 ↗']].forEach(function (entry) {
      var url = safeUrl(shop[entry[0]]);
      if (url && !seen.has(url)) { links.appendChild(link(entry[1], url)); seen.add(url); }
    });
    return links;
  }
  function shopDetails(shop, includeEvidence) {
    var details = element('details', 'shop-details');
    details.appendChild(element('summary', '', '位置与资料说明'));
    if (shop.note) details.appendChild(element('p', 'shop-note', shop.note));
    if (shop.coordinateNote) details.appendChild(element('p', 'shop-note', shop.coordinateNote));
    if (includeEvidence) {
      var links = evidenceLinks(shop);
      if (links.childNodes.length) details.appendChild(links);
    }
    return details.childNodes.length > 1 ? details : null;
  }
  function sourceLinks(shop, container) {
    (shop.sourceIds || []).forEach(function (id) {
      var source = sourceById.get(id);
      var url = source && safeUrl(source.url);
      if (url) {
        var node = link('笔记 ' + (sources.indexOf(source) + 1) + ' ↗', url);
        node.title = source.title || '原始来源';
        container.appendChild(node);
      }
    });
    container.appendChild(amapLink(shop));
  }
  function showNotice(message) { mapNotice.textContent = message; mapNotice.hidden = !message; }
  function isSearching() { return Boolean(state.query.trim()); }
  function appendOperatingInfo(container, shop) {
    var info = [shop.openingHours, shop.operatingNote].filter(function (value) { return typeof value === 'string' && value.trim(); });
    if (info.length) container.appendChild(element('p', 'shop-note', '营业资料：' + info.join(' · ')));
  }
  function popup(shop, group) {
    var wrap = element('div', 'shop-popup');
    if (group && group.shops.length > 1) {
      wrap.appendChild(element('p', 'popup-group-title', '同点位 · ' + group.shops.length + ' 条记录'));
      wrap.appendChild(element('p', 'popup-group-note', '同楼／街段点位为示意；共用坐标不代表已确认同址，请核对各店门牌。'));
      var chooser = element('div', 'popup-shop-chooser');
      group.shops.forEach(function (item) {
        var button = element('button', 'popup-shop-choice', numberFor(item) + ' ' + item.name);
        button.type = 'button';
        button.setAttribute('aria-pressed', String(item.id === shop.id));
        button.addEventListener('click', function (event) {
          event.stopPropagation();
          markSelected(item.id, true);
          var marker = markers.get(item.id);
          if (marker) marker.setPopupContent(popup(item, group));
        });
        chooser.appendChild(button);
      });
      wrap.appendChild(chooser);
    }
    wrap.appendChild(element('h3', 'popup-title', numberFor(shop) + ' · ' + shop.name));
    wrap.appendChild(element('p', 'popup-style', shop.style || '风格待补全'));
    wrap.appendChild(element('p', 'popup-address', shop.address || '地址待核实'));
    appendOperatingInfo(wrap, shop);
    var warning = warningFor(shop);
    if (warning) wrap.appendChild(element('p', 'popup-warning', warning));
    if (shop.extension) wrap.appendChild(element('p', 'popup-warning', '远端加选：请另留时间，核心路线时长不含全部加选。'));
    var details = shopDetails(shop, false);
    if (details) wrap.appendChild(details);
    var evidence = evidenceLinks(shop, 'popup-links evidence-links');
    if (evidence.childNodes.length) wrap.appendChild(evidence);
    var links = element('div', 'popup-links');
    sourceLinks(shop, links);
    wrap.appendChild(links);
    return wrap;
  }
  function markSelected(id, scrollCard) {
    state.selected = id;
    document.querySelectorAll('.shop-card').forEach(function (card) {
      card.classList.toggle('selected', card.dataset.shopId === id);
      if (scrollCard && !window.matchMedia('(max-width: 800px)').matches && card.dataset.shopId === id) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
    new Set(markers.values()).forEach(function (marker) {
      var node = marker.getElement();
      if (node) node.classList.toggle('selected', marker.shopGroup.shops.some(function (shop) { return shop.id === id; }));
    });
  }
  function focusShop(shop) {
    markSelected(shop.id, false);
    var marker = markers.get(shop.id);
    if (map && marker) {
      map.setView(marker.getLatLng(), Math.max(map.getZoom(), 16), { animate: !window.matchMedia('(prefers-reduced-motion: reduce)').matches });
      marker.setPopupContent(popup(shop, marker.shopGroup));
      marker.openPopup();
      if (window.matchMedia('(max-width: 800px)').matches) document.querySelector('.map-panel').scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (!core.mapEligibility(shop)) {
      showNotice(shop.name + '：尚无可靠坐标。请使用“搜索此店”核实具体位置。');
    }
  }
  function shopCard(shop) {
    var eligibility = core.mapEligibility(shop);
    var card = element('article', 'shop-card' + (state.selected === shop.id ? ' selected' : ''));
    card.dataset.shopId = shop.id;
    card.style.setProperty('--route', colorForShop(shop));
    var focus = element('button', 'shop-focus');
    focus.type = 'button';
    focus.setAttribute('aria-label', (eligibility ? '在地图上查看' : '查看位置提示：') + shop.name);
    focus.appendChild(element('span', 'shop-number ' + (eligibility || 'unknown'), numberFor(shop)));
    var main = element('span', 'shop-main');
    main.appendChild(element('span', 'shop-name', shop.name));
    focus.appendChild(main);
    focus.addEventListener('click', function () { focusShop(shop); });
    card.appendChild(focus);
    card.appendChild(element('p', 'shop-style', shop.style || '风格待补全'));
    card.appendChild(element('p', 'shop-address', shop.address || '地址待核实'));
    appendOperatingInfo(card, shop);
    var tags = element('div', 'shop-tags');
    if (shop.core) tags.appendChild(element('span', 'tag core', '核心店铺'));
    if (shop.extension) tags.appendChild(element('span', 'tag extension', '远端加选'));
    if (state.routeId === 'all' || isSearching()) tags.appendChild(element('span', 'tag', (routeById.get(shop.routeId) || {}).title || '路线待定'));
    (shop.tags || []).slice(0, 3).forEach(function (tag) { tags.appendChild(element('span', 'tag', tag)); });
    if (shop.status !== 'active') tags.appendChild(element('span', 'tag warning', shop.status === 'expired' ? '过期记录' : '待核实'));
    if (eligibility === 'approximate') tags.appendChild(element('span', 'tag warning', '近似参考'));
    if (!eligibility) tags.appendChild(element('span', 'tag warning', '未定位'));
    if (tags.childNodes.length) card.appendChild(tags);
    var warning = warningFor(shop);
    if (warning) card.appendChild(element('p', 'shop-warning', warning));
    var details = shopDetails(shop, true);
    if (details) card.appendChild(details);
    var links = element('div', 'shop-links');
    sourceLinks(shop, links);
    card.appendChild(links);
    return card;
  }
  function renderRoutes() {
    var tabs = document.getElementById('route-tabs');
    tabs.replaceChildren();
    routes.forEach(function (route, index) {
      var button = element('button', 'route-tab');
      button.type = 'button';
      button.style.setProperty('--route', routeColor(route));
      button.setAttribute('aria-pressed', String(!isSearching() && state.routeId === route.id));
      button.appendChild(element('span', 'route-number', String(index + 1).padStart(2, '0')));
      var text = element('span', 'route-text');
      text.appendChild(element('strong', '', route.title));
      if (route.subtitle) text.appendChild(element('small', '', route.subtitle));
      button.appendChild(text);
      button.appendChild(element('span', 'route-arrow', '↗'));
      button.addEventListener('click', function () { state.routeId = route.id; state.query = ''; document.getElementById('search').value = ''; state.selected = null; render(true); });
      tabs.appendChild(button);
    });
    var all = document.getElementById('all-routes');
    all.classList.toggle('active', state.routeId === 'all' || isSearching());
    all.setAttribute('aria-pressed', String(state.routeId === 'all' || isSearching()));
    var route = isSearching() ? null : routeById.get(state.routeId);
    var summary = document.getElementById('route-summary');
    summary.replaceChildren();
    if (isSearching()) summary.appendChild(element('p', '', '正在搜索全部路线、全部状态与非核心记录。清空关键词可恢复原筛选。'));
    else if (route) {
      summary.appendChild(element('p', '', route.summary || '沿街慢逛，按兴趣选择停留。'));
      var walking = Number.isFinite(route.walkingDistanceKm) && Number.isFinite(route.walkingMinutes) ? '步行约' + route.walkingDistanceKm + '公里 / ' + route.walkingMinutes + '分钟' : '';
      var duration = route.duration ? String(route.duration).replace(/^核心店建议\s*/, '建议逛店').replace(/\s+/g, '') : '';
      var meta = ['核心' + (route.coreIds || []).length + '店', walking, duration].filter(Boolean).join(' · ');
      if (meta) summary.appendChild(element('p', 'route-meta', meta));
    } else summary.appendChild(element('p', '', '五条独立动线，按街区与当天心情选择。虚线为核心步行参考线，基于参考点规划，非现场核验导航。'));
    var extensions = shops.filter(function (shop) { return shop.extension && (state.routeId === 'all' || shop.routeId === state.routeId); }).length;
    if (extensions && !isSearching()) summary.appendChild(element('p', 'extension-note', '含 ' + extensions + ' 处远端加选，建议另留时间；核心路线时长不包含全部加选。'));
    if (!isSearching()) {
      var evidenceRoutes = route ? [route] : routes;
      var evidence = element('details', 'route-evidence');
      evidence.appendChild(element('summary', '', '步行参考线依据'));
      evidence.appendChild(element('p', '', '基于参考点与 OSM 路网估算，不含逛店、等候或远端加选；非现场核验导航。'));
      evidenceRoutes.forEach(function (item) {
        var endpoints = [item.start, item.end].filter(Boolean).join(' → ');
        if (endpoints) evidence.appendChild(element('p', '', (route ? '' : item.title + '：') + endpoints));
        if (item.walkNote) evidence.appendChild(element('p', '', item.walkNote));
        var url = safeUrl(item.routeEvidenceUrl);
        if (url) evidence.appendChild(link(item.title + ' · 步行规划依据 ↗', url));
      });
      if (evidence.childNodes.length > 2) summary.appendChild(evidence);
    }
    document.getElementById('map-title').textContent = isSearching() ? '全部路线 · 搜索结果' : route ? route.title : '上海 · 五条逛街路线';
  }
  function validPath(route) {
    return (route.path || []).filter(function (point) { return Array.isArray(point) && Number.isFinite(point[0]) && Number.isFinite(point[1]) && Math.abs(point[0]) <= 90 && Math.abs(point[1]) <= 180; });
  }
  function selectedRoutes() { return isSearching() ? [] : routes.filter(function (route) { return state.routeId === 'all' || route.id === state.routeId; }); }
  function fitPoints(points) {
    if (!map || !points.length) return;
    map.fitBounds(window.L.latLngBounds(points), { paddingTopLeft: [55, 125], paddingBottomRight: [55, 80], maxZoom: 16, animate: false });
  }
  function renderMap(visible, fit) {
    if (!map) return;
    mapLayers.clearLayers();
    markers.clear();
    var points = [];
    selectedRoutes().forEach(function (route) {
      var path = validPath(route);
      if (path.length > 1) {
        window.L.polyline(path, { color: '#fffefa', weight: 8, opacity: .95, lineCap: 'round', interactive: false }).addTo(mapLayers);
        window.L.polyline(path, { color: routeColor(route), weight: 4, opacity: .9, dashArray: '8 9', lineCap: 'round', interactive: false }).addTo(mapLayers);
        points = points.concat(path);
      }
    });
    core.groupMapShops(visible).forEach(function (group) {
      var shop = group.shops[0];
      var grouped = group.shops.length > 1;
      var selected = group.shops.some(function (item) { return state.selected === item.id; });
      var label = numberFor(shop) + (grouped ? '<small>+' + (group.shops.length - 1) + '</small>' : '');
      var icon = window.L.divIcon({ className: 'map-marker ' + group.locationStatus + (grouped ? ' grouped' : '') + (selected ? ' selected' : ''), html: '<span style="--route:' + colorForShop(shop) + '">' + label + '</span>', iconSize: [grouped ? 43 : 30, 30], iconAnchor: [grouped ? 21 : 15, 15], popupAnchor: [0, -16] });
      var marker = window.L.marker([group.lat, group.lon], { icon: icon, title: group.shops.map(function (item) { return numberFor(item) + ' ' + item.name; }).join(' / ') + (group.locationStatus === 'approximate' ? '（参考点）' : ''), alt: grouped ? '同点位' + group.shops.length + '条记录，点击逐店查看' : shop.name, keyboard: true }).addTo(mapLayers);
      marker.shopGroup = group;
      marker.bindPopup(popup(shop, group), { maxWidth: 290, maxHeight: 400 });
      marker.on('click', function () {
        var current = group.shops.find(function (item) { return state.selected === item.id; }) || shop;
        marker.setPopupContent(popup(current, group));
        markSelected(current.id, true);
      });
      group.shops.forEach(function (item) { markers.set(item.id, marker); });
      points.push([group.lat, group.lon]);
    });
    if (fit) fitPoints(points);
  }
  function render(fit) {
    state = core.normalizeFilters(state);
    renderRoutes();
    var visible = core.selectShops(shops, routes, state);
    var coreCheckbox = document.getElementById('core-only');
    coreCheckbox.checked = Boolean(state.coreOnly);
    coreCheckbox.disabled = isSearching() || state.status === 'uncertain' || state.status === 'expired';
    coreCheckbox.title = state.status === 'uncertain' || state.status === 'expired' ? '查看待核实或过期记录时暂不限制核心店铺' : '';
    document.getElementById('status').disabled = isSearching();
    var list = document.getElementById('shop-list');
    list.replaceChildren();
    if (state.selected && !visible.some(function (shop) { return shop.id === state.selected; })) state.selected = null;
    visible.forEach(function (shop) { list.appendChild(shopCard(shop)); });
    if (!visible.length) list.appendChild(element('div', 'empty-state', shops.length ? '这一筛选下还没有小店。试试其他状态、路线或关键词。' : '店铺资料尚未载入，请稍后刷新页面。'));
    var unmapped = visible.filter(function (shop) { return !core.mapEligibility(shop); }).length;
    document.getElementById('result-count').textContent = visible.length + ' 家' + (unmapped ? ' · ' + unmapped + ' 家未定位' : '');
    document.getElementById('list-heading').textContent = isSearching() ? '全库搜索结果' : state.routeId === 'all' ? '街区小店清单' : '这一段的小店';
    document.getElementById('result-note').textContent = isSearching() ? '搜索已覆盖全部路线与状态，含非核心、待核实及过期记录；请留意卡片提示。' : (state.coreOnly ? '当前仅显示核心店铺，取消勾选可看完整清单。' : '') + (state.status === 'all' ? '含待核实与过期记录，请留意卡片标识；虚线仅串联核心点。' : state.status === 'active' ? '正常收录不代表当前营业；待核实及过期可在上方筛选。' : '请留意资料与位置提示，出发前确认现况。');
    renderMap(visible, fit);
  }
  function renderSources() {
    var container = document.getElementById('source-list');
    sources.forEach(function (source, index) {
      var item = element('div', 'source-item');
      var url = safeUrl(source.url);
      item.appendChild(url ? link(String(index + 1).padStart(2, '0') + ' · ' + source.title, url) : element('span', '', source.title));
      if (source.scope) item.appendChild(element('p', '', '阅读范围：' + source.scope));
      if (source.limitations) item.appendChild(element('p', '', '资料缺口：' + source.limitations));
      container.appendChild(item);
    });
    document.getElementById('source-count').textContent = sources.length + ' 篇';
    document.getElementById('updated').textContent = data.updated ? '资料整理于 ' + data.updated + ' · 出发前请核实门店现况' : '';
  }
  function renderCoverage() {
    var summary = core.coverageSummary(shops);
    document.getElementById('coverage-stats').textContent = summary.total + ' 条记录 · ' + summary.mapped + ' 条有地图参考点';
    document.getElementById('coverage-stats').title = summary.exact + ' 条精确门店点，' + summary.approximate + ' 条近似参考点，' + summary.unmapped + ' 条未定位。记录数不代表均已核实。';
    document.getElementById('coverage-note').textContent = data.coverageNote || '资料来自公开笔记与地址核查，未知信息保留待核。';
  }
  function initMap() {
    if (!window.L) {
      document.querySelector('.map-panel').classList.add('no-map');
      showNotice('地图组件暂时无法载入。店铺清单与来源仍可阅读，也可使用“搜索此店”打开高德。');
      document.getElementById('reset-map').disabled = true;
      return;
    }
    try {
      map = window.L.map('map', { zoomControl: false, scrollWheelZoom: true }).setView([31.213, 121.45], 14);
      window.L.control.zoom({ position: 'topright' }).addTo(map);
      mapLayers = window.L.layerGroup().addTo(map);
      var tile = window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>', maxZoom: 19 });
      tile.on('tileload', function () { tilesLoaded++; });
      tile.on('tileerror', function () { tileErrors++; if (tileErrors >= 3) showNotice('部分地图底图未能载入。编号与路线仍可查看；完整店铺资料在清单中。'); });
      tile.addTo(map);
      window.setTimeout(function () { if (!tilesLoaded) showNotice('地图底图暂时无法载入。清单仍可阅读；请使用“搜索此店”核实位置。'); }, 12000);
      if (window.ResizeObserver) new ResizeObserver(function () { map.invalidateSize(); }).observe(document.getElementById('map'));
    } catch (_) {
      map = null;
      document.querySelector('.map-panel').classList.add('no-map');
      showNotice('地图初始化失败，店铺清单和高德搜索仍可使用。');
      document.getElementById('reset-map').disabled = true;
    }
  }
  if (!core) {
    document.getElementById('shop-list').appendChild(element('p', 'empty-state', '页面组件未完整载入，请刷新重试。'));
    showNotice('筛选组件暂时无法载入，请刷新重试。');
    return;
  }
  document.getElementById('all-routes').addEventListener('click', function () { state.routeId = 'all'; state.query = ''; document.getElementById('search').value = ''; state.selected = null; render(true); });
  document.getElementById('search').addEventListener('input', function (event) { state.query = event.target.value; render(true); });
  document.getElementById('core-only').addEventListener('change', function (event) { state.coreOnly = event.target.checked; render(true); });
  document.getElementById('status').addEventListener('change', function (event) { state.status = event.target.value; render(true); });
  document.getElementById('reset-map').addEventListener('click', function () {
    var points = [];
    routes.forEach(function (route) { points = points.concat(validPath(route)); });
    shops.forEach(function (shop) { if (core.mapEligibility(shop)) points.push([shop.lat, shop.lon]); });
    fitPoints(points);
  });
  renderSources();
  renderCoverage();
  initMap();
  render(true);
}());
