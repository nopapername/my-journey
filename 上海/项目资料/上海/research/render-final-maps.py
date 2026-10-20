from pathlib import Path
import json, math, urllib.request, time, io
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'武康路轻松版';A=OUT/'地图资源'
DATA=json.loads((OUT/'行程数据.json').read_text(encoding='utf-8'));P=DATA['points']
views=json.loads((ROOT/'research/map-views.json').read_text(encoding='utf-8'))
place_file=OUT/'地图资源/店铺点位.json'
places=json.loads(place_file.read_text(encoding='utf-8')) if place_file.exists() else []
cache=ROOT/'research/osm-tile-cache';cache.mkdir(exist_ok=True)
headers={'User-Agent':'ShanghaiRelaxedItinerary/1.0 (personal travel map export; finite views)'}
def fetch(url,path):
    if path.exists():return path.read_bytes()
    for attempt in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=25) as r:b=r.read()
            path.write_bytes(b);time.sleep(.2);return b
        except Exception:
            if attempt:raise
            time.sleep(1)
for filename,url in [('leaflet.js','https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'),('leaflet.css','https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'),('Leaflet-LICENSE.txt','https://unpkg.com/leaflet@1.9.4/LICENSE')]:fetch(url,A/filename)
fontpath='C:/Windows/Fonts/msyh.ttc'
font=lambda s:ImageFont.truetype(fontpath,s)
def px(lat,lon,z):
    return (lon+180)/360*256*2**z,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*256*2**z
def ll(x,y,z):return math.degrees(math.atan(math.sinh(math.pi*(1-2*y/(256*2**z))))),x/(256*2**z)*360-180
def cached_tile(z,tx,ty):
    """Use an existing parent tile when sandboxed network access is unavailable."""
    path=cache/f'{z}-{tx}-{ty}.png'
    if path.exists():return Image.open(path).convert('RGB')
    for parent_zoom in range(z-1,9,-1):
        scale=2**(z-parent_zoom)
        parent=cache/f'{parent_zoom}-{tx//scale}-{ty//scale}.png'
        if parent.exists():
            img=Image.open(parent).convert('RGB')
            size=256//scale
            if size < 1:break
            x=(tx%scale)*size;y=(ty%scale)*size
            return img.crop((x,y,x+size,y+size)).resize((256,256),Image.Resampling.BILINEAR)
    return Image.new('RGB',(256,256),'#e8ede6')
def dash(draw,a,b,color,width=5):
    dx=b[0]-a[0];dy=b[1]-a[1];dist=math.hypot(dx,dy)
    if not dist:return
    for t in range(0,math.ceil(dist),20):
        u=min(t+12,dist);draw.line((a[0]+dx*t/dist,a[1]+dy*t/dist,a[0]+dx*u/dist,a[1]+dy*u/dist),fill=color,width=width)
def wrapped(draw,text,x,y,maxwidth,size=22,color='#173238'):
    f=font(size);line=''
    for c in text:
        if draw.textlength(line+c,font=f)>maxwidth:
            draw.text((x,y),line,font=f,fill=color);y+=size+12;line=c
        else:line+=c
    if line:draw.text((x,y),line,font=f,fill=color);y+=size+12
    return y
def label_position(anchor,width,height,occupied):
    ax,ay=anchor;step=max(width,height)+8;offsets=[(0,0)]
    for ring in range(1,5):
        n=step*ring
        offsets += [(0,-n),(n,0),(0,n),(-n,0),(n,-n),(n,n),(-n,n),(-n,-n)]
    best=None;best_score=float('inf')
    for dx,dy in offsets:
        x,y=ax+dx,ay+dy
        rect=(x-width/2-5,y-height/2-5,x+width/2+5,y+height/2+5)
        overlap=sum(max(0,min(rect[2],other[2])-max(rect[0],other[0]))*
            max(0,min(rect[3],other[3])-max(rect[1],other[1])) for other in occupied)
        edge=max(0,52-rect[0])+max(0,rect[2]-1458)+max(0,162-rect[1])+max(0,rect[3]-1088)
        score=overlap*100+edge*1000+math.hypot(dx,dy)
        if score<best_score:best_score=score;best=(x,y,rect)
        if overlap==0 and edge==0:break
    occupied.append(best[2])
    return best[:2]
exports=[]
for v in views:
    keys=v['keys'];W,H=1430,950;is_park=v['id'] in (10,11,12)
    coords=[px(P[k]['lat'],P[k]['lon'],0) for k in keys]
    dx=max(max(x for x,y in coords)-min(x for x,y in coords),.002);dy=max(max(y for x,y in coords)-min(y for x,y in coords),.002)
    # Retain the old approximate scale while showing more surrounding streets.
    z=min(17,max(10,math.floor(math.log2(min((W*.63)/dx,(H*.63)/dy)))))
    cx=(max(x for x,y in coords)+min(x for x,y in coords))/2*2**z;cy=(max(y for x,y in coords)+min(y for x,y in coords))/2*2**z
    left=int(cx-W/2);top=int(cy-H/2);base=Image.new('RGB',(W,H),'#eef2ed')
    for tx in range(left//256,(left+W-1)//256+1):
        for ty in range(top//256,(top+H-1)//256+1):
            tile=cached_tile(z,tx,ty);base.paste(tile,(tx*256-left,ty*256-top))
    basename=f'view-{v["id"]:02d}'
    base.save(A/f'{basename}-底图.png')
    south,west=ll(left,top+H,z);north,east=ll(left+W,top,z)
    v['bounds']=[[south,west],[north,east]];v['background']=f'地图资源/{basename}-底图.png'
    full=Image.new('RGB',(2110,1370),'#faf8f2');draw=ImageDraw.Draw(full)
    daydate=next((d['date'] for d in DATA['days'] if d['id']==v['id']),None)
    prefix='全程' if v['id']==0 else '市区' if v['id']==9 else '园内·10/27' if is_park else f'D{v["id"]}·{daydate}'
    draw.text((40,28),f'上海轻松旅行  |  {prefix} · {v["title"]}',font=font(36),fill='#173238')
    draw.text((40,91),'街道底图 · 北向上 · 虚线是游玩顺序，交通方式见下方；不是道路导航',font=font(23),fill='#556765')
    full.paste(base,(40,150))
    def pos(k):x,y=px(P[k]['lat'],P[k]['lon'],z);return x-left+40,y-top+150
    for r in v['routes']:
        seq=r['route'];col=r['color']
        for a,b in zip(seq,seq[1:]):dash(draw,pos(a),pos(b),col)
    # Lay out day/stop labels first, then store icons around them. Short leader
    # lines point back to the unchanged geographic coordinates.
    markerkeys=['sha','hotel','b','disney'] if v['id']==0 else ['b'] if v['id']==8 else ['hotel'] if v['id']==9 else keys
    main=set(k for r in v['routes'] for k in r['route']);occupied=[];route_marks=[];day_marks=[]
    if v['id']==9:
        for day,r in enumerate(v['routes'],2):
            anchor=pos(r['route'][0]);day_marks.append((day,anchor,label_position(anchor,53,33,occupied),r['color']))
    for i,k in enumerate(markerkeys,1):
        anchor=pos(k);route_marks.append((i,k,anchor,label_position(anchor,84 if k=='hotel' else 42,42,occupied)))
    relevant=[p for p in places if (v['id']==9 and any(2<=day<=5 or day==9 for day in p['days'])) or v['id'] in p['days']]
    if v['id']==0 or is_park:relevant=[]
    symbol={'food':('吃','#c4543d'),'tea':('茶','#6678b8'),'shop':('逛','#ad7b28')}
    place_marks=[]
    for p in relevant:
        x,y=px(p['lat'],p['lon'],z);x=x-left+40;y=y-top+150
        if not (42<x<40+W-22 and 152<y<150+H-22):continue
        place_marks.append((p,(x,y),label_position((x,y),24,24,occupied)))
    for p,anchor,target in place_marks:
        if anchor!=target:draw.line((*anchor,*target),fill='#758982',width=2)
    for day,anchor,target,color in day_marks:
        if anchor!=target:draw.line((*anchor,*target),fill=color,width=2)
    for i,k,anchor,target in route_marks:
        if anchor!=target:draw.line((*anchor,*target),fill='#0f766e',width=2)
    for p,anchor,(x,y) in place_marks:
        mark,color=symbol[p['kind']]
        draw.rounded_rectangle((x-12,y-12,x+12,y+12),radius=5,fill=color,outline='white',width=2)
        draw.text((x-draw.textlength(mark,font=font(16))/2,y-10),mark,font=font(16),fill='white')
    for day,anchor,(x,y),color in day_marks:
        draw.rounded_rectangle((x-27,y-17,x+27,y+17),radius=7,fill='#173238',outline='white',width=2)
        label=f'D{day}'
        draw.text((x-draw.textlength(label,font=font(20))/2,y-12),label,font=font(20),fill='white')
    for i,k,anchor,(x,y) in route_marks:
        lodging=k=='hotel'
        fill='#64748b' if lodging else '#0f766e' if k in main else '#ffffff';border='#64748b' if lodging else '#0f766e'
        if lodging:draw.rounded_rectangle((x-42,y-19,x+42,y+19),radius=18,fill=fill,outline='white',width=3)
        else:draw.ellipse((x-21,y-21,x+21,y+21),fill=fill,outline=border,width=3)
        city_order=sum(item!='hotel' for item in markerkeys[:i])
        s='住·海友' if lodging else f'D{v["id"]}-{city_order}' if 1<=v['id']<=8 else (str(i-1) if k in main and k not in ('disney','castle') else '')+{'disney':'入口','tron':'极速','mine':'矿车','hot':'热力','pirate':'海盗','soar':'飞越','rapids':'漂流','peter':'小飞','rex':'抱龙','castle':'城堡','storm':'剧场','buzz':'巴斯'}[k] if is_park else ['D1','D2–5','D6','D7'][i-1]
        fw=font(16 if len(s)>2 else 20)
        draw.text((x-draw.textlength(s,font=fw)/2,y-11),s,font=fw,fill='white' if lodging or k in main else border)
    draw.text((1510,150),'地点编号与安排',font=font(26),fill='#173238');y=202
    legendkeys=markerkeys
    for i,k in enumerate(legendkeys,1):
        suffix='（可选/替换）' if k not in main else ''
        label=('起点' if k=='disney' else '终点' if k=='castle' else '备选' if k not in main else str(i-1)) if is_park else '住' if k=='hotel' else str(sum(item!='hotel' for item in legendkeys[:i]))
        y=wrapped(draw,f'{label}. {P[k]["name"]}{suffix if k!="hotel" else ""}',1510,y,550,21)
    if v['id']==0:
        y+=10
        for d in DATA['days']:y=wrapped(draw,f'D{d["id"]}·{d["date"]}  {d["title"]}',1510,y,550,21)
        wrapped(draw,'市区景点细节见「01-市区路线总览」与每日图。',1510,y+8,550,20)
    elif v['id']==9:
        for d in DATA['days'][1:5]:y=wrapped(draw,f'D{d["id"]}·{d["date"]}  {d["title"]}',1510,y,550,21)
        y=wrapped(draw,'D2青绿｜D3棕黄｜D4玫红｜D5蓝色。海友酒店单独标记；四色线互不相连。',1510,y+8,550,20)
    elif is_park:
        y+=14;y=wrapped(draw,'编号为热门项目顺序；白色标记为可选地点。',1510,y,550,20)
    elif v['id']!=8:
        y+=14;y=wrapped(draw,'路线编号只标景点与街区；吃、茶、逛是位置参考，不必全去。',1510,y,550,20)
    if relevant:
        y+=18
        y=wrapped(draw,'吃=餐饮 · 茶=茶饮 · 逛=买手店；短细线指向原点，街区锚点按门牌导航。',1510,y,550,19)
    d=v.get('description')
    footer=[DATA['assumption'],'D2–D5按街区分日；各主要景点已在市区总览与每日图标注。'] if not d else [d['mode'],d['pace'],f'吃什么：{d["meal"]}']
    if is_park:
        first=v['routes'][0]['route'][1]
        a,b=P['disney'],P[first]
        distance=math.hypot((a['lat']-b['lat'])*111200,(a['lon']-b['lon'])*95200)*1.35
        first_walk='13–16' if v['id']==12 else '10–12'
        footer.insert(1,f'入口→{b["name"]}约{round(distance/50)*50}米，步行{first_walk}分钟；距离为园内点位估算，非道路导航。')
    fy=1135
    for t in footer:fy=wrapped(draw,t,40,fy,1990,22)
    draw.text((52,1060),'N ↑',font=font(25),fill='#173238',stroke_width=2,stroke_fill='white')
    draw.text((40,1330),'底图 © OpenStreetMap contributors · openstreetmap.org/copyright  |  市区海友酒店已定；抵达机场与乐园附近住宿待确认',font=font(17),fill='#556765')
    if v['id']==0:name='00-全程地理路线.png'
    elif v['id']==9:name='01-市区路线总览.png'
    elif v['id']==10:name='每日地图/D07-园内路线.png'
    elif v['id']==11:name='每日地图/D07-园内路线-矿山车优先.png'
    elif v['id']==12:name='每日地图/D07-园内路线-热力优先.png'
    else:name=f'每日地图/D{v["id"]:02d}-地理路线.png'
    full.save(OUT/name);v['static']=name;exports.append(name)
    print(json.dumps({'view':v['id'],'zoom':z,'image':name},ensure_ascii=False),flush=True)
(OUT/'地图资源/地图视图.json').write_text(json.dumps(views,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'map_count':len(exports),'unique_cached_tiles':len(list(cache.glob('*.png')))},ensure_ascii=False))
