const test = require('node:test');
const assert = require('node:assert/strict');
const { viewForViewport, dayName } = require('../武康路轻松版/地图资源/map-context.js');

test('whole-city zoom keeps the complete journey even above downtown', () => {
  assert.equal(viewForViewport({ zoom: 10.5, lat: 31.22, lon: 121.47, current: 0 }), 0);
});

test('zooming into central Shanghai reveals the four city sightseeing routes', () => {
  assert.equal(viewForViewport({ zoom: 13, lat: 31.22, lon: 121.47, current: 0 }), 9);
});

test('zooming into Disneyland reveals the park route without a button click', () => {
  assert.equal(viewForViewport({ zoom: 15, lat: 31.145, lon: 121.656, current: 0 }), 10);
});

test('a chosen city day stays selected while exploring its streets', () => {
  assert.equal(viewForViewport({ zoom: 15, lat: 31.214, lon: 121.445, current: 2 }), 2);
  assert.equal(viewForViewport({ zoom: 13, lat: 31.214, lon: 121.445, current: 2 }), 9);
});

test('zooming away from a region returns to complete journey context', () => {
  assert.equal(viewForViewport({ zoom: 11.5, lat: 31.145, lon: 121.656, current: 10 }), 0);
  assert.equal(viewForViewport({ zoom: 15, lat: 31.3, lon: 121.8, current: 9 }), 0);
});

test('day names are explicit rather than D-number shorthand', () => {
  assert.equal(dayName(1), '第一天');
  assert.equal(dayName(7), '第七天');
});
