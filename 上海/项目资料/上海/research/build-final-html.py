from pathlib import Path
import hashlib
import html
import json
import math
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "武康路轻松版"
data = json.loads((OUT / "行程数据.json").read_text(encoding="utf-8"))
views = json.loads((OUT / "地图资源/地图视图.json").read_text(encoding="utf-8"))
asset_version = hashlib.sha256(
    (OUT / "地图资源/map-context.js").read_bytes()
    +
    (OUT / "地图资源/map-ui.js").read_bytes()
    + (OUT / "地图资源/map-ui.css").read_bytes()
    + (OUT / "地图资源/地图视图.json").read_bytes()
).hexdigest()[:10]
raw_places = json.loads((ROOT / "research/map-place-pins.json").read_text(encoding="utf-8"))


def gcj_to_wgs(lat, lon):
    """Approximate inversion for display; store navigation still uses the POI name."""
    x, y = lon - 105, lat - 35
    dlat = -100 + 2*x + 3*y + .2*y*y + .1*x*y + .2*math.sqrt(abs(x))
    dlat += (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi))*2/3
    dlat += (20*math.sin(y*math.pi) + 40*math.sin(y/3*math.pi))*2/3
    dlat += (160*math.sin(y/12*math.pi) + 320*math.sin(y*math.pi/30))*2/3
    dlon = 300 + x + 2*y + .1*x*x + .1*x*y + .1*math.sqrt(abs(x))
    dlon += (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi))*2/3
    dlon += (20*math.sin(x*math.pi) + 40*math.sin(x/3*math.pi))*2/3
    dlon += (150*math.sin(x/12*math.pi) + 300*math.sin(x/30*math.pi))*2/3
    rad = lat*math.pi/180
    magic = 1-.006693421622965943*math.sin(rad)**2
    root = math.sqrt(magic)
    dlat = dlat*180/((6378245*(1-.006693421622965943)/(magic*root))*math.pi)
    dlon = dlon*180/(6378245/root*math.cos(rad)*math.pi)
    return lat-dlat, lon-dlon


places = []
for item in raw_places:
    pin = item.copy()
    if "gcj" in pin:
        pin["lat"], pin["lon"] = gcj_to_wgs(*pin.pop("gcj"))
        pin["approximate"] = False
    elif "gcj_area" in pin:
        pin["lat"], pin["lon"] = gcj_to_wgs(*pin.pop("gcj_area"))
        pin["approximate"] = True
    else:
        anchor = data["points"][pin.pop("anchor")]
        pin["lat"], pin["lon"] = anchor["lat"], anchor["lon"]
        pin["approximate"] = True
    places.append(pin)
(OUT / "地图资源/店铺点位.json").write_text(json.dumps(places, ensure_ascii=False, indent=2), encoding="utf-8")

page = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>上海轻松旅行｜每日路线地图</title>
<link rel="stylesheet" href="__PREFIX__地图资源/leaflet.css"><link rel="stylesheet" href="__PREFIX__地图资源/map-ui.css?v=__VERSION__"></head><body>
<header><nav class="site-nav" aria-label="主要导航"><a href="__PREFIX__index.html">旅行计划</a><a href="__PREFIX__全程与每日互动地图.html" aria-current="page">路线地图</a><a href="__PREFIX__美食与逛店清单.html">逛吃清单</a></nav><h1>上海轻松旅行 · 一张地图看全程</h1><p>放大看市区，移到迪士尼再放大看乐园内；也可直接选日期或点按钮</p></header>
<div class="controls"><label class="date-picker">查看某一天<select id="day-select" aria-label="每日路线"><option value="">选择一天</option>__DAYS__</select></label><div class="view-buttons" id="buttons" aria-label="地图范围"></div><span class="zoom-hint">拖动／缩放自动切换</span><fieldset class="filters"><legend>地图标记</legend><label><input type="checkbox" data-kind="food" checked> <span class="key food">吃</span> 餐饮</label><label><input type="checkbox" data-kind="tea" checked> <span class="key tea">茶</span> 茶饮</label><label><input type="checkbox" data-kind="shop" checked> <span class="key shop">逛</span> 买手店</label></fieldset><label class="online"><input type="checkbox" id="online" checked> 联网底图（断网显示离线图）</label></div>
<div class="layout"><aside><p class="eyebrow">景点与街区路线</p><h2 id="title"></h2><p id="pace"></p><p class="muted" id="mode"></p><ol id="list"></ol><details id="park-plan" class="park-plan" hidden><summary>10/27 早享时间线与排队切换</summary><p>以当天官方开园时刻 <b>O</b> 为基准。若 O=8:30，建议约6:30到指定早享入口；酒店出发时间另加车程与步行。</p><ol><li><b>早享 O−60～O</b>：矿山车≤25分先玩，随后热力≤30分再排；否则创极速≤20分先玩。途经矿山车／热力均超阈值就直走宝藏湾。</li><li><b>开园后前2小时</b>：沿动物城→宝藏湾→探险岛走。加勒比≤25分、飞越≤45分就排。</li><li><b>午后</b>：宝藏湾看「风暴来临」＋错峰午饭，坐下休息45–60分钟；再选短队项目。</li><li><b>傍晚</b>：复查漏掉的高排队项目；≤45分再补。烟花／城堡秀按当天时刻。</li></ol><p>项目开放、队列及演出以<a target="_blank" rel="noopener" href="https://www.shanghaidisneyresort.com/zh-cn/information/download-shanghai-disney-mobile-app">官方App</a>为准；<a target="_blank" rel="noopener" href="__PREFIX__迪士尼早享56篇审读索引.html">56篇笔记与取舍</a>。</p></details><p id="optional"></p><p id="meal"></p><details id="places-panel" open><summary>参考店铺 · 不作路线站 <span id="place-count"></span></summary><ul id="places-list"></ul></details><details class="references"><summary>研究来源</summary><div id="source"></div></details><p class="note">「住·海友」是已定市区酒店位置，不接每日景点线路。虚线只连景点与旅游街区，表示游玩顺序；跨区乘车。餐饮、茶饮和买手店只显示位置。图钉若标“街区位置”，请按门牌重新导航；营业与分店以当天为准。</p><a id="static" target="_blank" rel="noopener">下载当前离线地图</a></aside><div id="map"><img id="fallback" alt="离线路线地图"></div></div>
<script>window.JOURNEY_MAP={data:__DATA__,views:__VIEWS__,places:__PLACES__,initial:__DAY__,prefix:"__PREFIX__",version:"__VERSION__"};</script><script src="__PREFIX__地图资源/leaflet.js"></script><script src="__PREFIX__地图资源/map-context.js?v=__VERSION__"></script><script src="__PREFIX__地图资源/map-ui.js?v=__VERSION__"></script></body></html>"""

model = json.loads((OUT / '地图资源/迪士尼排队模型.json').read_text(encoding='utf-8'))
def schedule_rows(rides):
    return ''.join(
        '<tr><td>' + html.escape(r['time']).replace('–', '<br>–') + '</td>'
        '<td><b>' + html.escape(data['points'][r['key']]['name']) + '</b><small>实显≤' + str(r['threshold']) + '分再排</small></td>'
        '<td><b>' + str(r['queue'][0]) + '–' + str(r['queue'][1]) + '</b>分</td>'
        '<td><small>' + ('入口→' if r['from'] == 'disney' else '上站→') + '约' + str(r['distance_m']) + '米</small>'
        '步' + str(r['walk'][0]) + '–' + str(r['walk'][1]) + '分<br>玩' + str(r['experience'][0]) + '–' + str(r['experience'][1]) + '分</td></tr>'
        for r in rides
    )

ride_rows = schedule_rows(model['rides'])
alt_ride_rows = schedule_rows(model['mine_first']['rides'])
hot_ride_rows = schedule_rows(model['hot_first']['rides'])
heat_rows = ''.join(
    '<tr><td><a target="_blank" rel="noopener" href="' + html.escape(r['source']) + '">' + html.escape(r['name']) + '</a></td>'
    '<td>' + str(r['h8']) + '</td><td>' + str(r['h10']) + '</td><td>' + str(r['h20']) + '</td></tr>'
    for r in model['heatmap']
)
park_markup = '''<section id="park-plan" class="park-plan" hidden><h3>10/27 · 7:30早享热门八项</h3>
<div class="park-variants" role="group" aria-label="选择迪士尼早享路线"><button type="button" data-park-variant="tron" aria-pressed="true">A · 创极速先玩</button><button type="button" data-park-variant="mine" aria-pressed="false">B · 矿山车先玩</button><button type="button" data-park-variant="hot" aria-pressed="false">C · 热力先玩</button></div>
<div data-park-content="tron">
<p class="park-lead">6:30–6:45到指定早享入口；前五项约<b>12:00–13:45</b>完成，八项含30分钟午饭约<b>15:45–18:40</b>完成。按表中间情景走，超时就压缩演出和其他加项。</p>
<div class="park-table-scroll"><table class="park-schedule"><thead><tr><th>时段</th><th>项目 / 当场阈值</th><th>预计排队</th><th>移动 / 体验</th></tr></thead><tbody>__RIDE_ROWS__</tbody></table></div>
<p class="park-small">12:35–13:05在探险岛附近快餐。距离按两点直线距离×1.35估算，不是园区道路导航；入园闸机位置与项目队尾会影响实走时长。抱抱龙高刺激、雷鸣山可能打湿衣物。体验含上下载具与前导。</p>
<div class="park-afternoon"><p><b>16:55–17:25</b> 晚饭、补水；项目延误就按实际出队时间顺延。</p><p><b>17:25–19:30</b> 优先补漏掉的热门；有余量再选巴斯≤15分、胡迪≤35分，或宝藏湾「风暴来临」合适场次。</p><p><b>当晚至闭园</b> 按官方App在烟花与再刷一项间取舍；演出和闭园时刻尚待公布。</p></div>
</div><div data-park-content="mine" hidden>
<p class="park-lead">创极速早享未开放或实显&gt;25分，且矿山车开放、实显≤25分时选这条。6:30–6:45到入口；八项含午饭估计<b>16:40–19:45</b>完成，晚于A线也可能来不及全部玩完。</p>
<div class="park-table-scroll"><table class="park-schedule"><thead><tr><th>时段</th><th>项目 / 当场阈值</th><th>预计排队</th><th>移动 / 体验</th></tr></thead><tbody>__ALT_RIDE_ROWS__</tbody></table></div>
<p class="park-small">13:40–14:10在探险岛附近快餐。距离按两点直线距离×1.35估算，非道路导航。热力&gt;60分先转创极速；创极速&gt;80分先走宝藏湾、晚间再补。</p>
<div class="park-afternoon"><p><b>18:05后</b> 先吃晚饭；八项若有遗漏，优先补漏。</p><p><b>有余量</b> 再选巴斯、胡迪或「风暴来临」；实际演出场次与闭园时间以官方App为准。</p></div>
</div><div data-park-content="hot" hidden>
<p class="park-lead">C · 条件次优线：热力追踪早享开放且实显≤30分，而创极速与矿山车都&gt;25分时选。沿相邻园区走，八项含午饭估计<b>16:25–19:45</b>完成；创极速留在最后，存在下午排队升高风险。</p>
<div class="park-table-scroll"><table class="park-schedule"><thead><tr><th>时段</th><th>项目 / 当场阈值</th><th>预计排队</th><th>移动 / 体验</th></tr></thead><tbody>__HOT_RIDE_ROWS__</tbody></table></div>
<p class="park-small">13:10–13:40在探险岛附近快餐。距离为近似点位直线×1.35，不是道路导航。热力若&gt;30分，改选A/B中更短的首站；创极速约16:20到达时若&gt;95分，确认仍营业后晚间复查，不能保证八项全完成。</p>
<div class="park-afternoon"><p><b>18:00后</b> 晚饭、补水，优先补漏掉的热门。</p><p><b>有余量</b> 再选短队或演出；闭园与项目时刻以官方App为准。</p></div>
</div><details class="park-evidence"><summary>排队热力、计算与改线</summary><p>2026年历史逐小时平均排队（分钟），用于判断早、午、晚变化；8点数据不能直接当7:30早享队列。最近的10/13周二客流为59%，10/27仍未知。</p><table class="park-heat"><thead><tr><th>项目</th><th>8点</th><th>10点</th><th>20点</th></tr></thead><tbody>__HEAT_ROWS__</tbody></table><p>A线八项：排队310–445分＋步行55–73分＋体验97–120分＋午饭30分，约15:45–18:40。B线八项：排队360–500分＋步行63–84分＋体验97–120分＋午饭30分，约16:40–19:45。C线八项：排队355–505分＋步行54–73分＋体验97–120分＋午饭30分，约16:25–19:45。三组均是粗略规划区间，10/27现场客流未知。任一站超过表中阈值就在App记为候补、先去下一站；抱抱龙队长时可在19点后复查。</p><p><a target="_blank" rel="noopener" href="https://queue-times.com/en-US/parks/30/stats/2026?hide_archived=true">2026年均值</a>、<a target="_blank" rel="noopener" href="https://queue-times.com/en-US/parks/30/calendar">近期同周二客流</a>、<a target="_blank" rel="noopener" href="__PREFIX__迪士尼早享56篇审读索引.html">56篇早享笔记</a>、<a target="_blank" rel="noopener" href="https://static.shanghaidisneyresort.com/web-img-gallery/park-map-260227.pdf">官方园区图</a>。10/26晚核对<a target="_blank" rel="noopener" href="https://www.shanghaidisneyresort.com/zh-cn/information/download-shanghai-disney-mobile-app">官方App</a>的开放与演出。</p></details></section>'''
park_markup = park_markup.replace('__RIDE_ROWS__', ride_rows).replace('__ALT_RIDE_ROWS__', alt_ride_rows).replace('__HOT_RIDE_ROWS__', hot_ride_rows).replace('__HEAT_ROWS__', heat_rows)
page = re.sub(r'<details id="park-plan".*?</details>', park_markup, page, count=1, flags=re.S)

days_options = "".join(
    f'<option value="{d["id"]}">第{["零", "一", "二", "三", "四", "五", "六", "七", "八"][d["id"]]}天 · {d["date"]} {d["title"]}</option>'
    for d in data["days"]
)
for view_id in range(11):
    if view_id == 0:
        destination, prefix = OUT / "全程与每日互动地图.html", ""
    elif view_id == 9:
        destination, prefix = OUT / "市区互动地图.html", ""
    elif view_id == 10:
        destination, prefix = OUT / "每日地图/D07-园内路线.html", "../"
    else:
        destination = OUT / "每日地图" / f"D{view_id:02d}-路线地图.html"
        prefix = "../"
    content = (page.replace("__PREFIX__", prefix)
                   .replace("__DAYS__", days_options)
                   .replace("__DATA__", json.dumps(data, ensure_ascii=False))
                   .replace("__VIEWS__", json.dumps(views, ensure_ascii=False))
                   .replace("__PLACES__", json.dumps(places, ensure_ascii=False))
                   .replace("__DAY__", str(view_id))
                   .replace("__VERSION__", asset_version))
    destination.write_text(content, encoding="utf-8")

# Preserve exact original note links in the long-form reading copies.
for filename in ["上海轻松旅行方案.md", "美食与逛店清单.md"]:
    item = OUT / filename
    source = item.read_text(encoding="utf-8")
    source = re.sub(
        r"(?<!\[)R\d{3}(?!\])",
        lambda match: f'[{match[0]}]({data["sources"][match[0]]})'
        if match[0] in data["sources"] else match[0],
        source,
    )
    item.write_text(source, encoding="utf-8")

node = r"C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
subprocess.run([node, str(ROOT / "research/render-final-markdown.mjs")], check=True)
subprocess.run([node, str(ROOT / "research/build-site-home.mjs")], check=True)
print(json.dumps({"interactive_views": 11, "place_pins": len(places)}, ensure_ascii=False))
