import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {marked} from 'file:///C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked/lib/marked.esm.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../武康路轻松版');
const css='body{max-width:1080px;margin:auto;padding:26px;font:16px/1.8 Microsoft YaHei,sans-serif;color:#173238;background:#faf8f2}h1{font-size:30px}h2{font-size:23px;margin-top:35px}table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow:auto}td,th{padding:10px;border:1px solid #ccd5cd}th{background:#e0ebe4}a{color:#0f766e}img{max-width:100%}ul{padding-left:24px}nav{position:sticky;top:0;background:#faf8f2;padding:10px 0;border-bottom:1px solid #ccd5cd}';
for(const name of ['上海轻松旅行方案','美食与逛店清单','小红书155篇审读索引']){
  const s=fs.readFileSync(path.join(root,name+'.md'),'utf8').replaceAll('.md)', '.html)');
  const body=marked.parse(s);
  fs.writeFileSync(path.join(root,name+'.html'),'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+name+'</title><style>'+css+'nav{display:flex;gap:18px;flex-wrap:wrap;font-size:14px}nav a{text-decoration:none}</style></head><body><nav aria-label="主要导航"><a href="index.html">旅行计划</a><a href="全程与每日互动地图.html">路线地图</a><a href="美食与逛店清单.html">逛吃清单</a></nav>'+body+'<footer style="margin-top:35px;font-size:13px;color:#556765"><a href="小红书155篇审读索引.html">研究来源与取舍</a> · 抵达机场与酒店分店待确认</footer></body></html>','utf8');
}
