from __future__ import annotations

import datetime as dt
import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '武康路轻松版'
REVIEWS = ROOT / 'research/disney-early-notes-2026-10-14.json'
data_file = OUT / '行程数据.json'
views_file = ROOT / 'research/map-views.json'

notes = json.loads(REVIEWS.read_text(encoding='utf-8'))
# Search hits whose visible text was a question, character-meet record, non-early
# itinerary, or image-only post do not count as an analyzed early-entry guide.
excluded = {3, 16, 21, 23, 27, 31, 57, 58, 59, 60, 62, 63, 69}
accepted = [n for i, n in enumerate(notes, 1) if i not in excluded]
assert len(accepted) >= 50 and len({n['id'] for n in accepted}) == len(accepted)

def published(n):
    return dt.datetime.fromtimestamp(int(n['id'][:8], 16), dt.timezone.utc).date()

accepted.sort(key=published, reverse=True)
terms = {
    '矿山车': ('小矮人', '矿车', '矿山车'),
    '热力追踪': ('热力追踪', '动物城'),
    '创极速光轮': ('极速光轮', '创极速', '极创'),
    '飞越地平线': ('飞越', '飞跃', '翱翔'),
    '加勒比海盗': ('加勒比', '沉落宝藏'),
    '雷鸣山': ('雷鸣山', '漂流'),
    '演出/烟花': ('风暴来临', '花车', '烟花'),
}

def tags(n):
    body = n['body']
    found = [k for k, words in terms.items() if any(w in body for w in words)]
    return ' · '.join(found[:5]) if found else '入园时间与体力'

audit = {
    'checked_at': '2026-10-14',
    'visible_notes_opened': len(notes),
    'usable_distinct_early_entry_notes': len(accepted),
    'excluded_search_results': [{'id': notes[i-1]['id'], 'title': notes[i-1]['title']} for i in sorted(excluded)],
    'method': '逐篇打开小红书网页并阅读可见文字正文；仅正文有早享游玩/入园可用信息的独立笔记计数。未逐张审读图片，视频未完整观看。展示的项目提及次数不是推荐票数。',
    'mention_counts': {k: sum(any(w in n['body'] for w in words) for n in accepted) for k, words in terms.items()},
    'notes': [{'id': n['id'], 'title': n['title'], 'url': f"https://www.xiaohongshu.com/explore/{n['id']}",
               'visible_date': n['date'], 'published_date_inferred_from_id': str(published(n)),
               'visible_body_chars': len(n['body']), 'topics': tags(n)} for n in accepted],
}
(ROOT / 'research/disney-early-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

reference = lambda id: f'https://www.xiaohongshu.com/explore/{id}'
focus = {
    'TRON逆向首站': '6ac65163000000001500939f',
    '人多时矿山车后果断改线': '69eecf5a000000002301c0b4',
    '两位成年人完整时间线': '6a9fdca8000000002800368c',
    '热力追踪晚间回落实测': '6a6570df0000000001031155',
    '10月2日早享实测': '6ac115d9000000001a029b60',
    '酒店班车错过早享优势': '6a8cf4600000000023012cc5',
}
rows = []
for i, n in enumerate(accepted, 1):
    href = reference(n['id'])
    rows.append(f'<tr><td>{i:02d}</td><td><a target="_blank" rel="noopener" href="{href}">{html.escape(n["title"])}</a></td>'
                f'<td>{html.escape(n["date"] or "页面未显示")}</td><td>{html.escape(tags(n))}</td></tr>')
site_css = '<style>body{font:16px/1.7 "Microsoft YaHei",sans-serif;background:#faf8f2;color:#173238;margin:0}.wrap{max-width:1050px;margin:auto;padding:28px}a{color:#0f766e}.top{display:flex;gap:20px;align-items:center}.top a{text-decoration:none}h1{font-size:clamp(30px,5vw,52px);line-height:1.12}h2{margin-top:36px}p{max-width:850px}table{width:100%;border-collapse:collapse;background:white}th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #dce5df}th{position:sticky;top:0;background:#e8f0ea}.small{color:#5c7069;font-size:14px}.chips{display:flex;flex-wrap:wrap;gap:8px}.chips span{background:#e4ede7;border-radius:20px;padding:5px 12px}@media(max-width:650px){.wrap{padding:18px}table{font-size:13px}th,td{padding:6px}.date{display:none}}</style>'
summary = f'''<p>2026-10-14 逐篇打开小红书 {len(notes)} 篇早享相关搜索结果，保留 {len(accepted)} 篇有可用文字的独立笔记；图片未逐张审读，视频未完整观看。下面的项目统计只计“正文提到”，不能当作推荐票数或 10 月 27 日实时排队。</p>
<div class="chips"><span>矿山车 {audit['mention_counts']['矿山车']}</span><span>热力追踪 {audit['mention_counts']['热力追踪']}</span><span>创极速 {audit['mention_counts']['创极速光轮']}</span><span>飞越 {audit['mention_counts']['飞越地平线']}</span><span>加勒比 {audit['mention_counts']['加勒比海盗']}</span></div>
<h2>归纳后采用的规则</h2><ul>
<li>你们票面早享时间为 7:30；建议 6:30–6:45 到指定早享入口，酒店出发时间把实际车程和安检缓冲倒推。<a href="{reference(focus['酒店班车错过早享优势'])}">实游记录</a>。</li>
<li>高价值的早享站是矿山车、创极速与热力追踪；矿山车与热力常被首冲。默认先到创极速，再向北到矿山车和热力，避免稍晚才回到创极速。若创极速暂未开放或排队已超过 25 分，改先玩矿山车。<a href="{reference(focus['TRON逆向首站'])}">逆向实测</a>、<a href="{reference(focus['人多时矿山车后果断改线'])}">高客流改线实测</a>。</li>
<li>同一组人也可能早享入园偏晚。不要为原计划在已涨到 60–90 分的项目门口继续等；晚间再复查或按预算考虑官方单项尊享。<a href="{reference(focus['10月2日早享实测'])}">10月2日记录</a>、<a href="{reference(focus['热力追踪晚间回落实测'])}">晚间热力记录</a>。</li>
<li>加勒比通常比矿山车、热力、创极速更容易在白天或傍晚补；剧场和午餐适合穿插在宝藏湾。2026年整体排队数据也支持把早享优先留给高排队项目。</li>
<li>本次两位成年人以八个热门项目为全天目标；演出和低队列加项按现场余量决定。表内时刻是中间情景，不为赶表奔跑；热门项目超阈值时改排附近短队。<a href="{reference(focus['两位成年人完整时间线'])}">两人时间线</a>。</li></ul>'''
index_html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>迪士尼早享攻略审读｜上海轻松旅行</title>'+site_css+'</head><body><div class="wrap"><nav class="top"><a href="index.html">← 旅行计划</a><a href="每日地图/D07-园内路线.html">D7 园内路线</a></nav><h1>迪士尼早享：逐篇审读</h1>'+summary+'<h2>来源索引</h2><p class="small">日期照录网页显示；同名笔记按不同笔记 ID 去重。只列标题、来源与涉及项目，不复制笔记正文。</p><table><thead><tr><th>#</th><th>笔记</th><th>页面日期</th><th>正文涉及</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><p class="small">近期排队与园区营业以<a href="https://www.shanghaidisneyresort.com/zh-cn/information/download-shanghai-disney-mobile-app">上海迪士尼官方 App</a>为准；历史数据参考 <a href="https://queue-times.com/parks/30/stats/2026">Queue Times 2026</a>。</p></div></body></html>'
(OUT / '迪士尼早享56篇审读索引.html').write_text(index_html, encoding='utf-8')

data = json.loads(data_file.read_text(encoding='utf-8'))
data['points']['mine'] = {
    'id': 'mine', 'name': '七个小矮人矿山车', 'lat': 31.1476, 'lon': 121.6550,
    'tip': '主线早享第二站；备用线首站。主线显示≤40分钟、备用线显示≤25分钟时排，超出先去下一项。',
    'coordinate_status': 'Queue Times 标注的 OSM 近似坐标；入口请用官方 App',
    'coordinate_source': 'https://queue-times.com/parks/30/rides/2990',
}
data['points']['tron']['name'] = '创极速光轮'
data['points']['tron']['tip'] = '7:30早享首站；运行且显示≤25分钟就排，过长或暂未开放则先去矿山车。刺激项目，不适合者跳过。'
data['points']['hot']['tip'] = '矿山车旁第三站；显示≤70分钟就排，较长则晚间复查。'
data['points']['pirate']['tip'] = '宝藏湾顺路补；显示≤45分钟就排，较长可在傍晚补。'
data['points']['soar']['tip'] = '探险岛顺路补；显示≤75分钟就排，较长留待晚间复查。'
data['points']['rapids'] = {
    'id': 'rapids', 'name': '雷鸣山漂流', 'lat': 31.1449, 'lon': 121.6590,
    'tip': '探险岛第六个热门目标；显示≤60分钟且愿意可能打湿衣物时排。',
    'coordinate_status': 'Queue Times 标注的 OSM 近似坐标；入口以官方 App 为准',
    'coordinate_source': 'https://queue-times.com/en-US/parks/30/rides/2986/2026',
}
data['points']['buzz'] = {
    'id': 'buzz', 'name': '巴斯光年星际营救', 'lat': 31.1431, 'lon': 121.6530,
    'tip': '傍晚明日世界可选加项；显示≤15分钟再玩，不为此专程折返。',
    'coordinate_status': 'Queue Times 标注的 OSM 近似坐标；入口以官方 App 为准',
    'coordinate_source': 'https://queue-times.com/en-US/parks/30/rides/2999/2026',
}
data['points']['peter'] = {
    'id': 'peter', 'name': '小飞侠天空奇遇', 'lat': 31.1454, 'lon': 121.6540,
    'tip': '梦幻世界第七站；显示≤50分钟就排，超出则转抱抱龙或傍晚再查。',
    'coordinate_status': 'Queue Times 标注的 OSM 近似坐标；入口以官方 App 为准',
    'coordinate_source': 'https://queue-times.com/en-US/parks/30/rides/2989/2026',
}
data['points']['rex'] = {
    'id': 'rex', 'name': '抱抱龙冲天赛车', 'lat': 31.14574, 'lon': 121.65231,
    'tip': '玩具总动员园区第八站；显示≤90分钟且能接受高刺激再排；偏长可19:00后复查。',
    'coordinate_status': 'OSM 近似坐标；入口以官方 App 为准',
    'coordinate_source': 'https://www.openstreetmap.org/node/5599528012',
}
data['points']['storm'] = {
    'id': 'storm', 'name': '风暴来临·凡迭戈剧院', 'lat': 31.147743, 'lon': 121.65961,
    'tip': '宝藏湾室内演出，约30分钟；场次和是否开放以当日官方 App 为准。',
    'coordinate_status': '剧院位置约数；以官方 App 地图上的入口为准',
    'coordinate_source': 'https://www.shanghaidisneyresort.com/zh-cn/experience/entertainment/eye-of-storm-captain-jacks-spectacular',
}
data['points']['castle'] = {
    'id': 'castle', 'name': '奇幻童话城堡·夜间演出区域', 'lat': 31.14574, 'lon': 121.65533,
    'tip': '晚间演出或拍照收尾；10月27日演出和闭园时刻尚待官方公布。',
    'coordinate_status': 'OSM 城堡主体近似坐标；具体观演区以现场为准',
    'coordinate_source': 'https://static.shanghaidisneyresort.com/web-img-gallery/park-map-260227.pdf',
}
route = ['disney', 'tron', 'mine', 'hot', 'pirate', 'soar', 'rapids', 'peter', 'rex', 'castle', 'disney']
mine_route = ['disney', 'mine', 'hot', 'tron', 'pirate', 'soar', 'rapids', 'peter', 'rex', 'castle', 'disney']
hot_route = ['disney', 'hot', 'mine', 'pirate', 'soar', 'rapids', 'peter', 'rex', 'tron', 'castle', 'disney']
data['park'].update({
    'title': '迪士尼园内·7:30早享热门八项', 'route': route, 'optional': ['storm', 'buzz'],
    'mode': '主线：入口→创极速→矿山车→热力→加勒比→飞越→雷鸣山→小飞侠→抱抱龙→城堡→出口；虚线只表示顺序。',
    'meal': '12:35–13:05附近快餐，17:00左右简短晚饭；项目慢于计划就优先删演出与低队列加项。',
    'pace': '7:30早享；建议6:30–6:45到入口。前五项预计12:00–13:45完成；八项连午饭约15:45–18:40完成。',
    'source': ['D001', 'D002', 'D003', 'D004', 'Q2026', 'QHEAT', 'QCAL', 'QRAP', 'QPAN', 'QREX', 'OAPP', 'OMAP'],
})
data['park']['mine_first'] = {
    'title': '迪士尼园内·矿山车先玩备用', 'route': mine_route, 'optional': ['storm', 'buzz'],
    'mode': '备用线：入口→矿山车→热力→创极速→加勒比→飞越→雷鸣山→小飞侠→抱抱龙→城堡→出口；虚线只表示顺序。',
    'meal': '约13:40–14:10在探险岛附近快餐；项目慢于计划就优先删演出和低队列加项。',
    'pace': '当创极速早享关闭或排队>25分钟、而矿山车开放且≤25分钟时启用；八项连午饭约16:40–19:45完成。',
    'source': data['park']['source'],
}
data['park']['hot_first'] = {
    'title': '迪士尼园内·热力追踪首站备用C', 'route': hot_route, 'optional': ['storm', 'buzz'],
    'mode': 'C线：入口→热力追踪→矿山车→加勒比→飞越→雷鸣山→小飞侠→抱抱龙→创极速→城堡→出口；虚线只表示顺序。',
    'meal': '约13:10–13:40在探险岛附近快餐；热门八项优先，演出和其他项目只在有余量时加。',
    'pace': '热力开放且实显≤30分钟，创极速和矿山车均>25分钟时启用；八项含午饭约16:25–19:45完成。',
    'source': data['park']['source'],
}
day = next(d for d in data['days'] if d['id'] == 7)
day['title'] = '迪士尼早享·热门项目尽量多玩'
day['mode'] = '早享票 7:30 入园；建议6:30–6:45到指定入口。10/26晚核对官方项目开放、演出和闭园时刻。'
day['meal'] = '园内快餐、短休息；演出与低队列项目按现场余量决定。'
day['pace'] = '先抢创极速、矿山车、热力；下午接雷鸣山、小飞侠、抱抱龙。点「园内」看逐时表。'
day['source'] = data['park']['source']
data['sources'].update({
    'D001': reference('6ac65163000000001500939f'),
    'D002': reference('69eecf5a000000002301c0b4'),
    'D003': reference('6a9fdca8000000002800368c'),
    'D004': reference('6ac115d9000000001a029b60'),
    'Q2026': 'https://queue-times.com/parks/30/stats/2026',
    'QHEAT': 'https://queue-times.com/en-US/parks/30/rides/2990/2026',
    'QCAL': 'https://queue-times.com/en-US/parks/30/calendar',
    'QRAP': 'https://queue-times.com/en-US/parks/30/rides/2986/2026',
    'QPAN': 'https://queue-times.com/en-US/parks/30/rides/2989/2026',
    'QREX': 'https://queue-times.com/en-US/parks/30/rides/5633/2026',
    'OAPP': 'https://www.shanghaidisneyresort.com/zh-cn/information/download-shanghai-disney-mobile-app',
    'OMAP': 'https://static.shanghaidisneyresort.com/web-img-gallery/park-map-260227.pdf',
    'OSTORM': 'https://www.shanghaidisneyresort.com/zh-cn/experience/entertainment/eye-of-storm-captain-jacks-spectacular',
})
data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

views = json.loads(views_file.read_text(encoding='utf-8'))
park = next(v for v in views if v['id'] == 10)
park['title'] = data['park']['title']
park['keys'] = ['disney', 'tron', 'mine', 'hot', 'pirate', 'soar', 'rapids', 'peter', 'rex', 'castle', 'storm', 'buzz']
park['routes'] = [{'route': route, 'color': '#c2410c'}]
park['description'] = data['park']
mine_view = next((v for v in views if v['id'] == 11), None)
if mine_view is None:
    mine_view = {'id': 11}
    views.append(mine_view)
mine_view.update({
    'title': data['park']['mine_first']['title'],
    'keys': ['disney', 'mine', 'hot', 'tron', 'pirate', 'soar', 'rapids', 'peter', 'rex', 'castle', 'storm', 'buzz'],
    'routes': [{'route': mine_route, 'color': '#9a3412'}],
    'description': data['park']['mine_first'],
})
hot_view = next((v for v in views if v['id'] == 12), None)
if hot_view is None:
    hot_view = {'id': 12}
    views.append(hot_view)
hot_view.update({
    'title': data['park']['hot_first']['title'],
    'keys': ['disney', 'hot', 'mine', 'pirate', 'soar', 'rapids', 'peter', 'rex', 'tron', 'castle', 'storm', 'buzz'],
    'routes': [{'route': hot_route, 'color': '#7c3aed'}],
    'description': data['park']['hot_first'],
})
next(v for v in views if v['id'] == 7)['description'] = day
views_file.write_text(json.dumps(views, ensure_ascii=False, indent=2), encoding='utf-8')

plan = {
    'date': '2026-10-27', 'ticket_early_entry': '07:30', 'gate_arrival': '06:30–06:45',
    'status': '截至2026-10-14，10/27普通开园、闭园、项目及演出时刻未公布；07:30来自用户已购票信息。',
    'model': '2026年10月与周二排队均值、逐小时热力、10/13同周二及56篇小红书早享文字笔记综合后的规划区间；不是10/27实时报数或置信区间。',
    'walk_model': '景点近似坐标的直线距离乘1.35估园路，再按约75米/分钟估步行；各段步行另留机动。',
    'rides': [
        {'time':'07:30–08:05','key':'tron','walk':[10,12],'queue':[10,20],'experience':[10,12],'threshold':25},
        {'time':'08:05–08:55','key':'mine','walk':[8,10],'queue':[25,40],'experience':[8,10],'threshold':40},
        {'time':'08:55–10:10','key':'hot','walk':[4,6],'queue':[50,70],'experience':[15,18],'threshold':70},
        {'time':'10:10–11:05','key':'pirate','walk':[7,9],'queue':[25,40],'experience':[14,18],'threshold':45},
        {'time':'11:05–12:35','key':'soar','walk':[8,10],'queue':[55,75],'experience':[18,22],'threshold':75},
        {'time':'13:05–14:15','key':'rapids','walk':[4,6],'queue':[40,60],'experience':[12,16],'threshold':60},
        {'time':'14:15–15:20','key':'peter','walk':[10,14],'queue':[35,50],'experience':[10,12],'threshold':50},
        {'time':'15:20–16:55','key':'rex','walk':[4,6],'queue':[70,90],'experience':[10,12],'threshold':90},
    ],
    'mine_first': {
        'switch_rule': '创极速暂未开放或实显>25分钟，且矿山车开放、实显≤25分钟；若两项都短，优先原主线。',
        'completion_window': '16:40–19:45',
        'rides': [
            {'time':'07:30–08:15','key':'mine','walk':[10,12],'queue':[15,25],'experience':[8,10],'threshold':25},
            {'time':'08:15–09:25','key':'hot','walk':[4,6],'queue':[40,60],'experience':[15,18],'threshold':60},
            {'time':'09:25–10:55','key':'tron','walk':[10,14],'queue':[60,80],'experience':[10,12],'threshold':80},
            {'time':'10:55–12:00','key':'pirate','walk':[13,16],'queue':[30,45],'experience':[14,18],'threshold':45},
            {'time':'12:00–13:40','key':'soar','walk':[8,10],'queue':[70,90],'experience':[18,22],'threshold':90},
            {'time':'14:10–15:25','key':'rapids','walk':[4,6],'queue':[40,60],'experience':[12,16],'threshold':60},
            {'time':'15:25–16:30','key':'peter','walk':[10,14],'queue':[35,50],'experience':[10,12],'threshold':50},
            {'time':'16:30–18:05','key':'rex','walk':[4,6],'queue':[70,90],'experience':[10,12],'threshold':90},
        ],
    },
    'hot_first': {
        'switch_rule': '热力追踪早享开放且实显≤30分钟、创极速和矿山车均>25分钟时启用；若热力超过30分钟，仍按A/B线中实际更短的首站走。',
        'completion_window': '16:25–19:45',
        'rides': [
            {'time':'07:30–08:25','key':'hot','walk':[13,16],'queue':[20,35],'experience':[15,18],'threshold':30},
            {'time':'08:25–09:30','key':'mine','walk':[4,6],'queue':[40,60],'experience':[8,10],'threshold':60},
            {'time':'09:30–10:25','key':'pirate','walk':[7,9],'queue':[25,40],'experience':[14,18],'threshold':45},
            {'time':'10:25–11:55','key':'soar','walk':[8,10],'queue':[55,75],'experience':[18,22],'threshold':75},
            {'time':'11:55–13:10','key':'rapids','walk':[4,6],'queue':[40,60],'experience':[12,16],'threshold':60},
            {'time':'13:40–14:45','key':'peter','walk':[10,14],'queue':[35,50],'experience':[10,12],'threshold':50},
            {'time':'14:45–16:20','key':'rex','walk':[4,6],'queue':[70,90],'experience':[10,12],'threshold':90},
            {'time':'16:20–18:00','key':'tron','walk':[4,6],'queue':[70,95],'experience':[10,12],'threshold':95},
        ],
    },
    'heatmap': [
        {'name':'矿山车','key':'mine','h8':62,'h10':98,'h20':60,'source':'https://queue-times.com/en-US/parks/30/rides/2990/2026'},
        {'name':'创极速','key':'tron','h8':42,'h10':82,'h20':60,'source':'https://queue-times.com/en-US/parks/30/rides/2985/2026'},
        {'name':'热力追踪','key':'hot','h8':59,'h10':82,'h20':37,'source':'https://queue-times.com/en-US/parks/30/rides/12392/2026'},
        {'name':'飞越地平线','key':'soar','h8':39,'h10':73,'h20':39,'source':'https://queue-times.com/en-US/parks/30/rides/3002/2026'},
        {'name':'加勒比','key':'pirate','h8':12,'h10':43,'h20':9,'source':'https://queue-times.com/en-US/parks/30/rides/2996/2026'},
        {'name':'雷鸣山','key':'rapids','h8':21,'h10':51,'h20':19,'source':'https://queue-times.com/en-US/parks/30/rides/2986/2026'},
        {'name':'小飞侠','key':'peter','h8':6,'h10':40,'h20':20,'source':'https://queue-times.com/en-US/parks/30/rides/2989/2026'},
        {'name':'抱抱龙','key':'rex','h8':17,'h10':64,'h20':47,'source':'https://queue-times.com/en-US/parks/30/rides/5633/2026'},
    ],
}
for field, expected in [('walk',(55,73)), ('queue',(310,445)), ('experience',(97,120))]:
    assert tuple(sum(r[field][i] for r in plan['rides']) for i in range(2)) == expected
for field, expected in [('walk',(37,47)), ('queue',(165,245)), ('experience',(65,80))]:
    assert tuple(sum(r[field][i] for r in plan['rides'][:5]) for i in range(2)) == expected
for field, expected in [('walk',(63,84)), ('queue',(360,500)), ('experience',(97,120))]:
    assert tuple(sum(r[field][i] for r in plan['mine_first']['rides']) for i in range(2)) == expected
for field, expected in [('walk',(54,73)), ('queue',(355,505)), ('experience',(97,120))]:
    assert tuple(sum(r[field][i] for r in plan['hot_first']['rides']) for i in range(2)) == expected
for rides in (plan['rides'], plan['mine_first']['rides'], plan['hot_first']['rides']):
    previous = 'disney'
    for ride in rides:
        a, b = data['points'][previous], data['points'][ride['key']]
        meters = math.hypot((a['lat'] - b['lat']) * 111200,
                            (a['lon'] - b['lon']) * 95200) * 1.35
        ride['from'] = previous
        ride['distance_m'] = round(meters / 50) * 50
        previous = ride['key']
(ROOT / 'research/disney-queue-model-2026-10-27.json').write_text(
    json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / '地图资源/迪士尼排队模型.json').write_text(
    json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')

guide_file = OUT / '上海轻松旅行方案.md'
guide = guide_file.read_text(encoding='utf-8')
guide = re.sub(r'\|D7·10/27 迪士尼\|[^\n]+',
    '|D7·10/27 迪士尼|B→乐园→B|7:30早享先抢高排队项，全天争取八大热门|演出和其他项目按现场余量加减|[交通](每日地图/D07-地理路线.png)／[园内](每日地图/D07-园内路线.png)|', guide)
start = guide.index('## 迪士尼这样玩更轻松')
end = guide.index('**下一步落实：', start)
replacement = '''## 迪士尼这样玩更轻松

**27日一日票＋7:30早享票已购。** 建议6:30–6:45到指定早享入口；酒店出发时间另按实际交通倒推。26日晚在[官方App](https://www.shanghaidisneyresort.com/zh-cn/information/download-shanghai-disney-mobile-app)核对项目早享开放、演出及闭园。全天目标是 **创极速→矿山车→热力追踪→加勒比→飞越→雷鸣山→小飞侠→抱抱龙** 八项热门项目；地图最后经城堡出园。虚线只表示景点顺序，不是道路导航。抱抱龙刺激、雷鸣山可能打湿衣物；不想玩时直接以现场短队项目替换。

从园内入口到主线首站创极速约850米、步行10–12分钟；到备用B线首站矿山车也约850米、步行10–12分钟。C线到热力追踪的距离和各站间步行估算见[园内互动地图](每日地图/D07-园内路线.html)。距离用点位直线距离乘1.35估计，并非园区道路导航；从实际闸机、项目队尾到上车还需留现场缓冲。

|规划时段|项目与预计排队|到点决定|
|---|---|---|
|07:30–08:05|创极速 10–20分|到达时≤25分且开放才排；否则改矿山车首站。|
|08:05–08:55|矿山车 25–40分|≤40分排；较长记为晚间候补。|
|08:55–10:10|热力追踪 50–70分|≤70分排；较长先走宝藏湾。|
|10:10–11:05|加勒比 25–40分|≤45分排；否则傍晚补。|
|11:05–12:35|飞越地平线 55–75分|≤75分排；超过就傍晚再查。|
|12:35–13:05|探险岛附近快餐与短休|前五项延误就顺延，优先压缩演出与低队列加项。|
|13:05–14:15|雷鸣山 40–60分|≤60分、开放且愿意可能打湿衣物再玩。|
|14:15–15:20|小飞侠 35–50分|≤50分排，超过则转抱抱龙。|
|15:20–16:55|抱抱龙 70–90分|≤90分且能接受高刺激再排；太长就19点后复查。|
|16:55–17:25|晚饭与补水|从出队时间顺延。|
|17:25–19:30|先补漏掉的热门；有余量再加巴斯/胡迪/剧场|巴斯≤15分、胡迪≤35分或风暴来临有合适场次才加。|
|当晚至闭园|按官方App选烟花或再玩一项|演出和闭园时刻尚待公布；以个人取舍为准。|

**时间计算：** 前五项预计排队165–245分，五项约 **12:00–13:45** 完成。八项共预计排队310–445分、步行55–73分、体验/上下车/前导97–120分，再加30分钟午饭，总计约492–668分，因此八项大致在 **15:45–18:40** 完成，表中16:55是中间情景。历史数据只用于规划区间，不是10/27排队预测。园路以近似坐标直线距离乘1.35估算；排队参考2026年10月、周二及逐小时热力，并参考[56篇早享笔记审读索引](迪士尼早享56篇审读索引.html)。[2026项目均值](https://queue-times.com/en-US/parks/30/stats/2026?hide_archived=true)中，矿山车89、创极速78、热力70、抱抱龙68、飞越66、雷鸣山47分钟，早享优先处理前三项。现场请按官方App调整。[官方园区地图](https://static.shanghaidisneyresort.com/web-img-gallery/park-map-260227.pdf)核对位置。

**矿山车首站备用线：** 当创极速早享暂未开放或实显超过25分钟，同时矿山车开放且实显≤25分钟时，从入口直奔矿山车，随后热力追踪→创极速→加勒比→飞越→雷鸣山→小飞侠→抱抱龙。前两项预计07:30–09:25完成；创极速放到约09:25–10:55，因此这条线通常比创极速首站稍晚结束。八项预计排队360–500分钟、步行63–84分钟、体验97–120分钟，另加30分钟午饭，共550–734分钟，约 **16:40–19:45** 完成。若热力实显>60分钟，先去创极速；若创极速到达时>80分钟，就列入傍晚候补，不在门口硬等。项目开放与排队均以当天官方App和现场为准。[矿山车首站离线图](每日地图/D07-园内路线-矿山车优先.png)。

**热力追踪首站备用C线：** 仅在早享时热力开放且实显≤30分钟，而创极速、矿山车均>25分钟时选。入口→热力→矿山车→加勒比→飞越→雷鸣山→小飞侠→抱抱龙→创极速，按园区相邻区域推进，避免中途从西区折返东区。热力排队一旦>30分钟，改走A/B中实际更短的首站。C线八项预计排队355–505分钟、步行54–73分钟、体验97–120分钟，加30分钟午饭，共536–728分钟，约 **16:25–19:45** 完成；创极速约16:20到达，如实显>95分钟，应在仍营业的前提下晚间复查，八项可能无法全部完成。这是有条件的次优解，不保证比A线更快。[热力首站离线图](每日地图/D07-园内路线-热力优先.png)。

轻装带水杯、充电宝和外套。食品携带按[官方游客规则](https://www.shanghaidisneyresort.com/en/legal/park-rules)与[携带说明](https://www.shanghaidisneyresort.com/en/experience/guest-service/weather-packing-information)。

'''
guide = guide[:start] + replacement + guide[end:]
guide_file.write_text(guide, encoding='utf-8')

print(json.dumps({'opened': len(notes), 'usable': len(accepted), 'park_route': route}, ensure_ascii=False))
