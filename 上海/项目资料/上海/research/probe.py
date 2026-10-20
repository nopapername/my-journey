import importlib.util, json, re
from pathlib import Path
p=Path(r'D:\web3\code_project\旅游规划\上海\research\collect.py')
s=importlib.util.spec_from_file_location('travelcollect',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
urls=['https://you.ctrip.com/travels/shanghai2.html','https://www.google.com/search?q=Shanghai+travel+blog+itinerary','https://www.baidu.com/s?wd=上海旅游攻略','https://www.bing.com/search?q=Shanghai%20travel%20blog%20itinerary&setlang=en&cc=US']
for url in urls:
 try:
  raw,final=m.fetch(url)
  name=str(len(list(p.parent.glob('probe-*.html'))))+'.html'
  (p.parent/('probe-'+name)).write_text(raw,encoding='utf-8')
  text=m.plain(raw)
  print(json.dumps({'url':url,'final':final,'length':len(text),'text':text[:15000],'links':re.findall(r'href=["\x27]([^"\x27]+)',raw)[:70]},ensure_ascii=False))
 except Exception as e: print(json.dumps({'url':url,'error':str(e)},ensure_ascii=False))
