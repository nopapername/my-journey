import json, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'research.json').read_text(encoding='utf-8'))
shops={s['id']:s for s in data['shops']}
cache=ROOT/'research-walking-routes.json'
result=json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
for route in data['routes']:
    points=[[shops[sid]['lat'],shops[sid]['lon']] for sid in route['coreIds'] if shops[sid]['lat'] is not None]
    if len(points)<2:continue
    coordinate_string=';'.join(f'{lon:.6f},{lat:.6f}' for lat,lon in points)
    url='https://routing.openstreetmap.de/routed-foot/route/v1/driving/'+coordinate_string+'?overview=full&geometries=geojson&steps=false&continue_straight=false'
    previous=result.get(route['id'],{})
    if previous.get('url')==url and previous.get('inputPoints')==points and previous.get('response',{}).get('code')=='Ok':continue
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ShanghaiShopwalk/1.0 personal-itinerary-research'})
        with urllib.request.urlopen(req,timeout=30) as response:body=json.load(response)
        result[route['id']]={'url':url,'response':body,'profile':'FOSSGIS prepared foot graph','checkedAt':'2026-10-15','coreIds':route['coreIds'],'inputPoints':points}
        if body.get('routes'):print(route['id'],round(body['routes'][0]['distance']), 'm',round(body['routes'][0]['duration']/60),'min',flush=True)
    except Exception as e:result[route['id']]={'url':url,'error':str(e)};print(route['id'],str(e),flush=True)
    cache.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    time.sleep(1)
