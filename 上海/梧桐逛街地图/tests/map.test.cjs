const test = require('node:test');
const assert = require('node:assert/strict');
const { filterShops, mapEligibility, groupMapShops, coverageSummary, selectShops, normalizeFilters } = require('../dist/map-core.js');

const shops = [
  { id: 'a', name: 'Maison 森', style: '独立设计师', address: '上海安福路', tags: ['女装'], routeId: 'r1', core: true, status: 'active' },
  { id: 'b', name: '旧衣店', style: '古着', tags: ['复古'], routeId: 'r1', core: false, status: 'uncertain' },
  { id: 'c', name: '快闪', style: '设计师', routeId: 'r2', core: true, status: 'expired' },
  { id: 'd', name: '另一店', style: '古着', routeId: 'r2', core: false, status: 'active' }
];
test('默认排除待核实和过期记录，但不修改输入', () => {
  assert.deepEqual(filterShops(shops).map(s => s.id), ['a', 'd']);
  assert.equal(shops.length, 4);
});
test('路线、核心和搜索组合筛选', () => {
  assert.deepEqual(filterShops(shops, { routeId: 'r1', coreOnly: true, query: ' maison ' }).map(s => s.id), ['a']);
  assert.deepEqual(filterShops(shops, { routeId: 'all', query: '古着' }).map(s => s.id), ['d']);
  assert.equal(filterShops(shops, { query: '不存在' }).length, 0);
});
test('状态选择可显式访问待核实和过期记录', () => {
  assert.deepEqual(filterShops(shops, { status: 'uncertain' }).map(s => s.id), ['b']);
  assert.deepEqual(filterShops(shops, { status: 'expired', routeId: 'r2' }).map(s => s.id), ['c']);
  assert.equal(filterShops(shops, { status: 'all' }).length, 4);
});
test('搜索覆盖风格、地址与标签', () => {
  for (const query of ['独立设计师', '安福路', '女装']) {
    assert.deepEqual(filterShops(shops, { query }).map(s => s.id), ['a']);
  }
});
test('仅有声明及合法坐标的点才能绘制，近似点单独区分', () => {
  assert.equal(mapEligibility({ locationStatus: 'exact', lat: 31.2, lon: 121.4 }), 'exact');
  assert.equal(mapEligibility({ locationStatus: 'approximate', lat: 31.2, lon: 121.4 }), 'approximate');
  assert.equal(mapEligibility({ locationStatus: 'unknown', lat: 31.2, lon: 121.4 }), null);
  for (const lat of [null, undefined, '31.2', NaN, Infinity, 91]) {
    assert.equal(mapEligibility({ locationStatus: 'exact', lat, lon: 121.4 }), null);
  }
  assert.equal(mapEligibility({ locationStatus: 'exact', lat: 31.2, lon: 181 }), null);
});
test('相同坐标聚成一个可逐店访问的点，未知点不入组', () => {
  const records = [
    { id: 'a', locationStatus: 'exact', lat: 31.2, lon: 121.4 },
    { id: 'b', locationStatus: 'approximate', lat: 31.2, lon: 121.4 },
    { id: 'c', locationStatus: 'exact', lat: 31.21, lon: 121.4 },
    { id: 'd', locationStatus: 'unknown', lat: 31.2, lon: 121.4 }
  ];
  const groups = groupMapShops(records);
  assert.equal(groups.length, 2);
  assert.deepEqual(groups[0].shops.map(s => s.id), ['a', 'b']);
  assert.equal(groups[0].locationStatus, 'approximate');
  assert.equal(groups[1].locationStatus, 'exact');
  assert.equal(records.length, 4);
});
test('覆盖摘要区分记录数、精确点和近似点，不把未知点计入地图点', () => {
  const result = coverageSummary([
    { locationStatus: 'exact', lat: 31.2, lon: 121.4 },
    { locationStatus: 'approximate', lat: 31.2, lon: 121.4 },
    { locationStatus: 'unknown' },
    { locationStatus: 'exact', lat: null, lon: 121.4 }
  ]);
  assert.deepEqual(result, { total: 4, mapped: 2, exact: 1, approximate: 1, unmapped: 2 });
});
test('清单遵循路线顺序及shopIds顺序，远端加选在各路线底部', () => {
  const records = [
    { id: 'a', routeId: 'r2', status: 'active' },
    { id: 'b', routeId: 'r1', status: 'active', extension: true },
    { id: 'c', routeId: 'r1', status: 'active' },
    { id: 'd', routeId: 'r1', status: 'active' }
  ];
  const routeOrder = [{ id: 'r1', shopIds: ['b', 'd', 'c'] }, { id: 'r2', shopIds: ['a'] }];
  assert.deepEqual(selectShops(records, routeOrder, { routeId: 'all' }).map(s => s.id), ['d', 'c', 'b', 'a']);
  assert.deepEqual(records.map(s => s.id), ['a', 'b', 'c', 'd']);
});
test('搜索临时覆盖全部路线、资料状态和非核心记录，清空后恢复筛选', () => {
  const options = { routeId: 'r1', coreOnly: true, status: 'active', query: '快闪' };
  assert.deepEqual(selectShops(shops, [], options).map(s => s.id), ['c']);
  assert.equal(options.routeId, 'r1');
  assert.deepEqual(selectShops(shops, [], { ...options, query: '' }).map(s => s.id), ['a']);
});
test('从核心浏览切到过期或待核实状态时取消核心限制，回正常状态保持取消', () => {
  const records = shops.map(s => s.id === 'c' ? { ...s, core: false } : s);
  const initial = { routeId: 'r2', coreOnly: true, status: 'active', query: '' };
  assert.equal(selectShops(records, [], initial).length, 0);
  const expired = normalizeFilters({ ...initial, status: 'expired' });
  assert.equal(expired.coreOnly, false);
  assert.deepEqual(selectShops(records, [], expired).map(s => s.id), ['c']);
  const pending = normalizeFilters({ ...initial, routeId: 'r1', status: 'uncertain' });
  assert.equal(pending.coreOnly, false);
  assert.deepEqual(selectShops(records, [], pending).map(s => s.id), ['b']);
  const activeAgain = normalizeFilters({ ...pending, status: 'active' });
  assert.equal(activeAgain.coreOnly, false);
  assert.deepEqual(selectShops(records, [], activeAgain).map(s => s.id), ['a']);
  assert.equal(initial.coreOnly, true);
});
test('状态筛选入口本身不会让核心限制遮住非核心过期记录', () => {
  const records = [{ id: 'popup', routeId: 'r4', status: 'expired', core: false }];
  assert.deepEqual(selectShops(records, [], { routeId: 'r4', status: 'expired', coreOnly: true }).map(s => s.id), ['popup']);
});

test('品牌搜索忽略空格并匹配来源别名', () => {
  const shops=[{id:'x',name:'22 COLLECTION',sourceKey:'22collection',status:'uncertain',tags:[]},{id:'y',name:'MOONMOI',status:'uncertain',tags:[]}];
  assert.equal(filterShops(shops,{query:'22collection',status:'all'}).length,1);
  assert.equal(filterShops(shops,{query:'moon moi',status:'all'}).length,1);
});

