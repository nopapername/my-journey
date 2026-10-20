"""Keep sightseeing routes separate from optional shop and food pins."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent.parent
out = root / '武康路轻松版'
data_path = out / '行程数据.json'
views_path = root / 'research/map-views.json'
pins_path = root / 'research/map-place-pins.json'
data = json.loads(data_path.read_text(encoding='utf-8'))
views = json.loads(views_path.read_text(encoding='utf-8'))
pins = json.loads(pins_path.read_text(encoding='utf-8'))
p = data['points']

def sight(key, name, lat, lon, tip, source, status='公开地图地物中心；非测量入口'):
    p[key] = dict(id=key, name=name, lat=lat, lon=lon, tip=tip,
                  coordinate_status=status, coordinate_source=source,
                  kind='sight')

sight('hengshan', '衡山路·梧桐街段', 31.20646, 121.44191,
      '21日下午只走一小段；到酒店后再出发，累了随时回去',
      'https://www.openstreetmap.org/node/4559664576', '衡山路地铁站周边街段锚点；不是店铺入口')
sight('dongping', '东平路·岳阳路街区', 31.2090976, 121.4472944,
      '老建筑外观与梧桐街景；使用岳阳路酒店候选周边作街区锚点',
      'https://www.openstreetmap.org/node/7656355076', '岳阳路街区近似锚点；非东平路精确路口')
sight('anfu', '安福路西段', 31.2150838, 121.4353991,
      '只挑两三家兴趣店；路线点位表示街区，不代表必须进店',
      'https://www.amap.com/place/B0GRPONMIN', '安福路322号附近街段锚点；非店铺入口')
sight('yanqing', '延庆路·常熟路街区', 31.2170, 121.4458,
      '若体力允许再往东逛；GOODBAI是参考图钉，不是必经站',
      'https://www.amap.com/place/B0JDLCT3B2', '由延庆路92号向西取的街区近似锚点')
sight('sinan', '思南公馆街区', 31.21604, 121.46437,
      '看老洋房外观；街区开放空间慢逛，私宅不进入',
      'https://www.openstreetmap.org/way/494309300')
sight('fuxing', '复兴公园', 31.21907, 121.46444,
      '公园坐下休息半小时；开放时间以现场为准',
      'https://www.openstreetmap.org/way/39961770')
sight('nanjingstreet', '南京东路步行街', 31.23836, 121.48087,
      '只走靠近外滩的短段；这一站看街景与建筑，不安排逛商场',
      'https://www.openstreetmap.org/node/5345153737', '河南中路／南京东路路口锚点；非店铺入口')
sight('pearl', '东方明珠·外观', 31.24194, 121.49517,
      '广场看陆家嘴天际线；登塔仅在想去且天气合适时加选',
      'https://www.openstreetmap.org/way/40778038')

for key in ('wukang','court','uru','yu','bund','tower','river','xin'):
    p[key]['kind'] = 'sight'
p['xin']['tip'] = '石库门街巷短逛与休息；不安排新一轮买手店购物'
p['yu']['name'] = '豫园·九曲桥街区'
p['yu']['tip'] = '逛公共街区与九曲桥；收费园林另看开放与票务'
p['tower']['tip'] = '在地面看上海中心建筑外观；登高仅作天气好的加选'
p['river']['tip'] = '滨江步道选一小段坐看江景；累了直接乘车回住宿'

new = {
    1: dict(title='抵达·衡山岳阳轻逛', route=['hengshan','dongping'],
            keys=['hotel','hengshan','dongping'],
            mode='21日12:05抵沪；机场待核。先去酒店办理入住／寄存，再乘车或步行到街区；图上只画午后漫步段',
            meal='岳阳路附近面馆或本帮菜，顺路选一家；不为网红店跨区',
            pace='预计15:00–16:00出门，衡山路→东平／岳阳路慢走约1小时；晚餐后回酒店休息',
            source=['R006','R022','R035']),
    2: dict(title='武康安福·唯一逛店日',
            route=['wukang','court','anfu','uru','yanqing'],
            keys=['wukang','court','anfu','uru','yanqing'],
            mode='住宿往返首末站另乘车；虚线只连武康路、安福路和延庆路街区，店铺全是参考图钉',
            meal='瀚祥或蒋掌柜二选一；面包／茶饮最多加一家；买手店按兴趣选两三家',
            pace='10:30左右出门，午后坐下45–60分钟；延庆路可按体力删去，后续几日不再安排购物',
            source=['R021','R022','R028','R033','R036','R059','R098','R102']),
    3: dict(title='思南公馆·复兴公园·新天地',
            route=['sinan','fuxing','xin'], keys=['sinan','fuxing','xin'],
            mode='从住宿乘车到思南公馆；街区和公园之间慢走，返程另乘车；新天地只逛石库门街巷',
            meal='味香斋或附近正餐选一家；茶饮可顺路加选，不追远处店',
            pace='午前或午后出发均可；公园坐下休息，整段约半日，不进入商场扫店',
            source=['R004','R016','R019','R022','R033','R039']),
    4: dict(title='豫园老城·南京东路·外滩',
            route=['yu','nanjingstreet','bund'],
            keys=['yu','nanjingstreet','bund'],
            mode='住宿到豫园、豫园到南京东路、外滩回程均乘车；虚线是景区先后，不是跨区步行导航',
            meal='南翔或大壶春二选一；沈大成糕团只顺路少量买',
            pace='11:00左右进老城；下午休息，黄昏走南京东路靠东短段与外滩',
            source=['R010','R013','R017','R052','R057']),
    5: dict(title='东方明珠·上海中心·滨江',
            route=['pearl','tower','river'],
            keys=['pearl','tower','river'],
            mode='住宿往返浦东乘地铁或打车；图上仅画陆家嘴地面景观顺序',
            meal='就近找一家正餐；红茶公司仅作为可选茶饮图钉，商场不列游览站',
            pace='11:00左右出门；默认不登高，江边走短段，保留下午坐下休息时间',
            source=['R002','R017','R043']),
}
for day in data['days']:
    if day['id'] in new:
        spec=new[day['id']]
        for field in ('title','route','mode','meal','pace','source'):
            day[field]=spec[field]
        day.pop('optional',None)
for view in views:
    if view['id'] in new:
        spec=new[view['id']]
        view['title']=spec['title']; view['keys']=spec['keys']
        view['routes']=[{'route':spec['route'], 'color':data['colors'][view['id']-1]}]
        view['description']={k:day[k] for day in data['days'] if day['id']==view['id'] for k in ('id','title','route','mode','meal','pace','source')}

city = next(v for v in views if v['id']==9)
city['keys'] = list(dict.fromkeys(k for n in range(2,6) for k in new[n]['route']))
city['routes'] = [next(v for v in views if v['id']==n)['routes'][0] for n in range(2,6)]
overview = next(v for v in views if v['id']==0)
overview['keys'] = ['sha','hotel','wukang','sinan','yu','bund','pearl','b','disney']

# The same venue may be referenced on several notes; a pin is one venue, never
# a numbered route stop. Shop-only detours outside D2 are city-overview options.
for pin in pins:
    if pin['kind']=='shop':
        pin['days']=[2] if pin['name'] in ('多抓鱼循环商店','Wiggle Wiggle','in the PARK','GOODBAI') else [9]
    if pin['name']=='光明邨大酒家': pin['days']=[9]
    if pin['name']=='味香斋·雁荡路店': pin['tip']='麻酱面顺路加选；当天看排队，别把餐饮当路线站'
    if pin['name']=='ALTER·新天地': pin['tip']='仅市区总览保留的位置参考；D3不安排进店'
    if pin['name']=='Badmarket／fRUITYSHOP':
        pin['name']='Badmarket';pin['location']='长乐路619号';pin['tip']='D2逛店跨区备选；图钉为长乐路街段，入口按门牌导航'

def add_pin(pin):
    if not any(existing['name']==pin['name'] for existing in pins):
        pins.append(pin)

add_pin({'name':'fRUITYSHOP','kind':'shop','days':[9], 'anchor':'changle',
             'location':'长乐路617号','tip':'D2跨区备选；与Badmarket同街段，入口按门牌导航',
             'source':'https://www.xiaohongshu.com/explore/69eae2fa000000002202470d'})
add_pin({'name':'大壶春·豫园店','kind':'food','days':[4],
             'gcj':[31.227094,121.491432], 'location':'豫园老街／豫春路',
             'tip':'6篇已审读笔记提及品牌；与南翔二选一，分店与排队当天核',
             'source':'https://www.amap.com/place/B0LDAAL87Y'})
add_pin({'name':'茂隆餐厅·进贤路店','kind':'food','days':[9],
             'gcj_area':[31.2232,121.4614], 'location':'进贤路134号',
             'tip':'2篇笔记提及；仅市区总览参考，坐标是进贤路附近估点，导航门牌',
             'source':'https://www.dianping.com/shop/502076/photos/album'})
add_pin({'name':'sunflour·安福路','kind':'food','days':[2], 'anchor':'anfu',
             'location':'安福路322号附近；营业待核',
             'tip':'R036提及的顺路面包候选；图钉为街区，具体门店与营业另查',
             'source':'https://www.timeoutshanghai.com/venue/Restaurants__Cafes-Cafes/4284/Sunflour%2C-Anfu-Lu.html'})

# Prevent an accidental regression: city sightseeing routes may only contain
# named scenic points, even if a merchant anchor still exists in data.points.
for day_id in range(1,6):
    route=new[day_id]['route']
    assert all(p[key].get('kind')=='sight' for key in route), (day_id,route)

data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
views_path.write_text(json.dumps(views,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pins_path.write_text(json.dumps(pins,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'routes':[new[n]['route'] for n in range(1,6)],'pins':len(pins)},ensure_ascii=False))
