from pathlib import Path
import json, time, urllib.parse, urllib.request
P=Path(__file__).parent
targets={
 'hotel':'上海图书馆 上海 淮海中路', 'hotelA':'全季 岳阳路 上海',
 'wukang':'武康大楼 上海','court':'武康庭 上海',
 'park':'in the PARK 上海 安福路','csy':'CSYSeLECTED 上海',
 'uru':'乌鲁木齐中路 上海','fumin':'富民路 上海','julu':'巨鹿路 上海',
 'guang':'光明邨 上海','xin':'新天地 上海','alter':'ALTER 上海 新天地',
 'yu':'豫园 上海','nanxiang':'南翔馒头店 上海 豫园','nanjing':'沈大成 上海 南京东路',
 'bund':'和平饭店 上海','ifc':'上海国金中心','tower':'上海中心大厦',
 'river':'滨江大道 上海 陆家嘴','b':'康新公路站 上海','disney':'上海迪士尼乐园',
 'pvg':'上海浦东国际机场','sha':'上海虹桥国际机场',
 'goodbai':'GOODBAI 上海 延庆路','badmarket':'Badmarket 上海 长乐路',
 'iapm':'环贸 上海','apoli':'Apoli Ita Bakery 上海',
 'yongjia':'永嘉路 上海','xujiahui':'美罗城 上海',
}
rows=[]
for key,q in targets.items():
 u='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q,'format':'jsonv2','limit':1,'countrycodes':'cn','viewbox':'121.2,31.4,121.9,30.9','bounded':1})
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'ShanghaiTravelPlan/1.0 (local personal itinerary)'})
  result=json.loads(urllib.request.urlopen(req,timeout=15).read())
  rows.append({'id':key,'query':q,'results':result,'source_url':u})
  print(json.dumps({'id':key,'results':[{k:x.get(k) for k in ['lat','lon','display_name']} for x in result]},ensure_ascii=False),flush=True)
 except Exception as e:rows.append({'id':key,'query':q,'error':str(e),'source_url':u});print(key,'failed',flush=True)
 (P/'map-pois.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 time.sleep(1.05)
