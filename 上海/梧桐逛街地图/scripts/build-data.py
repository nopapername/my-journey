import json, math, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(name):
    x=json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
    return x if isinstance(x,list) else x.get('entries',x.get('places',[]))
research=read('research-west.json')+read('research-east.json')+read('research-south.json')
research.append(dict(name='MUSINSA',address='上海市徐汇区安福路201-1号（品牌官网写201号）',lat=31.213813,lon=121.443383,coordinateSystem='GCJ02',confidence='exact',evidenceUrl='https://www.amap.com/place/B0LKUUYVQU',notes='品牌官网2025-12-19开业公告与高德同名POI交叉确认，https://about.musinsa.com/zh/newsroom/2025-1219-musinsa-anpuru-open 。'))

sources=[
 ('n01','6acf6b87000000001501539a','超顺路J人自制上海逛街路线🛍️怒逛十五家','CBzvBFShbaoMk2CWrjY68gXQvxulrZfab3ipZU0IlbbeY=','正文章节、作者评论；视频部分画面','原始清单同一链接出现3次，作为1篇独立笔记保留。视频末尾甜品店已核为APOLI ITABAKERY；BF为作者评论简称候选，24ans仅评论相对位置。'),
 ('n02','6a7c8ae7000000002402eb94','上海宝藏逛街地图🚶‍♀️10家小众私藏美店！','CBAGEkXKE4DB0ampYLBFqf4Rkb5hXseAViEJvGVsjUjhM=','正文10店清单','部分小店缺门牌，未将同名或近似拼写店铺强行合并。'),
 ('n03','6a58c472000000000301ed39','上海shopping第二弹🛍️','CBnQiFOeEMDHZTaX6qqgtogxOnFr55pqVEJTnlX4iX2sA=','正文路线与风格评价','The Edit Room公开可查的是历史快闪地址，现状待确认。'),
 ('n04','6a5223cc0000000008030062','上海就是一个巨大的汉南洞','CBV_czhmMovUCHAXfQ-Pwtc1697KOPBvmpuQsne-mfrOo=','正文4店清单','东日/冬日是个卷毛保留别名；Negative three未查明上海门店。PB ARCHIVE位于苏河，不强塞进梧桐区主线。'),
 ('n05','6a3cecbc000000000f03283a','上海⑥家好逛的美丽新店🏡','CBVEMAnRqRsmYdUB5AAOvc-8UWy480vQ2xkL3xh4s6vt4=','正文6店及门牌','正文给出的门牌属于原文证据，独立地址核查不足的条目会明确标注。'),
 ('n06','6ab7c0fb000000001500f16c','国庆假期 逛街必逛！！上海私藏小众店铺','CB2bPJ8KMajtwGxzKMhwXD-terno3TonEGCy9PHDzfQ3c=','正文、作者地址回复、视频三个品牌章节画面','已核对FIRSTFLOOR、22 Collection、PB ARCHIVE画面。视频未做逐秒转录。'),
 ('n07','6a6340a5000000000f0324fb','跟穿搭博主怒逛12家！时髦美衣线下爽逛','CBZEtNAMzN0zBKGXkhEjSiJZDsUM5ILCq9XvGp01Ik0gQ=','正文、作者评论及视频多段抽查','视频正文未列全店名；评论中的点点总结仅作线索。仍有5个店名未可靠提取，保留缺口条目；不宣称12家已全部识别。'),
 ('n08','69903c7e000000001a02adc4','上海｜巨富长之本土设计师品牌又美又卷7家','CBBsAnftgt-M4csZT0Cbu6Y26ncqfdOj7p0fhtg2DSGSw=','正文7店、街区与风格评价','EXISTENTIALISM原文称新乐路，另一篇图片称长乐路，未查实前合为待核分店线索。'),
 ('n09','6abba21e0000000012035597','跟着穿搭博主怒逛10家 上海购物狂来了','CB6rqq2UqkwvG-TmQT4HZJgZp-kPjrWLXx5lkRnJ4cPZI=','正文、作者评论、视频抽查、置顶网友地图图片','网友地图列10家但道路方向不可靠，仅用作店名线索；SHKUCO、pupuhome门牌仍待核，不按网友地图直接落点。'),
 ('n10','6aaf917d0000000028003e8d','上海逛街🧭淮海中路“不回头版”攻略（附地图）','CBuWuwzdr_W5yHLGOxGbqjYI5T8org5DNJhCFSB7UWgOs=','全文15组店铺、风格与活动日期','过森日按原文活动期截至10月7日，现已超过期限；原文餐饮评价为作者主观感受。'),
 ('n11','6a2a7513000000003600018d','上海逛街去哪里｜一定是安福路的鞋店','CBqiz8KKLahdBa1GcXnAIj0ETcO9pMiMMq6wwXSEPAggo=','正文两店','安福路为片区称谓；Morethings+实查乌鲁木齐中路196号，RizzDarling仅查到街道。'),
 ('n12','6acb9ffa000000001301b4f7','双11前必存｜在上海梧桐区种草的13家女装店','CBroMXAoVIDcGhJzYlPuDVnognzWs9Wfj9twrx96gdX1w=','正文及全部5张图片逐张查看','13家含不同街区。图中素船依品牌官网校正为素舶；AAAD安福附近线索对应五原路分店；RandomPiece新天地铺位未独立查实。')
]
sources.append(('n13','6a099bcc0000000036018827','把上海当作小韩来逛｜一起云逛街','CBezKx7q91mDopALpt1nckpg_FT-GsLckKsfJ9R3pAQ04=','正文、评论与视频各品牌段落画面核对','画面确认OPEN YY、Negative Three、22 Collection、Lost in echo、MOONMOI、Rockfish、HAUS NOWHERE；MOONMOI同名地图登记类别有矛盾；OPEN YY活动期限未核。'))
source_data=[dict(id=i,title=t,url=f'https://www.xiaohongshu.com/explore/{nid}?xsec_token={token}&xsec_source=app_share',scope=sc,limitations=lim) for i,nid,t,token,sc,lim in sources]

# Positions for address-only records are transparent street/block estimates,
# never claimed as surveyed storefront locations. Higher-quality POI anchors
# collected below replace these estimates where an address matches.
blocks={
 '静安寺':(31.2231,121.4457),'陕西北路':(31.2333,121.4555),'太古汇':(31.2300,121.4610),'苏河':(31.2422,121.4750),
 '愚园路':(31.2197,121.4180),'利西路':(31.2168,121.4250),'华山路':(31.2162,121.4330),
 '安福西':(31.2153,121.4350),'安福东':(31.2150,121.4400),'五原西':(31.2129,121.4392),'五原东':(31.2140,121.4442),'武康':(31.2102,121.4349),
 '巨鹿西':(31.2225,121.4470),'巨鹿东':(31.2234,121.4532),'富民':(31.2203,121.4471),'长乐':(31.2176,121.4430),'新乐':(31.2190,121.4505),'华亭':(31.2180,121.4467),'东湖':(31.2183,121.4506),
 '淮海西':(31.2180,121.4543),'淮海中':(31.2200,121.4583),'淮海东':(31.2224,121.4637),'新天地':(31.2175,121.4760),
 '乌南':(31.2050,121.4450),'建西':(31.2066,121.4495),'永嘉':(31.2080,121.4520),'汾阳':(31.2145,121.4520),'永康':(31.2120,121.4560),'嘉善':(31.2112,121.4600),'建中':(31.2100,121.4660),
}
# key, readable name, source ids, route, block (None = no location), short style, tags
specs=[
 ('SUPERSCAPE','素舶 SUPERSCAPE','n12','r1','静安寺','简约日常女装，基础版型与柔和配色','极简,女装'),
 ('开间 KEIGAN','开间 KEIGAN','n12','r1','静安寺','摩登极简，建筑感线条与利落剪裁','极简,通勤'),
 ('TWOI','TWOI Design Lab','n12','r1','静安寺','奶油色系、松弛服饰与生活周边','休闲,生活方式'),
 ('jajainthemoment','jajainthemoment','n12','r1','陕西北路','轻松休闲女装，老洋房生活场景','休闲,女装'),
 ('Fabrique','Fabrique · 兴业太古汇','n07','r1','太古汇','设计师合作女装，视频以度假风穿搭为线索','设计师,女装'),
 ('PB ARCHIVE','PB ARCHIVE','n04,n06','r1','苏河','韩系买手选品，视频出现针织与设计感女装','韩系,买手店'),
 ('an action a day（愚园','an action a day · 愚园路','n05','r2','愚园路','自然舒适的运动休闲，家居场景式陈列','运动,休闲'),
 ('Typha','Typha','n05','r2','利西路','芭蕾舞蹈运动，蕾丝与蓬裙的浪漫感','芭蕾,运动'),
 ('TOGGLER','TOGGLER','n05','r2','华山路','英伦浪漫配饰，珍珠、蝴蝶结与芭蕾元素','配饰,浪漫'),
 ('Rockfish Weatherwear（安福','Rockfish Weatherwear · 安福路','n01','r2','安福西','复古英伦鞋履，芭蕾鞋与日常鞋袜','鞋履,英伦'),
 ('Grove / GRVRGROVE（安福','GROVE · 安福路','n01','r2','安福西','韩系复古休闲，基础款带轻运动感','韩系,休闲'),
 ('Brandy','Brandy Melville · 安福路','n01,n03','r2','安福西','美式少女基础款，吊带、针织和短裙','美式,少女'),
 ('Alicia','Alicia','n05,n09','r2','安福东','饰品与发饰；视频作者在此购买头饰，完整选品待核','配饰,发饰'),
 ('The Edit Room','The Edit Room','n03','r2','安福东','韩牌买手集合，适合比较多种韩系穿搭','韩系,买手店'),
 ('Morethings+','Morethings+','n11','r2','安福东','设计鞋包与首饰，手工皮具、中古配饰','鞋履,包袋,首饰'),
 ('RizzDarling','RizzDarling','n02,n11','r2',None,'设计女鞋与搭配配饰；具体门牌待核','鞋履,配饰'),
 ('FIRSTFLOOR','FIRSTFLOOR 家与工坊','n06','r2','五原东','极简休闲，牛仔、短外套与日常基础款','极简,休闲'),
 ('an action a day（五原','an action a day · 五原路','n12','r2','五原东','运动休闲基础款，「客厅与阳台」生活场景','运动,休闲'),
 ('椋木','椋木','n02','r2','五原西','原创茶酒器皿、家居器物与艺术策展','器物,生活方式'),
 ('LOOKNOW（武康','LOOKNOW · 武康路','n01','r2','武康','全球设计师服装、鞋包与生活方式集合','买手店,设计师'),
 ('Subdued','Subdued · 武康路','n01,n12','r2','武康','青春少女与Y2K，贴身上衣和小翅膀元素','少女,Y2K'),
 ('Yearly Plan','Yearly Plan','n08','r3','长乐','中性长期主义服装，零售与Gallery并置','中性,极简'),
 ('asomesome（长乐','asomesome · 长乐路','n01,n03,n08,n12','r3','长乐','简洁日常、柔和通勤，轻松好搭的设计款','通勤,简约'),
 ('LABELDEL','LABELDEL.','n08','r3','巨鹿西','东方复古与天然肌理，宽松剪裁和手工细节','东方,设计师'),
 ('LADYFAFA','LADYFAFA','n08,n09','r3','巨鹿西','原创复古女装，别致花色与轮廓','复古,原创'),
 ('LABELHOOD','LABELHOOD 蕾虎','n02,n08','r3','富民','中国独立设计师，先锋服装、首饰与家居','先锋,设计师'),
 ('chelchel','chelchel house','n05','r3','富民','简约自然女装，亲肤面料与通勤休闲','自然,通勤'),
 ('Bistro11','Bistro11','n02','r3','富民','All Day Brunch与融合西餐，蓝色法式门头','餐饮,休息'),
 ('Freja','Freja 别院','n05','r3','富民','审美空间与服饰探店；具体选品风格待核','空间,待核'),
 ('Academy of Love','Academy of Love','n08','r3',None,'纯白极简与爱心元素，无性别服装','极简,中性'),
 ('CERRIC','CERRIC','n01,n09,n12','r3',None,'韩系甜美，蕾丝、轻柔裙装与少女感','韩系,少女'),
 ('teenteens','teenteens','n01','r3',None,'韩系休闲服装与帽饰；当前快闪状态待核','韩系,帽饰'),
 ('oror','oror by fine','n01','r3','新乐','泰式餐厅，冬阴功与绿咖喱为原文推荐','餐饮,泰式'),
 ('NNN2097','NNN2097 vintage','n09','r3','新乐','美式古着、学院衬衫与90年代休闲','古着,学院'),
 ('melomela','melomela','n01','r3','华亭','可爱杂货、文具与小型收纳好物','杂货,可爱'),
 ('Sinoon','Sinoon / Snoon','n01,n03,n10','r3','东湖','韩系浪漫少女，蕾丝、蝴蝶结与花苞轮廓','韩系,浪漫'),
 ('Rest &','Rest & Recreation','n01,n10','r3','东湖','韩系日常与轻运动，开衫、短袖等基础款','韩系,运动'),
 ('Alimentari','Alimentari Grande · 东湖路','n10','r3','东湖','意式熟食、咖啡与brunch，适合中途休息','餐饮,休息'),
 ('Come Come','Come Come Bakery','n09','r2','安福东','烘焙面包，顺路补给；与soso为不同店','面包,餐饮'),
 ('ffroom','ffroom','n01,n09','r3',None,'韩系少女服装，兼有配饰与收纳小物','韩系,少女'),
 ('Lagoon Store','Lagoon Store','n09','r3','巨鹿东','中古器物、贝壳与餐具，生活杂货选品','器物,杂货'),
 ('pupuhome','pupuhome','n09','r3',None,'服饰与生活方式线索；上海门店和风格待核','待核'),
 ('SHKUCO','SHKUCO','n09','r3',None,'弄堂服饰小店；视频可见基础色与连衣裙','女装,待核'),
 ('EXISTENTIALISM（新乐','EXISTENTIALISM · 巨富长线索','n08,n12','r3',None,'原创先锋女装，独特剪裁与沉浸式空间','先锋,设计师'),
 ('LOOKNOW PARK','LOOKNOW PARK · 淮海中路','n01,n10','r4','淮海西','工业风买手集合，设计服装、配饰与Jellycat','买手店,毛绒'),
 ('Grove / GRVRGROVE（环贸','GROVE · 环贸iapm','n10','r4','淮海西','韩系轻运动休闲；和环贸吃饭一起顺逛','韩系,运动'),
 ('老吉士','老吉士 · 环贸iapm','n10','r4','淮海西','本帮菜，作为原文餐饮替代选项','餐饮,本帮'),
 ('CUBIC','CUBIC','n09,n10','r4','淮海中','都市极简女装，建筑感廓形与克制配色','极简,通勤'),
 ('HAUS NOWHERE','HAUS NOWHERE 上海','n10','r4','淮海中','眼镜、香氛与大型装置，赛博艺术空间','香氛,艺术'),
 ('emis','emis','n10','r4','淮海中','韩系休闲，彩色棒球帽、包袋与基础服装','韩系,帽饰'),
 ('niko and','niko and ... 全球旗舰店','n10','r4','淮海中','日系服装、文创、家具与生活杂货','日系,杂货'),
 ('光明邨','光明邨大酒家','n10','r4','淮海东','沪上老字号，本帮菜、熟食与鲜肉月饼','餐饮,老字号'),
 ('上海哈尔滨','哈尔滨食品厂','n10','r4','淮海东','俄式海派糕点、饼干与哈斗，适合买少量尝鲜','糕点,老字号'),
 ('TX淮海','TX淮海','n10','r4','淮海东','潮流策展商场，服饰、快闪与青年文化','商场,潮流'),
 ('HAI550','HAI550','n10','r4','淮海东','主理人品牌、手作与生活方式集合楼宇','商场,生活方式'),
 ('言二丁','言二丁','n10','r4','淮海东','文艺真皮女鞋，现代东方审美','鞋履,东方'),
 ('MURMURMI','MURMURMI','n10','r4',None,'天然材质与褶皱设计，原文尤其推荐连衣裙','设计师,自然'),
 ('PSO BRAND','PSO BRAND','n10','r4','淮海东','可爱印花与舒适休闲，年轻日常服饰','休闲,印花'),
 ('W0311','W0311 山石衣','n10','r4','淮海东','小众设计师集合，原文以小礼服为看点','礼服,设计师'),
 ('MASONPRINCE','MASON PRINCE','n10','r4','淮海东','无性别街头、复古摇滚与先锋解构','街头,中性'),
 ('RARELY ALIKE','RARELY ALIKE','n12','r4',None,'设计感女装，日常实穿与独立表达','设计师,女装'),
 ('Oneup','Oneup · 新天地东台里','n12','r4','新天地','城市运动生活方式，将运动与日常结合','运动,休闲'),
 ('RandomPiece','RandomPiece · 新天地线索','n12','r4',None,'舒适基本款与利落廓形，当前门店待核','休闲,极简'),
 ('过森日','过森日 · 原文快闪','n10','r4','淮海东','森系、日系、手作首饰与独立品牌市集','快闪,手作'),
 ('Dragonshop','Dragonshop','n10','r4',None,'韩系少女服装与连衣裙；原文提示瑞金公寓401','韩系,少女'),
 ('Folder','Folder Bakery & Coffee','n07','r5','乌南','法棍、法式吐司与咖啡，适合分享式补给','面包,餐饮'),
 ('ASTEE','ASTEE ATELIER','n02','r5','建西','珠宝与婚嫁首饰，钻戒、银饰和日常珠宝','珠宝,首饰'),
 ('Re knit','Re knit','n07','r5','永嘉','进口毛线、彩色编织与手作灵感','编织,手作'),
 ('SoftServe','SoftServe 柔软供应','n07','r5','汾阳','水果主题器皿、手机壳与可爱生活设计','器物,可爱'),
 ('miulab','miulab','n07','r5','永康','买手选品、韩牌与设计服装；视频提到Paloma Wool','买手店,韩系'),
 ('小玉','小玉 yuy × Parlid 快闪线索','n01','r5','嘉善','萌系潮玩与拍立得联名，当前快闪按公告复核','潮玩,快闪'),
 ('22collection','22 COLLECTION','n01,n02,n04,n06','r5','建中','韩系服饰集合，针织、外套与设计细节','韩系,买手店'),
 ('EXISTENTIALISM（复兴','EXISTENTIALISM · 复兴西路线索','n07','r2',None,'小众先锋设计女装；该分店信息仅评论线索','先锋,待核'),
 ('Woodeng','Woodeng','n07',None,None,'西太后品牌买手线索；店名拼写、门牌待核','买手店,待核'),
 ('cotempt','cotempt','n02',None,None,'原文归为服装／珠宝，具体选品风格待核','服装珠宝,待核'),
 ('luftkuss','luftkuss','n02',None,None,'服装买手选品，具体风格与门牌待核','买手店,待核'),
 ('thirty','thirty','n02',None,None,'原文归为生活方式，具体选品待核','生活方式,待核'),
 ('HAKU','HAKU','n02',None,None,'原文归为餐食／甜品，具体品类与地址待核','餐饮,待核'),
 ('Negative three','Negative three','n04',None,None,'韩系探店清单中的品牌，店名与具体风格待核','韩系线索,待核'),
 ('24ans','24ans · LOOKNOW对面线索','n01','r4',None,'女装线索；作者评论称粉色门头，风格待核','女装,待核'),
 ('东日','东日是个卷毛 · DongRi studio','n01,n04','r4',None,'简约百搭、按色系陈列的日常女装；冬日为原文别称','简约,日常'),
 ('MUSINSA','MUSINSA Store · 安福路','n12','r2','安福东','韩系与本土设计师集合，兼有运动品牌与潮流配饰','韩系,买手店'),
]

def gcj_to_wgs(lat,lon):
    a=6378245.0; ee=0.00669342162296594323
    def tl(x,y):
        r=-100+2*x+3*y+.2*y*y+.1*x*y+.2*math.sqrt(abs(x))
        r+=(20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
        r+=(20*math.sin(y*math.pi)+40*math.sin(y/3*math.pi))*2/3
        return r+(160*math.sin(y/12*math.pi)+320*math.sin(y*math.pi/30))*2/3
    def tn(x,y):
        r=300+x+2*y+.1*x*x+.1*x*y+.1*math.sqrt(abs(x))
        r+=(20*math.sin(6*x*math.pi)+20*math.sin(2*x*math.pi))*2/3
        r+=(20*math.sin(x*math.pi)+40*math.sin(x/3*math.pi))*2/3
        return r+(150*math.sin(x/12*math.pi)+300*math.sin(x/30*math.pi))*2/3
    rad=lat/180*math.pi;m=1-ee*math.sin(rad)**2; sm=math.sqrt(m)
    dlat=tl(lon-105,lat-35)*180/((a*(1-ee))/(m*sm)*math.pi)
    dlon=tn(lon-105,lat-35)*180/(a/sm*math.cos(rad)*math.pi)
    return round(lat-dlat,6),round(lon-dlon,6)

shops=[]
for i,(key,name,src,route,block,style,tags) in enumerate(specs,1):
    m=next((e for e in research if key.lower() in e['name'].lower()),{})
    lat=lon=None; loc='unknown'; coordnote='暂无可靠点位，不在地图上放置猜测图钉。'
    address=m.get('address') or '门牌待核实'
    if m.get('lat') is not None:
        lat,lon=gcj_to_wgs(m['lat'],m['lon']);loc='exact';coordnote='同名高德POI坐标，已由GCJ-02转换为WGS84；门店入口仍以现场门牌为准。'
    # Address-only entries wait for verified POI anchors or address geocoding.
    if not m.get('confidence') or m.get('confidence')=='unknown':
        # Keep useful original-note addresses, but flag their independent verification gap.
        pass
    note=m.get('notes','')
    if '用户提供' in note:note=note.replace('用户提供','所给笔记／评论提供')
    address=address.replace('用户提供','原文提供')
    status='expired' if key=='过森日' else 'uncertain' if (loc=='unknown' or key in ['The Edit Room','小玉','PB ARCHIVE','PSO BRAND']) else 'active'
    if key=='小玉':note+=' 此嘉善路联名活动与n01中的“小玉快闪”是否同一场尚未完全确认，作为候选线索，不算已核实原店。'
    if key=='PB ARCHIVE':note+=' 苏河延伸点，离静安主线较远；原建筑报道曾提示装修，不承诺当前营业。'
    if key=='The Edit Room':note+=' 当前地址证据来自7月快闪，原文较新探店不等于已核实当前常设营业。'
    if key=='LOOKNOW（武康':note+=' n01未明确LOOKNOW分店；同时保留武康旗舰店为同品牌加选，原文路线更可能为淮海店。'
    if key=='asomesome（长乐':note+=' n12图片标为安福附近，不额外杜撰安福独立分店。'
    shops.append(dict(id=f's{i:02}',name=name,style=style,address=address,tags=tags.split(','),routeId=route,sourceIds=src.split(','),lat=lat,lon=lon,locationStatus=loc,status=status,note=note,evidenceUrl=m.get('evidenceUrl'),coordinateNote=coordnote,core=False,sourceKey=key,extension=key in ['PB ARCHIVE','an action a day（愚园','Typha','Oneup']))

# Add source-mentioned landmarks and unextracted video references without fabricated names/positions.
extras=[('花园饭店','n01','r4','喷泉与老建筑拍照；不属于服装店','上海市黄浦区茂名南路58号','淮海西'),('ZARA · 分店待核','n09','r4','快时尚女装；原视频与网友地图未可靠对应分店','具体分店待核',None),('甜品店 · 店名待识别','n01',None,'原视频末段甜品停留，尚未可靠识别店名','待识别',None)]
for name,src,r,style,address,b in extras:
    shops.append(dict(id=f's{len(shops)+1:02}',name=name,style=style,address=address,tags=['补充','待核'] if not b else ['拍照'],routeId=r,sourceIds=[src],lat=None,lon=None,locationStatus='unknown',status='uncertain',note='原文补充点；不计为已核实购物门店。',evidenceUrl=None,core=False,coordinateNote='入口未核实。'))
for name,style in [('老洋房首饰店','珠宝首饰'),('手作屋','手作小物'),('宝藏店铺','选品未完整提取'),('法式马卡龙店','甜品'),('尼泊尔风格买手店','异域服饰、天然材质')]:
    shops.append(dict(id=f's{len(shops)+1:02}',name=f'视频中{name} · 店名待识别',style=style+'；尚未可靠对应具体店名',address='店名与地址待核',tags=['视频缺口','待核'],routeId=None,sourceIds=['n07'],lat=None,lon=None,locationStatus='unknown',status='uncertain',note='n07视频未完整提取的店名，评论仅有描述；不以猜测品牌替代。',evidenceUrl=None,core=False))

# Append supplements after existing IDs so cached geocodes remain bound to their stores.
supplement=read('research-supplement.json')
for key,route,style,tags in [('DORYDORY',None,'复古东方美学女装，成衣与裙装','女装,待核'),('MOONMOI','r2','都市女装，柔和配色与日常成衣','女装,日常'),('OPEN YY','r1','韩系街头与解构女装，Y2K配饰与鞋履','韩系,设计师'),('Lost in echo','r2','设计鞋履与包袋，雕塑感廓形和金属细节','鞋履,包袋')]:
    m=next((e for e in supplement if key.lower() in e['name'].lower()),{})
    shops.append(dict(id=f's{len(shops)+1:02}',name=key,sourceKey=key,style=style,address=m.get('address','上海门牌待核实'),tags=tags.split(','),routeId=route,sourceIds=['n13'],lat=None,lon=None,locationStatus='unknown',status='uncertain',note=m.get('notes','新增视频可见品牌标注，当前店址待核实。'),evidenceUrl=m.get('evidenceUrl'),core=False,extension=(key=='OPEN YY'),coordinateNote='门牌及当前营业未确认，不放置猜测图钉。'))
for shop in shops:
    key=shop.get('sourceKey','')
    if key in ['22collection','Negative three','CERRIC','Rockfish Weatherwear（安福','HAUS NOWHERE']:
        shop['sourceIds'].append('n13')
    if key=='SoftServe':
        shop['name']='SoftServe / Sorbet';shop['style']+='；Sorbet为同店配饰副线';shop['note']+=' Sorbet作为同店副线收录，不重复生成门店。'
    if key=='CERRIC':
        m=next(e for e in supplement if e['name']=='CERRIC');shop['address']=m['address'];shop['style']=m['style'];shop['note']+=' '+m['notes'];shop['evidenceUrl']=m['evidenceUrl'];shop['tags']=['韩系','设计师','鞋履']
    if key=='Negative three':
        shop['style']='韩国设计师鞋履，运动鞋、玛丽珍与靴子';shop['note']+=' 新视频可见品牌标注；官网另有2025年12月已结束快闪，但不能据此认定为视频同一场。当前店址与活动期限待核。'


# Keep prior IDs stable; resolve the unlabelled n01 bakery in place.
location_updates=read('research-location-updates.json')
for update in location_updates:
    next(x for x in shops if x['id']==update['id']).update(update)
shops.append(dict(id='s95',name='BF · BASEMENT FG候选',sourceKey='BF',style='年轻街头与复古休闲服饰集合；品牌匹配待核',address='上海市徐汇区新乐路82号（BASEMENT FG候选门牌）',tags=['街头','买手店','评论候选'],routeId='r3',sourceIds=['n01'],lat=None,lon=None,locationStatus='unknown',status='uncertain',core=False,extension=False,keepUncertain=True,note='n01作者原评论明确路线经过BF，位于东日到oror泰餐途中。BASEMENT FG官方与上观明确新乐路82号，简称和地段相容，但未取得作者确认全名；仅作为候选店址参考。',evidenceUrl='https://www.sina.cn/news/detail/5215144281903017.html',operatingNote='作者简称匹配与当前营业待确认；未纳入核心线。',coordinateNote='候选门牌参考，不代表已确认视频中的BF。'))
# User explicitly asked to ignore DORYDORY; do not recycle s91 for another store.
shops=[x for x in shops if x.get('sourceKey')!='DORYDORY']

def ids(keys):return [next(s['id'] for s in shops if s.get('sourceKey')==k) for k in keys]
routes=[
 dict(id='r1',title='静安寺 → 南京西路',subtitle='极简女装 · 商场与老洋房',color='#38735f',summary='先逛静安寺相邻三店，再向东去何东旧居与兴业太古汇；苏河PB ARCHIVE作为独立加选，不折回梧桐区。',duration='核心店建议 3–4 小时',walkNote='静安寺三店 → 陕西北路 → 兴业太古汇；PB ARCHIVE另行导航。时间是逛店安排建议，非实时步行估算。',start='静安寺站',end='南京西路站',keys=['SUPERSCAPE','TWOI','开间 KEIGAN','jajainthemoment','Fabrique','PB ARCHIVE'],coreKeys=['SUPERSCAPE','TWOI','开间 KEIGAN','jajainthemoment','Fabrique']),
 dict(id='r2',title='安福路 → 五原路 → 武康路',subtitle='少女鞋包 · 设计小物 · 梧桐散步',color='#bd7755',summary='主线沿安福路向东逛鞋包，再由乌鲁木齐中路接五原路，向西收进武康路。愚园／利西／华山是北侧加选，建议与主线择一半天。',duration='核心店建议 4–5 小时',walkNote='Rockfish／GROVE／BM → Morethings+ → FIRSTFLOOR／AAAD → 椋木 → Subdued。北侧加选不要强行一口气逛完。',start='常熟路站／安福路西端',end='交通大学站／武康路南端',keys=['an action a day（愚园','Typha','TOGGLER','Rockfish Weatherwear（安福','Grove / GRVRGROVE（安福','Brandy','Alicia','The Edit Room','Morethings+','RizzDarling','Come Come','FIRSTFLOOR','an action a day（五原','椋木','LOOKNOW（武康','Subdued','EXISTENTIALISM（复兴'],coreKeys=['Rockfish Weatherwear（安福','Grove / GRVRGROVE（安福','Brandy','Morethings+','FIRSTFLOOR','an action a day（五原','椋木','Subdued']),
 dict(id='r3',title='巨鹿路 → 富民路 → 东湖路',subtitle='本土设计师 · 韩系选品 · 杂货',color='#8f719a',summary='先从巨鹿路西段看设计女装，沿富民路向南接新乐与华亭，再到东湖路FUFU两家韩牌；长乐西段可先逛后向东接入。门牌未核实店保留在线索清单。',duration='核心店建议 4–5 小时',walkNote='LABELDEL／LADYFAFA → LABELHOOD → oror／NNN2097 → melomela → Sinoon／R&R。长乐路Yearly Plan与asomesome可提前加选；Lagoon巨鹿东段单独加选。',start='静安寺站南侧／巨鹿路',end='陕西南路站',keys=['Yearly Plan','asomesome（长乐','LABELDEL','LADYFAFA','LABELHOOD','chelchel','Bistro11','Freja','Academy of Love','CERRIC','teenteens','oror','NNN2097','melomela','Sinoon','Rest &','Alimentari','ffroom','Lagoon Store','pupuhome','SHKUCO','EXISTENTIALISM（新乐'],coreKeys=['LABELDEL','LADYFAFA','LABELHOOD','oror','NNN2097','melomela','Sinoon','Rest &']),
 dict(id='r4',title='淮海中路 · 向东一直逛',subtitle='艺术香氛 · 日杂 · 潮流商场',color='#567b9b',summary='从环贸与LOOKNOW出发，顺淮海中路向东串联CUBIC、HAUS、emis、niko，最后在TX／HAI550与老字号收尾。新天地东台里适合仍有体力时延伸。',duration='核心店建议 4–5 小时',walkNote='LOOKNOW → CUBIC → HAUS／emis → niko → 哈尔滨食品厂／光明邨 → TX／HAI550。商场内店铺同楼集中逛，不另外来回跑。',start='陕西南路站',end='淮海中路站；加选新天地站',keys=['LOOKNOW PARK','Grove / GRVRGROVE（环贸','老吉士','CUBIC','HAUS NOWHERE','emis','niko and','上海哈尔滨','光明邨','TX淮海','PSO BRAND','W0311','HAI550','言二丁','MURMURMI','MASONPRINCE','RARELY ALIKE','Dragonshop','24ans','过森日','Oneup','RandomPiece'],coreKeys=['LOOKNOW PARK','CUBIC','HAUS NOWHERE','emis','niko and','TX淮海','HAI550']),
 dict(id='r5',title='乌南 → 永康路 → 建国中路',subtitle='珠宝与编织 · 生活设计 · 韩系服饰',color='#af9250',summary='从乌鲁木齐南路补给开始，接建国西路珠宝、永嘉毛线，再往永康与嘉善路向东，最后到建国中路22 COLLECTION。小玉快闪先查公告再决定是否绕入。',duration='核心店建议 3–4 小时',walkNote='Folder → ASTEE → Re knit → SoftServe → miulab → 22 COLLECTION。汾阳路为短支线；嘉善路快闪身份和活动期需再核。',start='衡山路站／乌鲁木齐南路',end='打浦桥站／建国中路',keys=['Folder','ASTEE','Re knit','SoftServe','miulab','小玉','22collection'],coreKeys=['Folder','ASTEE','Re knit','SoftServe','miulab','22collection'])
]

def apply_anchors():
    for file in ROOT.glob('research-anchors-*.json'):
        raw=json.loads(file.read_text(encoding='utf-8-sig'))
        anchors=raw if isinstance(raw,list) else raw.get('anchors',raw.get('entries',raw.get('places',[])))
        for a in anchors:
            lat=a.get('lat');lon=a.get('lon')
            if lat is None or lon is None:continue
            # Matching uses explicit matchKeys or a Chinese road+doorplate token.
            patterns=a.get('matchKeys',[])
            targets=a.get('targetNames',[]) or [a.get('targetName','')]
            addr=a.get('targetAddress') or a.get('address') or a.get('query') or ''
            token=re.search(r'([\u4e00-\u9fff]+(?:路|街)\d+(?:-\d+)?(?:弄\d+)?号)',addr)
            for s in shops:
                if s['locationStatus']=='exact':continue
                matched=any(p in s['name'] or p in s['address'] for p in patterns)
                normalize=lambda value:re.sub(r'[\W_]+','',str(value).lower())
                if not matched and s.get('sourceKey'):
                    matched=any(normalize(s['sourceKey']) in normalize(t) for t in targets if t)
                if not matched and token:matched=token.group(1) in s['address']
                if not matched:continue
                s['lat'],s['lon']=gcj_to_wgs(lat,lon);s['locationStatus']='approximate'
                s['anchorEvidenceUrl']=a.get('evidenceUrl');s['anchorName']=a.get('anchorName') or a.get('name')
                s['coordinateNote']='同楼／邻近地图POI参考点：'+str(s['anchorName'])+'。不是该门店实测入口；请按门牌与高德搜索核对。'
                if '仅同街' in str(a.get('anchorRelation','')):s['broadLocation']=True
                if s['status']=='uncertain' and s.get('sourceKey') not in ['The Edit Room','小玉','PB ARCHIVE']:
                    s['status']='active'
apply_anchors()

# Address geocoding is a reference location, never promoted to merchant POI exact.
geocode_file=ROOT/'research-address-geocodes.json'
if geocode_file.exists():
    geocodes=json.loads(geocode_file.read_text(encoding='utf-8'))
    for s in shops:
        g=geocodes.get(s['id'],{});candidates=g.get('response',{}).get('candidates',[])
        if s['locationStatus']!='unknown' or not candidates:continue
        c=candidates[0];xy=c.get('location',{});typ=c.get('attributes',{}).get('Addr_type','')
        if c.get('score',0)<85 or not (31.15<xy.get('y',0)<31.28 and 121.39<xy.get('x',0)<121.51):continue
        requested=re.search(r'([\u4e00-\u9fff]+(?:路|街))',g.get('query','').removeprefix('上海市'))
        if requested and requested.group(1) not in c.get('address',''):continue
        if requested and requested.group(1) not in s['address']:continue
        s['lat'],s['lon']=round(xy['y'],6),round(xy['x'],6);s['locationStatus']='approximate'
        s['geocodeEvidenceUrl']=g.get('url');s['geocodeMatchedAddress']=c.get('address');s['geocodeType']=typ
        broad=typ in ['StreetName','StreetMidBlock','StreetBetween']
        s['coordinateNote']=('整条街道参考，未匹配门牌，可能偏离门店较远。' if broad else '公开门牌地理编码参考，非同名门店POI；园区楼栋及入口尚未核实。')+'来源：Esri ArcGIS，WGS84。'
        s['broadLocation']=broad
        if s['status']=='uncertain' and s.get('sourceKey') not in ['The Edit Room','小玉','PB ARCHIVE','PSO BRAND'] and s.get('sourceKey') not in ['EXISTENTIALISM（复兴']:
            s['status']='active'

# Resolve review findings conservatively: keep uncertain current-store identity
# out of the walkable core, and never connect an entire-street reference as a stop.
for s in shops:
    key=s.get('sourceKey')
    original=next((e for e in research if key and key.lower() in e['name'].lower()),{})
    if original.get('confidence')=='unknown' or key=='PSO BRAND':s['status']='uncertain'
    if key=='TOGGLER':
        s.update(lat=None,lon=None,locationStatus='unknown',status='uncertain',extension=True)
        s['note']+=' 地址地理编码落点与街区资料存在明显矛盾，取消图钉，待确认后再落点。'
    if key=='LADYFAFA':
        s['status']='uncertain';s['note']+=' 699-4号证据较早，741号仅为附近地图锚点，不代表该店当前地址已确认。'
    if key=='22collection':
        s['status']='uncertain';s['note']+=' 当前门店地址存在建国中路／建国西路报道差异，保留候选但移出核心步行线，出发前以品牌门店公告核对。'
    if key in ['LOOKNOW（武康','an action a day（愚园','Typha','TOGGLER','Oneup','PB ARCHIVE','Lagoon Store']:
        s['extension']=True
    if key in ['Yearly Plan','asomesome（长乐','melomela','oror','miulab','小玉','22collection']:
        s['extension']=True

for shop in shops:
    if shop.get('keepUncertain'):shop['status']='uncertain'
    elif shop.get('verifiedIdentity') and shop['locationStatus']!='unknown':shop['status']='active'

routes[2]['summary']='核心线沿巨鹿路741号一带接富民路，再经新乐路144号走到东湖路FUFU两家韩牌。长乐西段、华亭杂货与餐饮可按兴趣加选；门牌或当前店址待核的品牌保留在完整清单。'
routes[4].update(title='乌南 → 建国西 → 永嘉路',subtitle='珠宝与编织 · 器物与生活设计',summary='核心线从乌鲁木齐南路面包补给出发，沿建国西路看珠宝，再北上永嘉路与汾阳路看毛线和生活设计。永康路miulab、嘉善快闪及22 COLLECTION另作加选；22当前门店有中路／西路报道差异，先核实再去。',end='汾阳路／陕西南路站方向')
for r,text in zip(routes,[
    '静安寺三店起步，经何东旧居向东到太古汇。苏河另作加选。',
    '沿安福路向东，再接五原路向西，武康路收尾。愚园、利西为远端加选。',
    '巨鹿→富民→新乐→东湖，主线集中。长乐、华亭与巨鹿东段另作加选。',
    '从环贸对面沿淮海路向东，至TX、HAI550收尾；新天地另行加选。',
    '乌南→建国西→永嘉→汾阳，一路向北逛。永康及22 COLLECTION为待核加选。'
]):r['summary']=text

for r in routes:
    r['shopIds']=ids(r.pop('keys'));r['coreIds']=ids(r.pop('coreKeys'))
    r['shopIds'] += [x['id'] for x in shops if x.get('sourceKey') in ['MOONMOI','OPEN YY','Lost in echo','APOLI ITABAKERY','BF'] and x['routeId']==r['id']]
    if r['id']=='r2':
        musinsa=next(s for s in shops if s.get('sourceKey')=='MUSINSA')
        r['shopIds'].insert(r['shopIds'].index(ids(['Morethings+'])[0]),musinsa['id'])
        r['coreIds'].insert(r['coreIds'].index(ids(['Morethings+'])[0]),musinsa['id'])
    if r['id']=='r4':r['shopIds'].append(ids(['东日'])[0])
    r['coreIds']=[sid for sid in r['coreIds'] if any(s['id']==sid and s['status']=='active' and not s.get('broadLocation') and s['locationStatus']!='unknown' for s in shops)]
    for s in shops:
        if s['id'] in r['coreIds']:s['core']=True
    # A schematic connector through core locations, not a routing engine result.
    r['path']=[[s['lat'],s['lon']] for sid in r['coreIds'] for s in shops if s['id']==sid and s['lat'] is not None]

# Adopt OSM pedestrian geometry only if it was computed for this exact core.
walking_file=ROOT/'research-walking-routes.json'
walking=json.loads(walking_file.read_text(encoding='utf-8')) if walking_file.exists() else {}
for r in routes:
    walk=walking.get(r['id'],{})
    if walk.get('coreIds')!=r['coreIds'] or walk.get('inputPoints')!=r['path']:continue
    result=walk.get('response',{}).get('routes',[])
    if not result:continue
    line=result[0];r['path']=[[lat,lon] for lon,lat in line['geometry']['coordinates']]
    r['walkingDistanceKm']=round(line['distance']/1000,1);r['walkingMinutes']=round(line['duration']/60)
    r['pathKind']='pedestrian-reference';r['routeEvidenceUrl']=walk['url']
    r['walkNote']='核心点步行参考约'+str(r['walkingDistanceKm'])+'公里／'+str(r['walkingMinutes'])+'分钟（不含逛店、等候和支线；基于OSM与参考点，非现场核验导航）。'

data=dict(updated='2026-10-15',sources=source_data,routes=routes,shops=shops,coordinateSystem='WGS84',mapNote='核心虚线基于OSM步行路网与门店参考点规划，未实测入口或现场通行。空心点为门牌／同楼参考，实心点来自同名地图POI。',coverageNote='13篇独立来源全部保留。视频采用正文、作者评论和画面抽查，尚有未识别店名；不宣称所有视频店铺已完全提取。',unplacedSummary='未确认门牌、同名分店或店名的条目保留在待核清单，不用猜测坐标。')
(ROOT/'dist').mkdir(exist_ok=True)
(ROOT/'dist'/'data.js').write_text('window.DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(ROOT/'research.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(shops)} records; {sum(s["locationStatus"]=="exact" for s in shops)} exact; {sum(s["locationStatus"]=="approximate" for s in shops)} approximate; {sum(s["locationStatus"]=="unknown" for s in shops)} unplaced')
