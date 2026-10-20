import fs from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {marked} from 'file:///C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked/lib/marked.esm.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../武康路轻松版');
const data=JSON.parse(fs.readFileSync(path.join(root,'行程数据.json'),'utf8'));
const reviews=JSON.parse(fs.readFileSync(path.resolve(root,'../research/xhs-v2-reviews.json'),'utf8'));
const guide=fs.readFileSync(path.join(root,'上海轻松旅行方案.md'),'utf8').replace(/\r\n/g,'\n');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sections=guide.split(/^## /m);
const section=name=>{
  const chunk=sections.find(s=>s.startsWith(name+'\n'));
  if(!chunk)throw new Error('Missing guide section: '+name);
  return marked.parse(chunk.slice(chunk.indexOf('\n')+1).replaceAll('.md)','.html)'));
};
const dayText=section('每天一个主题');
const alternatives=dayText.slice(dayText.indexOf('</table>')+'</table>'.length);
const accepted=reviews.filter(r=>r.countable).length;
const intro=sections[0].split('\n').find(line=>line.startsWith('已通过'));
const mapVersion=createHash('sha256')
  .update(fs.readFileSync(path.join(root,'地图资源/map-context.js')))
  .update(fs.readFileSync(path.join(root,'地图资源/map-ui.js')))
  .update(fs.readFileSync(path.join(root,'地图资源/map-ui.css')))
  .update(fs.readFileSync(path.join(root,'地图资源/地图视图.json')))
  .digest('hex').slice(0,10);

const homepage=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>上海轻松旅行｜每日路线与地图</title><meta name="description" content="上海10月21–27日轻松旅行：一天一条路线，在地图上看景点、美食、奶茶与买手店。"><link rel="stylesheet" href="网站资源/site.css"></head><body>
<header class="topbar"><a class="brand" href="index.html">上海 · 轻松旅行</a><nav aria-label="主要导航"><a class="active" href="index.html" aria-current="page">旅行计划</a><a href="全程与每日互动地图.html">路线地图</a><a href="美食与逛店清单.html">逛吃清单</a></nav></header>
<main><section class="intro"><p class="eyebrow">成都出发 · 两位成人 · 10月21–27日上海行程</p><h1>一张地图，<br>慢慢逛上海。</h1><p class="lead">21日12:05抵沪，先入住海友上海淮海中路酒店，下午逛衡山／岳阳路；22日集中逛店，之后几天走景点与热门街区。26日转场，27日迪士尼早享。</p><div class="chips"><span>市区海友酒店已定5晚</span><span>乐园附近2晚待定</span><span>27日乐园票＋早享票已购</span></div><p class="quiet">抵达机场、26–27日乐园附近住宿待确认；28日起前往杭州，后续暂不规划。</p></section>
<section id="map" class="section map-section"><div class="section-head"><div><p class="eyebrow">全程 · 市区 · 迪士尼乐园内</p><h2>缩放地图，路线跟着变。</h2></div><a class="secondary" href="全程与每日互动地图.html">打开全屏地图 →</a></div><iframe name="journey-map" id="journey-map" title="上海全程与每日路线互动地图" src="全程与每日互动地图.html?embed=1&amp;v=${mapVersion}" loading="eager"></iframe><p class="map-note">放大市区看第二天到第五天的分区路线；移到迪士尼再放大看乐园内路线。也可直接选日期或点上方按钮。「住·海友」只标酒店位置，不接景点路线；「吃」「茶」「逛」仅供顺路参考。</p><details class="text-panel"><summary>路线替换</summary><div class="prose">${alternatives}</div></details></section>
<section class="section compact-section"><details class="text-panel" open><summary>住宿安排 · 前5晚海友淮海中路</summary><div class="prose">${section('已确认住宿')}</div></details><details class="text-panel"><summary>本地经验与避雷</summary><div class="prose">${section('本地经验与避雷，保留这几条')}</div></details><details class="text-panel"><summary>迪士尼轻松玩法与入园准备</summary><div class="prose">${section('迪士尼这样玩更轻松')}</div></details></section>
<footer><details class="research-note"><summary>研究依据：${reviews.length}篇上海审读＋56篇迪士尼早享补充</summary><div class="prose">${marked.parse(intro.replaceAll('.md)','.html)'))}<p>原有上海研究${accepted}篇实质文字分析；迪士尼另逐篇打开69条相关结果，保留56篇早享可用正文。图片未逐张审读，视频未完整观看。</p><a href="小红书155篇审读索引.html">上海研究索引 →</a> · <a href="迪士尼早享56篇审读索引.html">迪士尼早享索引 →</a></div></details><p class="quiet">2026-10-14更新 · 街道底图 © OpenStreetMap contributors · 市区海友酒店已定，抵达机场与乐园附近住宿待确认</p></footer></main><script>const journeyFrame=document.getElementById('journey-map');addEventListener('message',event=>{if(event.origin!==location.origin||event.source!==journeyFrame.contentWindow||!matchMedia('(max-width:800px)').matches)return;const height=Number(event.data?.journeyMapHeight);if(Number.isFinite(height)&&height>600&&height<5000)journeyFrame.style.height=(height+2)+'px'});addEventListener('resize',()=>{if(!matchMedia('(max-width:800px)').matches)journeyFrame.style.height=''})</script></body></html>`;
fs.writeFileSync(path.join(root,'index.html'),homepage,'utf8');

function placeCards(fragment){
  return fragment.replace(/<table>[\s\S]*?<\/table>/g,table=>{
    const headers=[...(table.match(/<thead>[\s\S]*?<\/thead>/)||[''])[0].matchAll(/<th[^>]*>([\s\S]*?)<\/th>/g)].map(m=>m[1]);
    const titleIndex=headers.some(s=>/候选|店名与|街区/.test(s))&&headers.length>1?1:0;
    const sourceIndex=headers.findIndex(s=>s.includes('来源'));
    const rows=[...(table.match(/<tbody>[\s\S]*?<\/tbody>/)||[''])[0].matchAll(/<tr>[\s\S]*?<\/tr>/g)];
    return '<div class="place-grid">'+rows.map(row=>{
      const cells=[...row[0].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(m=>m[1]);
      return '<article class="place-card"><h3>'+cells[titleIndex]+'</h3>'+cells.map((cell,i)=>i===titleIndex?'':i===sourceIndex?'<details class="card-source"><summary>参考来源</summary>'+cell+'</details>':'<p><span class="field-label">'+headers[i]+'</span>'+cell+'</p>').join('')+'</article>';
    }).join('')+'</div>';
  });
}
const food=fs.readFileSync(path.join(root,'美食与逛店清单.md'),'utf8').replace(/\r\n/g,'\n').replaceAll('.md)','.html)');
const foodParts=food.split(/^## /m);
const groups=foodParts.slice(1).map((part,index)=>{
  const title=part.slice(0,part.indexOf('\n'));
  return '<details class="text-panel food-group"'+(index===0?' open':'')+'><summary>'+esc(title)+'</summary><div class="prose">'+placeCards(marked.parse(part.slice(part.indexOf('\n')+1)))+'</div></details>';
}).join('');
const foodPage=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>上海轻松旅行｜逛吃清单</title><link rel="stylesheet" href="网站资源/site.css"></head><body><header class="topbar"><a class="brand" href="index.html">上海 · 轻松旅行</a><nav aria-label="主要导航"><a href="index.html">旅行计划</a><a href="全程与每日互动地图.html">路线地图</a><a class="active" aria-current="page" href="美食与逛店清单.html">逛吃清单</a></nav></header><main><section class="section"><p class="eyebrow">美食 · 茶饮 · 买手店</p><h1 class="page-title">顺路挑一家，<br>好好吃一顿。</h1><p class="lead">按当天街区选店，按自己口味点单。</p><div class="chips"><span>一餐一家主店</span><span>茶饮选一杯</span><span>小店选两三家</span></div><p class="quiet">在<a href="index.html#map">路线地图</a>查看位置；这里展开看点单、取舍与来源。价格、分店入口和营业以当天为准。</p></section><section class="section">${groups}</section><footer><details class="research-note"><summary>候选清单的来源与使用范围</summary><div class="prose">${marked.parse(foodParts[0].replace(/^# .+\n/,''))}</div></details><p class="quiet">2026-10-14更新 · <a href="小红书155篇审读索引.html">研究来源与取舍</a></p></footer></main></body></html>`;
fs.writeFileSync(path.join(root,'美食与逛店清单.html'),foodPage,'utf8');
console.log(JSON.stringify({homepage:'index.html',days:data.days.length,read:reviews.length,accepted}));
