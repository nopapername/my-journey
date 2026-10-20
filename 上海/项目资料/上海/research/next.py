import importlib.util, json, re, urllib.parse, html
from pathlib import Path
p=Path(r'D:\web3\code_project\旅游规划\上海\research\collect.py')
s=importlib.util.spec_from_file_location('travelcollect',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
urls=['https://www.bing.com/search?'+urllib.parse.urlencode({'q':'"武康路" "安福路" 攻略'}),'https://www.baidu.com/s?'+urllib.parse.urlencode({'wd':'上海旅游攻略'}),'https://www.bing.com/search?'+urllib.parse.urlencode({'q':'Shanghai travel blog itinerary','format':'rss'}),'https://www.shanghaidisneyresort.com/','https://www.chinahighlights.com/shanghai/']
for n,url in enumerate(urls):
 try:
  raw,final=m.fetch(url); text=m.plain(raw)
  (p.parent/f'next-{n}.html').write_text(raw,encoding='utf-8')
  print(json.dumps({'url':url,'final':final,'length':len(text),'text':text[:11000],'links':[html.unescape(x) for x in re.findall(r'href=["\x27]([^"\x27]+)',raw) if any(w in x.lower() for w in ['shanghai','attraction','ticket','rule','calendar','travel','disney','line','cn/'])][:100]},ensure_ascii=False))
 except Exception as e: print(json.dumps({'url':url,'error':str(e)},ensure_ascii=False))
