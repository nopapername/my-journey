import concurrent.futures, json, re, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'research.json').read_text(encoding='utf-8'))
cache_path=ROOT/'research-address-geocodes.json'
cache=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}
queries={}
for s in data['shops']:
    address=s['address']
    m=re.search(r'([\u4e00-\u9fff]+(?:路|街)\d+(?:-\d+)?(?:弄\d+)?号)',address)
    if m:
        street=re.sub(r'^.*(?:市|区|为)', '', m.group(1))
        queries[s['id']]='上海市'+street
# Verified merchant/mall addresses missing a street in the original list.
queries.update({'s01':'上海市南京西路1601号','s03':'上海市愚园路68号','s05':'上海市石门一路288号'})
def fetch(item):
    sid,q=item
    params={'SingleLine':q,'f':'json','outFields':'Match_addr,Addr_type,Score','maxLocations':1,'outSR':4326,'countryCode':'CHN','searchExtent':'121.39,31.15,121.51,31.28','location':'121.45,31.22'}
    url='https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?'+urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url,timeout=25) as r: result=json.load(r)
        return sid,{'query':q,'url':url,'response':result,'checkedAt':'2026-10-15'}
    except Exception as e: return sid,{'query':q,'error':str(e),'checkedAt':'2026-10-15'}
def needs_retry(sid,q):
    if sid not in cache or cache[sid].get('query')!=q:return True
    cs=cache[sid].get('response',{}).get('candidates',[])
    if not cs:return True
    xy=cs[0].get('location',{})
    return not (31.15<xy.get('y',0)<31.28 and 121.39<xy.get('x',0)<121.51)
pending=[(sid,q) for sid,q in queries.items() if needs_retry(sid,q)]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    for sid,result in executor.map(fetch,pending):cache[sid]=result
cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
for sid in queries:
    result=cache[sid]; candidates=result.get('response',{}).get('candidates',[])
    c=candidates[0] if candidates else {}
    print(sid, result['query'],c.get('score'),c.get('attributes',{}).get('Addr_type'),c.get('location'))
