from pathlib import Path
import json, math, html, urllib.parse, urllib.request, time, zipfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '武康路轻松版'
OUT.mkdir(exist_ok=True)
(OUT / '每日地图').mkdir(exist_ok=True)
notes = json.loads((ROOT/'research/xhs-reviewed.json').read_text(encoding='utf-8'))
# WGS84 approximate area pins; these are not confirmed storefront entrances.
raw = [
('hotel','住宿基地区域·上海图书馆站',31.2073,121.4371,'酒店未选；区域锚点，不代表已预订酒店'),
('wukang','武康大楼',31.2035,121.4304,'外观拍照'),
('court','武康庭',31.2041,121.4307,'短逛与坐下休息'),
('park','in the PARK·安福路322号',31.2091,121.4346,'X03；6号楼1楼，确认在营'),
('ronin','RONIN MADE·安福路275号5弄',31.2093,121.4362,'X04/X06；预约确认后加选'),
('csy','CSYSeLECTED·安福路234号',31.2097,121.4377,'X05；2楼，店方笔记'),
('uru','乌鲁木齐中路·街区',31.2098,121.4394,'只走顺路短段'),
('fumin','蕾虎·富民路184号',31.2176,121.4444,'X03；地址候选，确认在营'),
('julu','巨鹿路·富民路口',31.2201,121.4460,'散步购物替换段'),
('guang','光明邨·淮海中路988号',31.2146,121.4533,'X01/X02；点心候选，门店复核'),
('xin','新天地北里',31.2190,121.4700,'石库门街区短逛'),
('alter','ALTER·马当路245号',31.2177,121.4706,'X03；L116，确认当前入口'),
('yu','豫园商城·九曲桥区域',31.2271,121.4876,'免费公共区与收费园林分开'),
('nanxiang','南翔馒头店·豫园',31.2270,121.4873,'X02/X10；鲜肉小笼'),
('nanjing','南京东路·沈大成区域',31.2352,121.4761,'X02/X10；糕团少量买'),
('bund','外滩·和平饭店段',31.2390,121.4895,'黄昏江景，保留体力'),
('ifc','陆家嘴·国金中心',31.2358,121.4995,'商场午饭与休息'),
('tower','上海中心·三件套外观',31.2329,121.5055,'地面游览；登高只选一个'),
('river','浦东滨江·陆家嘴段',31.2350,121.4953,'短段散步'),
('b','乐园住宿基地区域·康新公路站',31.1291,121.6178,'区域锚点，酒店未选'),
('disney','上海迪士尼·入园区域',31.1430,121.6670,'园内项目用官方App定位，不按城际图导航'),
('pvg','上海浦东国际机场',31.1443,121.8083,'返程示例，航班未定'),
('sha','上海虹桥机场',31.1979,121.3363,'抵达示例，航班未定'),
]
points = {r[0]:dict(id=r[0],name=r[1],lat=r[2],lon=r[3],tip=r[4],coordinate_status='approximate_area_wgs84') for r in raw}
days = [
 dict(id=1,title='抵达与附近晚餐',route=['sha','hotel'],mode='机场交通',meal='酒店周边生煎或面馆，不为网红店跨区',pace='航班抵达后入住，晚上休息',source=['X01','X02']),
 dict(id=2,title='武康安福慢逛',route=['hotel','wukang','court','park','csy','uru','hotel'],optional=['ronin'],mode='街区步行；累了打车',meal='安福路附近简餐＋一杯茶饮；不用打卡所有店',pace='10:30出门；下午坐下45–60分钟；17点左右结束',source=['X03','X04','X05','X06']),
 dict(id=3,title='淮海路与新天地',route=['hotel','guang','xin','alter','hotel'],optional=['fumin','julu'],mode='短段步行＋地铁/打车',meal='光明邨点心少量；味香斋只在地图确认顺路后替换午餐',pace='10:30出门；新天地1小时；不把整条淮海路走完',source=['X01','X02','X03']),
 dict(id=4,title='老城与外滩黄昏',route=['hotel','yu','nanxiang','nanjing','bund','hotel'],mode='跨区地铁/打车；老城与外滩间乘车',meal='南翔或大壶春选一个；沈大成糕团；裕莲茶楼可选',pace='11点左右老城；下午商场坐下休息；黄昏到外滩',source=['X02','X10']),
 dict(id=5,title='陆家嘴与滨江',route=['hotel','ifc','tower','river','hotel'],mode='地铁过江；浦东短段步行',meal='商场午餐；晚上回住宿街区吃本帮菜候选',pace='11点到陆家嘴；登高可选；滨江只走短段',source=['X01']),
 dict(id=6,title='睡到自然醒与转场',route=['hotel','b'],optional=['disney'],mode='退房后带行李打车优先',meal='新酒店附近吃饭；不为夜逛再赶路',pace='午前退房；下午入住B；整理入园用品早睡',source=['X01','X02']),
 dict(id=7,title='迪士尼一日',route=['b','disney','b'],mode='酒店至乐园地铁/可靠接驳/打车',meal='园内午餐坐下；不空腹连排项目',pace='3个主目标＋看秀＋午休；当日官方App查队列',source=['X01','X02']),
 dict(id=8,title='返程',route=['b','pvg'],mode='机场交通',meal='早餐后出发，按航班留足机场时间',pace='优先下午航班；机场与航班确定后重排',source=['X02']),
]
colors=['#64748b','#0f766e','#b45309','#be123c','#1d4ed8','#7c3aed','#c2410c','#475569']
data=dict(status='研究待完成：已有10篇旧小红书审读；本次新增0篇可核正文；目标101篇以上。浏览器启动故障已修复，当前等待小红书重新登录。',assumption='前5晚市区，D6退房；8天7晚为暂定主方案',coordinate_boundary='图钉为WGS84近似区域位置，非核实门店入口；连线仅表示顺序，不表示道路或地铁轨迹。导航按中文POI重新定位。',points=points,days=days,colors=colors)
(OUT/'行程数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

HTML = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>上海武康路轻松旅行·地图草案</title><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><style>body{margin:0;font:16px Microsoft YaHei,Arial;color:#173238;background:#f7f6f0}header{padding:20px 24px;background:#173238;color:white}h1{margin:0 0 8px;font-size:25px}.layout{display:grid;grid-template-columns:350px 1fr;height:calc(100vh - 130px)}aside{padding:20px;overflow:auto}#map{min-height:500px}button{padding:9px 12px;border:1px solid #bbc8c5;background:white;border-radius:7px;margin:4px;cursor:pointer}button.active{background:#17665a;color:white}.alert{padding:10px;background:#fff0ce;font-size:13px;line-height:1.6}.pin{width:28px;height:28px;border-radius:50%;color:white;text-align:center;line-height:28px;border:2px solid white;font-weight:bold}li{margin-bottom:12px;line-height:1.6}a{color:#17665a}.muted{font-size:13px;color:#566967}@media(max-width:750px){.layout{display:flex;flex-direction:column;height:auto}aside{order:2}#map{height:65vh;order:1}}</style></head><body><header><h1>上海轻松旅行 · 武康路住宿基地</h1><div>8天7晚草案｜市区5晚＋乐园附近2晚｜点击日期查看每日路线</div></header><div class="layout"><aside><div class="alert">__STATUS__<br>酒店、航班未定。图钉为近似区域位置；连线是游玩顺序，不是道路导航。</div><div id="buttons"></div><h2 id="title"></h2><div id="pace"></div><ol id="list"></ol><p id="meal"></p><p class="muted" id="source"></p><p class="muted">底图需要联网；底图不可用时请打开同目录离线SVG。高德入口按中文地名搜索，避免坐标系偏差。图中回程连线会重叠，以左侧编号顺序为准。</p></aside><div id="map"></div></div><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>const data=__DATA__; const sources=__SOURCES__;const map=L.map('map');L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);const layers=L.layerGroup().addTo(map);const el=id=>document.getElementById(id);const search=n=>'https://uri.amap.com/search?keyword='+encodeURIComponent(n)+'&city='+encodeURIComponent('上海')+'&view=map';function draw(id){layers.clearLayers();const selected=id?data.days.filter(d=>d.id===id):data.days;const bounds=[];for(const d of selected){const coords=d.route.map(k=>[data.points[k].lat,data.points[k].lon]);bounds.push(...coords);L.polyline(coords,{color:data.colors[d.id-1],weight:id?4:3,dashArray:'8 6'}).addTo(layers);const seen=new Set();d.route.forEach((key,i)=>{if(seen.has(key))return;seen.add(key);const p=data.points[key];L.marker([p.lat,p.lon],{icon:L.divIcon({className:'',html:'<div class="pin" style="background:'+data.colors[d.id-1]+'">'+(id?i+1:'D'+d.id)+'</div>',iconSize:[32,32]})}).bindPopup('<b>'+p.name+'</b><br>'+p.tip+'<br><a target="_blank" rel="noopener" href="'+search(p.name.replace('·街区',''))+'">高德搜索地点</a>').addTo(layers);});if(id)for(const key of d.optional||[]){const p=data.points[key];bounds.push([p.lat,p.lon]);L.circleMarker([p.lat,p.lon],{color:data.colors[d.id-1],radius:8,fillOpacity:.15}).bindPopup('加选：'+p.name+'<br>'+p.tip).addTo(layers);}}map.fitBounds(bounds,{padding:[35,35],maxZoom:16});el('title').textContent=id?'D'+id+'｜'+selected[0].title:'全程路线总览';el('pace').textContent=id?selected[0].pace:'D1–D5住A；D6退房转场；D7乐园；D8返程。';el('list').innerHTML=id?selected[0].route.map((k,i)=>{const p=data.points[k];return '<li><a target="_blank" rel="noopener" href="'+search(p.name)+'">'+p.name+'</a><br><span class="muted">'+p.tip+'</span></li>'}).join(''):selected.map(d=>'<li><b>D'+d.id+' '+d.title+'</b><br>'+d.route.map(k=>data.points[k].name).join(' → ')+'</li>').join('');el('meal').textContent=id?'吃什么：'+selected[0].meal:'';el('source').innerHTML=id?'旧审读来源：'+selected[0].source.map(k=>'<a target="_blank" rel="noopener" href="'+sources[k]+'">'+k+'</a>').join('、'):data.assumption;document.querySelectorAll('button').forEach(b=>b.classList.toggle('active',+b.dataset.day===id));}el('buttons').innerHTML=[0,...data.days.map(d=>d.id)].map(i=>'<button type="button" data-day="'+i+'">'+(i?'D'+i:'全程')+'</button>').join('');el('buttons').addEventListener('click',e=>{if(e.target.dataset.day!==undefined)draw(+e.target.dataset.day)});draw(__DAY__);</script></body></html>'''
source_urls={n['id']:n['url'] for n in notes}
for day in range(9):
    rendered=HTML.replace('__STATUS__',html.escape(data['status'])).replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__SOURCES__',json.dumps(source_urls)).replace('__DAY__',str(day))
    name=OUT/'全程与每日互动地图.html' if day==0 else OUT/'每日地图'/f'D{day:02d}-路线地图.html'
    name.write_text(rendered,encoding='utf-8')

# Geographical offline overview: Mercator projection, true north and scale.
def svg_map(day):
    selected=days if not day else [days[day-1]]
    keys=list(dict.fromkeys(k for d in selected for k in d['route']+d.get('optional',[])))
    def proj(p):return p['lon'],math.degrees(math.log(math.tan(math.pi/4+math.radians(p['lat'])/2)))
    xy={k:proj(points[k]) for k in keys}
    minx=min(v[0] for v in xy.values());maxx=max(v[0] for v in xy.values());miny=min(v[1] for v in xy.values());maxy=max(v[1] for v in xy.values())
    dx=max(maxx-minx,.018);dy=max(maxy-miny,.018);cx=(minx+maxx)/2;cy=(miny+maxy)/2
    scale=min(1130/dx,670/dy)*.85
    def pos(k):x,y=xy[k];return 640+(x-cx)*scale,445-(y-cy)*scale
    title='全程总览' if not day else f'D{day} '+days[day-1]['title']
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050">','<rect width="1600" height="1050" fill="#faf8f2"/>',f'<text x="55" y="64" font-family="Microsoft YaHei" font-size="35" fill="#173238">上海轻松旅行｜{html.escape(title)}</text>','<text x="55" y="103" font-family="Microsoft YaHei" font-size="18" fill="#596c6a">近似地理位置 · 北向上 · 连线仅为游玩顺序，非道路导航 · 酒店和航班未定</text>','<rect x="40" y="135" width="1200" height="710" rx="10" fill="#edf3ef"/>']
    legend=[]
    for d in selected:
        line=' '.join(f'{pos(k)[0]:.1f},{pos(k)[1]:.1f}' for k in d['route'])
        out.append(f'<polyline points="{line}" fill="none" stroke="{colors[d["id"]-1]}" stroke-width="4" stroke-dasharray="10 7"/>')
        if not day:legend.append(f'D{d["id"]} {d["title"]}')
    for i,k in enumerate(keys):
        x,y=pos(k);p=points[k]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="#17665a" stroke="white" stroke-width="2"/><text x="{x:.1f}" y="{y+5:.1f}" text-anchor="middle" font-family="Arial" font-size="13" fill="white">{i+1}</text>')
        # Numbered key keeps dense nearby shops readable.
        ly=170+i*27
        out.append(f'<text x="1260" y="{ly}" font-family="Microsoft YaHei" font-size="16" fill="#173238">{i+1}. {html.escape(p["name"])}</text>')
    out.append('<text x="1170" y="182" font-family="Arial" font-size="28" fill="#173238">N ↑</text>')
    if day:
        lines=[' → '.join(str(keys.index(k)+1) for k in selected[0]['route']),selected[0]['mode'],selected[0]['pace']]
    else:lines=['  /  '.join(legend[:4]),'  /  '.join(legend[4:]),'机场为示例；A、B为住宿区域锚点，不代表选定酒店。']
    for j,t in enumerate(lines):out.append(f'<text x="55" y="{895+j*38}" font-family="Microsoft YaHei" font-size="22" fill="#173238">{html.escape(t)}</text>')
    # scale bar uses Mercator longitude scale at mean latitude
    lat=sum(points[k]['lat'] for k in keys)/len(keys);km_per_deg=111.32*math.cos(math.radians(lat));km=1 if day in [2,3,4,5] else 5;bar=km/km_per_deg*scale
    out.append(f'<path d="M 75 798 h {bar:.1f}" stroke="#173238" stroke-width="4"/><text x="75" y="780" font-family="Microsoft YaHei" font-size="16">约 {km} km</text>')
    out.append('</svg>');return ''.join(out)
for day in range(9):
    name=OUT/'00-全程地理路线.svg' if not day else OUT/'每日地图'/f'D{day:02d}-地理路线.svg'
    name.write_text(svg_map(day),encoding='utf-8')

ledger='# 小红书研究台账｜待补全\n\n目标：101篇以上去重、实际正文审读。当前只有旧项目10篇审读记录，本次新增0篇可核正文。不能称为100篇研究成果。\n\n2026-10-14访问记录：浏览器两次启动失败；node_repl再次检测提示Windows沙箱初始化失败；网页搜索工具无法打开两篇已有笔记，专题页请求超时。搜索摘要与其他平台转载不计入。\n\n|编号|标题|类型|采用信息|限制|\n|---|---|---|---|---|\n'
for n in notes:ledger+=f'|{n["id"]}|[{n["title"]}]({n["url"]})|{n["kind"]}|{n["adopt"]}|{n["reject"]}|\n'
ledger+='\n后续每篇记录：规范链接、作者、可见日期、正文读取范围、商户和地址、路线、避雷、推广迹象、采用/排除理由。图片攻略要读图；仅标签、短视频未看完整、广告重复与严重错误不计。自称“本地人”不等于身份核实。\n'
ledger+='\n访问恢复进展：上海目录所有者从CodexSandboxOffline恢复为Administrator，修复时访问权限列表不变。浏览器工具已正常启动；小红书页面显示“电脑设备登录超限，请重新登录”，等待用户扫码重新登录。\n'
(OUT/'小红书研究台账-待补全.md').write_text(ledger,encoding='utf-8')
print(json.dumps({'output':str(OUT),'maps_html':9,'maps_svg':9,'old_xhs_records':len(notes),'new_xhs_read':0},ensure_ascii=False))
