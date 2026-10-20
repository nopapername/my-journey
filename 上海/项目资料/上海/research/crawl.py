import importlib.util,json,re,html,urllib.parse,concurrent.futures
from pathlib import Path
P=Path(__file__).parent
s=importlib.util.spec_from_file_location('tc',P/'collect.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
seeds=['https://www.chinahighlights.com/shanghai/','https://www.travelchinaguide.com/cityguides/shanghai.htm','https://www.thepoortraveler.net/shanghai-travel-guide/','https://vivianexplore.tw/shanghai-disneyland/','https://gotravellingworld.com/shanghai-disneyland-guide/','https://gochinaquest.com/zh-CN/%E5%A4%96%E6%BB%A9%E4%B8%8A%E6%B5%B7%E6%8C%87%E5%8D%97/','https://visitcn.com.cn/zh/attractions/the-bund-shanghai','https://www.loongwander.com/zh-CN/article/lujiazui','https://www.greentourasia.com/article/shanghaiyuyuanyouwan','https://www.gochinatravel.org/zh/shanghai/yu-garden','https://chinawondersguide.com/zh-Hans/the-bund-shanghai-nanjing-east-road/','https://www.meet-in-shanghai.net/cn/','https://english.shanghai.gov.cn/en-ExploreShanghai/index.html','https://www.shanghaidisneyresort.com/en/legal/park-rules/','https://www.shanghaidisneyresort.com/en/legal/shanghai-disney-resort-real-name-ticketing-policy','https://www.shanghaidisneyresort.com/en/information/transportation']
seen=set(); queue=seeds[:]; results=[]
markers=['shanghai','bund','lujiazui','wukang','anfu','xintiandi','nanjing','huaihai','disney','上海','外滩','陸家嘴','陆家嘴','武康','安福','新天地','迪士尼','豫园','豫園','奶茶','生煎','本帮','本幫']
def task(url):
 try:
  raw,final=m.fetch(url); text=m.plain(raw)
  t=re.search(r'<title[^>]*>(.*?)</title>',raw,re.S|re.I); title=m.plain(t.group(1)) if t else url
  article=re.search(r'<article\b[^>]*>(.*?)</article>',raw,re.S|re.I)
  main=m.plain(article.group(1)) if article else text
  name=__import__('hashlib').sha256(url.encode()).hexdigest()[:16]+'.txt'
  (P/'crawl-pages').mkdir(exist_ok=True); (P/'crawl-pages'/name).write_text(main,encoding='utf-8')
  links=[]
  for match in re.finditer(r'<a\b[^>]*href=["\x27]([^"\x27]+)["\x27][^>]*>(.*?)</a>',raw,re.S|re.I):
   href=html.unescape(match.group(1)); anchor=m.plain(match.group(2)); link=urllib.parse.urljoin(final,href).split('#')[0]
   label=urllib.parse.unquote(link).lower()+' '+anchor.lower()
   if link.startswith('http') and any(x in label for x in markers) and not any(x in link.lower() for x in ['.jpg','.png','.pdf','facebook','twitter','instagram','whatsapp','wechat','login','search?','subscribe','mailto','maps.google','booking.com','klook','kkday','tripadvisor','tours/','tour/','tag/','category/','contact']):
    links.append(link)
  return {'url':url,'final_url':final,'title':title,'length':len(main),'text_file':'crawl-pages/'+name,'text':main,'links':links,'status':'read'}
 except Exception as e:return {'url':url,'status':'failed','error':str(e)}
for level in range(4):
 todo=[u for u in queue if u not in seen][:160 if level else 40]; queue=[]; seen.update(todo)
 if not todo:break
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for r in pool.map(task,todo):
   results.append(r); print(json.dumps({k:v for k,v in r.items() if k not in ['text','links']},ensure_ascii=False),flush=True)
   if r.get('links'):queue.extend(r['links'])
 (P/'crawl-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 if len(results)>=250:break
