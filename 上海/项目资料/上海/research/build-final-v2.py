from pathlib import Path
import json, math, html

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'武康路轻松版'
ASSETS=OUT/'地图资源'; ASSETS.mkdir(exist_ok=True)
(OUT/'每日地图').mkdir(exist_ok=True)
reviews=json.loads((ROOT/'research/xhs-v2-reviews.json').read_text(encoding='utf-8'))
sources={r['code']:r['url'] for r in reviews if r['countable']}
geo={r['id']:r for r in json.loads((ROOT/'research/map-pois.json').read_text(encoding='utf-8'))}
osm=json.loads((ROOT/'research/osm-context.json').read_text(encoding='utf-8'))['elements']
points={}
def add(k,name,lat,lon,tip,source,status='公开地图POI中心；入口以现场导航为准'):
    points[k]=dict(id=k,name=name,lat=lat,lon=lon,tip=tip,coordinate_status=status,coordinate_source=source)
def nom(k,name,tip):
    r=geo[k]['results'][0]
    add(k,name,float(r['lat']),float(r['lon']),tip,f"https://www.openstreetmap.org/{r['osm_type']}/{r['osm_id']}")
def osmp(k,eid,name,tip,status='OSM地物中心；并非实时入口'):
    e=next(e for e in osm if e['id']==eid);g=e.get('geometry',[])
    if g: lat=(min(v['lat'] for v in g)+max(v['lat'] for v in g))/2;lon=(min(v['lon'] for v in g)+max(v['lon'] for v in g))/2
    else:lat=e['lat'];lon=e['lon']
    add(k,name,lat,lon,tip,f"https://www.openstreetmap.org/{e['type']}/{eid}",status)
def gcj(k,name,lat,lon,tip,url):
    # Approximate GCJ-02 to WGS84 inversion, for display only. Navigation uses POI names.
    x=lon-105;y=lat-35
    dlat=-100+2*x+3*y+.2*y*y+.1*x*y+.2*math.sqrt(abs(x))
    dlat+=(20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    dlat+=(20*math.sin(y*math.pi)+40*math.sin(y/3*math.pi))*2/3
    dlat+=(160*math.sin(y/12*math.pi)+320*math.sin(y*math.pi/30))*2/3
    dlon=300+x+2*y+.1*x*x+.1*x*y+.1*math.sqrt(abs(x))
    dlon+=(20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
    dlon+=(20*math.sin(x*math.pi)+40*math.sin(x/3*math.pi))*2/3
    dlon+=(150*math.sin(x/12*math.pi)+300*math.sin(x/30*math.pi))*2/3
    rad=lat*math.pi/180;magic=1-.006693421622965943*math.sin(rad)**2;sqrt=math.sqrt(magic)
    dlat=dlat*180/((6378245*(1-.006693421622965943)/(magic*sqrt))*math.pi)
    dlon=dlon*180/(6378245/sqrt*math.cos(rad)*math.pi)
    add(k,name,lat-dlat,lon-dlon,tip,url,'高德GCJ-02近似转换为WGS84；非测量入口')
nom('hotel','A住宿区域·上海图书馆站','前5晚；酒店未选，路线用地铁站作区域锚点')
nom('hotelA','候选全季·岳阳路','岳阳路58号；华住候选，未预订')
nom('wukang','武康大楼','建筑外观；不占车道拍照；午餐瀚祥或蒋掌柜二选一')
gcj('court','武康庭·武康路376号',31.206897,121.439072,'短逛后休息；使用庭内商户位置作园区锚点','https://www.amap.com/place/B0FFISZVVB')
gcj('park','安福路322·in the PARK',31.213209,121.440011,'R098：6号楼1楼；图钉为永乐汇园区，逛两三家即可','https://www.amap.com/place/B0GRPONMIN')
osmp('uru',154073217,'安福路·乌鲁木齐中路口','沿路短逛；茶饮一杯，店铺先查当天营业','公交路口区域锚点；不是店铺入口')
gcj('goodbai','GOODBAI·延庆路92号',31.215217,121.451100,'R021/R102：逛店为主，下午再出门也可以','https://www.amap.com/place/B0JDLCT3B2')
add('fumin','富民路·蕾虎候选',31.2205225,121.4468629,'R098：蕾虎富民路184号；地图只标道路段，门店入口另搜','https://www.openstreetmap.org/way/424580476','富民路道路段中心；非184号店铺入口')
osmp('changle',1068144849,'长乐路·潮牌短段','R102：Badmarket619、fRUITYSHOP617；店铺未核入口，先导航门牌','长乐路道路段中心；非具体店铺入口')
nom('iapm','环贸iapm·休息午饭','取商场内Apple位置作锚点；购物之后坐下45–60分钟')
osmp('guang',4580624892,'光明邨·淮海中路588号','总店地址已校正；适合新天地替换线，不强加购物主线')
nom('xin','新天地·石库门街区','D3替换方案；ALTER在马当路245号L116；与巨富长二选一')
nom('alter','ALTER·马当路245号','R098：新天地L116；替换线买手店候选')
osmp('nanxiang',2485006011,'南翔馒头店·豫园','R013：鲜肉小笼；排队长时换顺路大壶春')
add('yu','豫园商城·九曲桥区域',31.22795,121.48715,'免费公共区与收费园林分开；此点在南翔周边','https://www.openstreetmap.org/node/2485006011','由南翔POI定位的商城周边近似锚点')
nom('nanjing','沈大成·南京东路','双酿团/条头糕少量现买；附近商场休息')
nom('bund','外滩·和平饭店段','黄昏短逛；江边添外套；酒店回程乘车')
osmp('ifc',526005642,'陆家嘴·国金中心','商场午餐与休息；只选一个商场')
nom('tower','上海中心·外观','默认地面看三件套；想登高只加一个观景台')
add('river','浦东滨江·陆家嘴短段',31.2383631,121.4929157,'地图以陆家嘴西路滨江大道口作锚点；不沿江走完整长线','https://www.openstreetmap.org/node/495652438','道路口区域锚点')
osmp('b',4269627924,'B住宿区域·康新公路站','D6/D7两晚；酒店未选，夜间接驳另落实')
add('disney','迪士尼·入园区域',31.1428,121.6583,'乐园南侧近似入园区域；按当天官方指引找安检口','https://www.openstreetmap.org/way/494725605','OSM园区范围内近似入口区域；非实时闸机')
osmp('town',495825377,'迪士尼小镇·可选','D6有余力才去；进入小镇不等于进乐园')
osmp('hot',1234934044,'疯狂动物城·热力追踪','主目标之一；从南侧入园步行过来，先查队列')
osmp('pirate',495387203,'加勒比海盗·沉落宝藏','主目标之一；相邻区域看风暴来临，场次看官方App')
osmp('soar',494352071,'翱翔·飞越地平线','第三目标A；热力/加勒比/飞越不保证当日可同时完成')
osmp('tron',495378407,'创极速光轮·替换飞越','第三目标B；喜欢刺激才选，不强行两项全加')
nom('pvg','浦东机场·返程示例','航班未定；确定航站楼后按实际交通重排')
nom('sha','虹桥机场·抵达示例','航班未定；机场范围中心，不是航站楼入口')
days=[
dict(id=1,title='抵达与附近晚餐',route=['sha','hotel'],optional=['hotelA'],mode='机场→住宿：地铁或打车；机场为示例',meal='酒店周边面馆或生煎，蔡先生/老盛昌等只选顺路分店',pace='抵达后入住；不再赶外滩',source=['R006','R017']),
dict(id=2,title='武康安福慢逛',route=['hotel','wukang','court','park','uru','hotel'],mode='到武康大楼乘车亦可；街区短段步行；回程乘车',meal='瀚祥面馆或蒋掌柜二选一；Apoli面包/一杯茶饮加选',pace='10:30出门；安福路只逛两三店；坐下45–60分钟',source=['R028','R036','R059','R063','R064','R068','R098']),
dict(id=3,title='巨富长购物半日',route=['hotel','goodbai','fumin','changle','iapm','hotel'],optional=['guang','xin'],mode='酒店→延庆路乘车；店间短段步行；回程乘车',meal='iapm坐下吃饭；味香斋仅顺路时替换；不专程折返光明邨',pace='午后出门也可；GOODBAI/蕾虎/Badmarket选两三家',source=['R021','R038','R047','R052','R098','R102']),
dict(id=4,title='老城与外滩黄昏',route=['hotel','yu','nanxiang','nanjing','bund','hotel'],mode='酒店→老城、老城→南京路、外滩→酒店乘车；南京路尾段步行',meal='南翔或大壶春选一个；沈大成糕团少量；鲜得来可替换',pace='11点左右到老城；下午商场休息；黄昏到外滩',source=['R010','R013','R017','R052','R057']),
dict(id=5,title='陆家嘴与滨江',route=['hotel','ifc','tower','river','hotel'],mode='地铁或打车过江；浦东短段步行；不能步行过黄浦江',meal='国金中心午餐；晚上回住宿街区选择本帮菜',pace='11点出门；默认不登高；江边只走短段，累了即回',source=['R002','R017','R043']),
dict(id=6,title='退房转场与休息',route=['hotel','b'],optional=['town'],mode='带行李打车优先；小镇为可选加程',meal='新酒店附近吃饭；不为省餐费另赶远路',pace='午前退房，下午入住B；准备入园用品早睡',source=['R125','R127','R152']),
dict(id=7,title='迪士尼轻松一日',route=['b','disney','b'],mode='可靠酒店接驳、11号线或打车；回程先落实',meal='园内午餐坐下休息；不强行出园吃饭',pace='3个主目标＋看秀＋午休；当日App调顺序；点「园内」看主线',source=['R122','R137','R139','R140','R142','R147','R153']),
dict(id=8,title='返程',route=['b','pvg'],mode='按实际航班选择机场；地图以浦东作示例',meal='早餐后出发；酒店到机场保留缓冲',pace='优先下午航班；实际日期与航站楼确定后校正',source=['R127']),
]
colors=['#64748b','#0f766e','#b45309','#be123c','#1d4ed8','#7c3aed','#c2410c','#475569']
park=dict(id=10,title='迪士尼园内·三主目标',route=['disney','hot','pirate','soar','disney'],optional=['tron'],mode='园内步行；连线表示安排顺序，入口与排队动线用官方App',meal='加勒比附近安排看秀与午饭；午后留45–60分钟坐下',pace='第三目标：飞越与创极速二选一；先查队列再决定先去哪个',source=days[6]['source'])
data=dict(status='2026-10-14审读155篇去重笔记，101篇纳入实质文字分析，54篇排除；图片未逐张审读、视频未完整观看。',assumption='成都出发·2位成人·暂按8天7晚，前5晚市区，D6退房；酒店与航班未定。',coordinate_boundary='WGS84地图展示；个别街区为近似区域锚点；虚线表示游玩顺序，不是道路、地铁或可步行轨迹。',points=points,days=days,park=park,colors=colors,sources=sources)
(OUT/'行程数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Each view is also exported with an offline street basemap by render-final-maps.py.
views=[]
for id in range(11):
    if id==0:
        routes=[{'route':['sha','hotel','b','disney','b','pvg'],'color':'#0f766e'}]
        keys=['sha','hotel','wukang','park','goodbai','yu','bund','ifc','b','disney','pvg']
        title='全程与住宿基地';d=None
    elif id==9:
        routes=[{'route':d['route'],'color':colors[d['id']-1]} for d in days[1:5]]
        keys=list(dict.fromkeys(k for d in days[1:5] for k in d['route']))
        title='市区D2–D5·分区总览';d=None
    else:
        d=park if id==10 else days[id-1]
        routes=[{'route':d['route'],'color':colors[6] if id==10 else colors[id-1]}]
        keys=list(dict.fromkeys(d['route']+d.get('optional',[])));title=d['title']
    coords=[[points[k]['lat'],points[k]['lon']] for k in keys]
    views.append(dict(id=id,title=title,keys=keys,routes=routes,description=d))
(ROOT/'research/map-views.json').write_text(json.dumps(views,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'points':len(points),'days':len(days),'views':len(views),'accepted_sources':len(sources)},ensure_ascii=False))
