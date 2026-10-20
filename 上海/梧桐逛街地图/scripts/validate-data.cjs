const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const c={window:{}};vm.runInNewContext(fs.readFileSync('dist/data.js','utf8'),c);const d=c.window.DATA;
assert.equal(d.sources.length,13,'13 independent supplied sources');assert.equal(d.routes.length,5,'5 routes');
const sources=new Set(d.sources.map(s=>s.id)),shops=new Map(d.shops.map(s=>[s.id,s]));assert.equal(shops.size,d.shops.length);
for(const s of d.shops){assert(s.name&&s.style);assert(s.sourceIds.length);for(const id of s.sourceIds)assert(sources.has(id),`${s.name} source ${id}`);if(s.locationStatus==='exact'){assert(s.evidenceUrl);assert(Number.isFinite(s.lat)&&Number.isFinite(s.lon));}if(s.locationStatus==='unknown')assert(s.lat===null&&s.lon===null);}
for(const r of d.routes){for(const id of r.shopIds)assert(shops.has(id),id);for(const id of r.coreIds){let s=shops.get(id);assert(s&&s.status!=='expired'&&s.locationStatus!=='unknown',`invalid core ${id}`);}}
for(const source of d.sources)assert(d.shops.some(s=>s.sourceIds.includes(source.id)),`${source.id} missing shops`);
assert(d.shops.some(s=>s.name.includes('过森日')&&s.status==='expired'));
console.log(`Validated ${d.sources.length} sources, ${d.routes.length} routes, ${d.shops.length} records.`);

for(const name of ['MOONMOI','OPEN YY','Lost in echo','22 COLLECTION']) assert.equal(d.shops.filter(s=>s.name===name).length,1,name+' must occur once');

assert(!d.shops.some(s=>s.sourceKey==='DORYDORY'));
for(const key of ['东日','MOONMOI','OPEN YY','APOLI ITABAKERY']) {const s=d.shops.find(s=>s.sourceKey===key); assert(s&&s.address&&s.operatingNote,key);}

for(const key of ['东日','MOONMOI','OPEN YY','APOLI ITABAKERY']) {const s=d.shops.find(s=>s.sourceKey===key);assert(Number.isFinite(s.lat)&&Number.isFinite(s.lon),key+' mapped');}
for(const key of ['MOONMOI','OPEN YY','BF']) {const s=d.shops.find(s=>s.sourceKey===key);assert(s.status==='uncertain'&&!s.core,key+' remains uncertain');}
