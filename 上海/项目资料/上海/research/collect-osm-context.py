from pathlib import Path
import urllib.request, urllib.parse, json
root=Path(__file__).resolve().parent
query='''[out:json][timeout:90];(
nwr["name"~"武康庭|九曲桥|国金|康新公路|迪士尼小镇|热力追踪|沉落宝藏|风暴来临|飞越地平线|创极速|LABELHOOD|蕾虎|光明邨|南翔馒头|延庆路|安福路|富民路|长乐路|武康路|乌鲁木齐中路|滨江大道|迪士尼|上海环贸|GOODBAI"](31.10,121.40,31.27,121.70);
);out center geom;'''
url='https://overpass-api.de/api/interpreter'
req=urllib.request.Request(url,data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'ShanghaiItineraryResearch/1.0 personal travel mapping'})
with urllib.request.urlopen(req,timeout=120) as f: data=json.load(f)
(root/'osm-context.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for el in data['elements']:
    tags=el.get('tags',{}); c=el.get('center',el)
    print(json.dumps({'id':el['id'],'name':tags.get('name'),'lat':c.get('lat'),'lon':c.get('lon'),'addr':{k:v for k,v in tags.items() if k.startswith('addr:')}},ensure_ascii=False))
