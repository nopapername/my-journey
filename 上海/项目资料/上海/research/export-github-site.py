from pathlib import Path
import shutil,json
from PIL import Image

WORKSPACE=Path(__file__).resolve().parents[2]
SOURCE=WORKSPACE/'上海/武康路轻松版'
REPO=WORKSPACE/'my-journey'
DEST=REPO/'上海';DEST.mkdir(exist_ok=True)
allowed={'.html','.css','.js','.json','.md','.txt','.png'}
manifest=[]
for p in sorted(SOURCE.rglob('*')):
    if not p.is_file() or '历史草案' in p.parts or p.suffix not in allowed:continue
    rel=p.relative_to(SOURCE);out=DEST/rel;out.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.png':
        out=out.with_suffix('.jpg')
        Image.open(p).convert('RGB').save(out,'JPEG',quality=86,optimize=True,progressive=True)
    else:
        text=p.read_text(encoding='utf-8')
        # The exported map images are JPEG, but JavaScript's remote OSM tile
        # URL must keep its original .png extension.
        if p.suffix in {'.html','.json','.md','.txt'}:
            text=text.replace('.png','.jpg')
        out.write_text(text,encoding='utf-8')
    manifest.append({'path':out.relative_to(REPO).as_posix(),'bytes':out.stat().st_size})
(REPO/'.nojekyll').write_text('',encoding='utf-8')
(REPO/'.gitignore').write_text('Thumbs.db\n.DS_Store\n__pycache__/\n',encoding='utf-8')
(REPO/'README.md').write_text('''# 我的旅行

[上海轻松旅行网站](https://nopapername.github.io/my-journey/%E4%B8%8A%E6%B5%B7/)

## 目录

- `上海/`：完整上海旅行网站；入口是 `上海/index.html`。
- `上海/每日地图/`：D1–D8与迪士尼园内地图。
- `上海/网站资源/`：首页样式与交互。
- `上海/地图资源/`：离线街道底图、Leaflet及许可证。

网站使用相对链接，部署到GitHub Pages项目路径后可直接访问。顶部只保留旅行计划、路线地图、逛吃清单三个入口。

## 发布

GitHub Pages选择 `Deploy from a branch`，分支 `main`，目录 `/(root)`。`.nojekyll`让网站文件直接发布，无需安装依赖或构建。

访问地址：`https://nopapername.github.io/my-journey/上海/`。

## 资料与状态

2026-10-14整理；155篇上海笔记审读，其中101篇实质文字分析。迪士尼早享另打开69条相关结果，保留56篇可用正文，独立来源索引见 `上海/迪士尼早享56篇审读索引.html`。图集未逐张审读，视频未完整观看。原文缓存与历史草案不包含在仓库中。

两位成人、10月21日12:05抵沪，27日迪士尼一日票＋早享票已购；21–25日5晚已定海友上海淮海中路酒店（乌鲁木齐中路247号2楼），26–27日乐园附近住宿待定。28日起转杭州，后续暂不规划。抵达机场待确认。市区酒店在地图中单独标注，不连接每日景点路线；路线虚线表示景点顺序，跨区乘车。

地图数据 © OpenStreetMap contributors，参见 https://www.openstreetmap.org/copyright 。Leaflet许可证位于 `上海/地图资源/Leaflet-LICENSE.txt`。网页里的研究摘要不代表笔记作者达成一致推荐。
''',encoding='utf-8')
(REPO/'index.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>我的旅行</title><style>body{max-width:760px;margin:10vh auto;padding:25px;font:17px/1.8 Microsoft YaHei,sans-serif;background:#faf8f2;color:#173238}h1{font-size:38px}a{display:block;padding:25px;border:1px solid #cbd9cf;border-radius:12px;background:white;color:#0f766e;text-decoration:none}small{color:#60736c}</style></head><body><h1>我的旅行</h1><p>按城市，慢慢计划。</p><a href="上海/"><b>上海 · 轻松旅行 →</b><br><small>10月21–27日上海 · 每日安排 · 路线地图 · 逛吃清单</small></a></body></html>''',encoding='utf-8')
(WORKSPACE/'上海/research/github-export-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(manifest),'total_bytes':sum(x['bytes'] for x in manifest),'largest_file':max(manifest,key=lambda x:x['bytes'])},ensure_ascii=False))
