"""Replace the city lodging placeholder with the booked Huaihai Middle Road hotel."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '武康路轻松版'
DATA_FILE = OUT / '行程数据.json'
VIEWS_FILE = ROOT / 'research/map-views.json'
GUIDE_FILE = OUT / '上海轻松旅行方案.md'
README_FILE = OUT / '开始阅读.txt'

data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
data['assumption'] = (
    '成都出发·2位成人·10月21日12:05抵沪，抵达机场待核；27日迪士尼一日票＋早享票已购；'
    '21–25日5晚已定海友上海淮海中路酒店，26–27日乐园附近住宿待定；28日起转杭州，后续不在此规划。'
)
data['points']['hotel'] = {
    'id': 'hotel',
    'name': '海友上海淮海中路酒店',
    'lat': 31.2140144,
    'lon': 121.4416665,
    'tip': '21日入住、26日退房；徐汇区乌鲁木齐中路247号2楼。市区每日图只标位置，不接景点路线。',
    'coordinate_status': '高德门店POI坐标由GCJ-02换算为WGS84近似；实际入口以华住会和现场导航为准',
    'coordinate_source': 'https://ditu.amap.com/place/B00156TK9N',
    'hotel_source': 'https://m.huazhu.com/Hotel/Detail/2000312',
}
data['points'].pop('hotelA', None)
data['days'][0]['mode'] = (
    '21日12:05抵沪，机场待核。先到海友上海淮海中路酒店办理入住／寄存，'
    '再去衡山路、东平路轻逛；酒店只作地图标记，不接午后游览线。'
)
data['days'][5]['mode'] = '从海友上海淮海中路酒店退房，转往乐园附近住宿；小镇为可选延伸。'
DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

views = json.loads(VIEWS_FILE.read_text(encoding='utf-8'))
for view in views:
    if view['id'] in (1, 2, 3, 4, 5, 9):
        view['keys'] = ['hotel', *[key for key in view['keys'] if key != 'hotel']]
    if view['id'] in (1, 6):
        view['description'] = data['days'][view['id'] - 1]
VIEWS_FILE.write_text(json.dumps(views, ensure_ascii=False, indent=2), encoding='utf-8')

guide = GUIDE_FILE.read_text(encoding='utf-8')
guide = guide.replace('# 上海轻松旅行｜武康路住宿版', '# 上海轻松旅行｜海友淮海中路住宿版')
guide = guide.replace(
    '抵达机场、酒店分店与转杭交通待定。',
    '21–25日5晚已定海友上海淮海中路酒店；抵达机场、26–27日乐园附近住宿和转杭交通待定。'
)
guide = guide.replace(
    '虚线不是道路导航；A、B是待选酒店的区域锚点，个别小店标街道段，入口用中文店名重新导航。',
    '虚线不是道路导航；市区每日图和市区总览均单独标出海友酒店，不与游览线相连。乐园附近住宿仍用区域锚点，个别小店标街道段，入口用中文店名重新导航。'
)
start = guide.index('## 酒店先选这一带') if '## 酒店先选这一带' in guide else guide.index('## 已确认住宿')
end = guide.index('## 每天一个主题', start)
guide = guide[:start] + '''## 已确认住宿

**21日入住、26日退房：** [海友上海淮海中路酒店](https://m.huazhu.com/Hotel/Detail/2000312)，华住会地址为**徐汇区乌鲁木齐中路247号2楼**。 [高德门店点位](https://ditu.amap.com/place/B00156TK9N)已换算后标入全程、市区总览及D1–D5每日地图；图上「住·海友」是酒店位置，不属于游览路线。办理入住及行李寄存按订单和门店实际情况；21日机场到店交通待机场信息确认。

**26–27日两晚**乐园附近住宿仍待确定。可优先比较康新公路／秀沿路附近正规酒店，再核对27日早享去程、散场回程及实际接驳安排。

''' + guide[end:]
guide = guide.replace('机场→A寄存／入住', '机场→海友寄存／入住')
guide = guide.replace('累了回A', '累了回海友')
guide = guide.replace('A退房→B入住→休息', '海友退房→乐园附近入住→休息')
guide = guide.replace('A/B分店与26–27日酒店接驳', '26–27日乐园附近酒店与接驳')
GUIDE_FILE.write_text(guide, encoding='utf-8')

readme = README_FILE.read_text(encoding='utf-8')
readme = readme.replace('酒店候选', '已定酒店')
readme = readme.replace(
    '抵达机场与酒店分店待确认；A/B为住宿区域锚点。',
    '21–25日已定海友上海淮海中路酒店，地址乌鲁木齐中路247号2楼；抵达机场与26–27日乐园附近酒店待确认。'
)
README_FILE.write_text(readme, encoding='utf-8')

print(json.dumps({'hotel': data['points']['hotel']['name'], 'city_views': [1, 2, 3, 4, 5, 9]}, ensure_ascii=False))
