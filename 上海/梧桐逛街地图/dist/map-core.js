(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.MapCore = factory();
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  function filterShops(shops, options) {
    var o = options || {};
    var query = String(o.query || '').trim().toLocaleLowerCase().replace(/\s+/g, '');
    var status = o.status || 'active';
    return shops.filter(function (shop) {
      return (!o.routeId || o.routeId === 'all' || shop.routeId === o.routeId)
        && (!o.coreOnly || shop.core === true)
        && (status === 'all' || shop.status === status)
        && (!query || [shop.name, shop.sourceKey, shop.style, shop.address].concat(shop.tags || []).join(' ').toLocaleLowerCase().replace(/\s+/g, '').includes(query));
    });
  }
  function mapEligibility(shop) {
    if (!shop || !['exact', 'approximate'].includes(shop.locationStatus)) return null;
    if (!Number.isFinite(shop.lat) || !Number.isFinite(shop.lon) || Math.abs(shop.lat) > 90 || Math.abs(shop.lon) > 180) return null;
    return shop.locationStatus;
  }
  function groupMapShops(shops) {
    var groups = new Map();
    shops.forEach(function (shop) {
      var eligibility = mapEligibility(shop);
      if (!eligibility) return;
      var key = shop.lat + ',' + shop.lon;
      if (!groups.has(key)) groups.set(key, { lat: shop.lat, lon: shop.lon, shops: [], locationStatus: eligibility });
      var group = groups.get(key);
      group.shops.push(shop);
      if (eligibility === 'approximate') group.locationStatus = 'approximate';
    });
    return Array.from(groups.values());
  }
  function coverageSummary(shops) {
    var summary = { total: shops.length, mapped: 0, exact: 0, approximate: 0, unmapped: 0 };
    shops.forEach(function (shop) {
      var eligibility = mapEligibility(shop);
      if (eligibility) { summary.mapped++; summary[eligibility]++; }
      else summary.unmapped++;
    });
    return summary;
  }
  function normalizeFilters(options) {
    var normalized = Object.assign({}, options || {});
    if (normalized.status === 'uncertain' || normalized.status === 'expired') normalized.coreOnly = false;
    return normalized;
  }
  function selectShops(shops, routes, options) {
    var o = normalizeFilters(options);
    var searching = String(o.query || '').trim();
    var selected = filterShops(shops, searching ? { query: searching, routeId: 'all', status: 'all', coreOnly: false } : o);
    var routeOrder = new Map();
    var shopOrder = new Map();
    var originalOrder = new Map();
    routes.forEach(function (route, index) {
      routeOrder.set(route.id, index);
      (route.shopIds || []).forEach(function (id, position) { shopOrder.set(id, position); });
    });
    shops.forEach(function (shop, index) { originalOrder.set(shop.id, index); });
    function rank(map, key, fallback) { return map.has(key) ? map.get(key) : fallback; }
    return selected.sort(function (a, b) {
      return rank(routeOrder, a.routeId, routes.length) - rank(routeOrder, b.routeId, routes.length)
        || Number(Boolean(a.extension)) - Number(Boolean(b.extension))
        || rank(shopOrder, a.id, shops.length) - rank(shopOrder, b.id, shops.length)
        || originalOrder.get(a.id) - originalOrder.get(b.id);
    });
  }
  return { filterShops: filterShops, mapEligibility: mapEligibility, groupMapShops: groupMapShops, coverageSummary: coverageSummary, selectShops: selectShops, normalizeFilters: normalizeFilters };
}));
