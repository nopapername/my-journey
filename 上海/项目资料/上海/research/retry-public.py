from collect import fetch,plain,search,read
from html.parser import HTMLParser
from urllib.parse import urljoin
from pathlib import Path
import concurrent.futures,json,re
P=Path(__file__).parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.href=None;self.label=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.label=[]
 def handle_data(self,d):
  if self.href:self.label.append(d)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.links.append({'url':self.href,'label':''.join(self.label).strip()});self.href=None
urls=[
 'https://www.shanghaidisneyresort.com/zh-cn/legal/park-rules/',
 'https://www.shanghaidisneyresort.com/zh-cn/legal/shanghai-disney-resort-real-name-ticketing-policy',
 'https://www.shanghaidisneyresort.com/zh-cn/information/transportation',
 'https://www.shmetro.com/',
 'https://www.hsay.com/'
]
records=[]
for url in urls:
 try:
  raw,final=fetch(url);text=plain(raw);parser=Links();parser.feed(raw)
  record={'url':url,'final':final,'text':text,'links':[dict(l,url=urljoin(final,l['url'])) for l in parser.links]}
  records.append(record)
  (P/('retry-'+str(len(records))+'.txt')).write_text('URL '+url+'\n'+text,encoding='utf-8')
  print(json.dumps({'url':url,'chars':len(text),'file':'retry-'+str(len(records))+'.txt','links':[l for l in record['links'] if re.search(r'票|食品|实名|证件|线路|站点|交通|品牌|关于|ticket|hours|calendar|park-rules',l['label']+' '+l['url'],re.I)]},ensure_ascii=False),flush=True)
 except Exception as e:records.append({'url':url,'error':str(e)});print(json.dumps({'url':url,'error':str(e)},ensure_ascii=False),flush=True)
(P/'retry-public.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
queries=['LOOKNOW 上海 安福路 地址','DECADE HUG Labelhood 上海 买手店 地址','桂源铺 阿姨奶茶 上海 品牌']
results=[]
for q in queries:
 try:
  entries=search(q)
  print(json.dumps({'query':q,'entries':entries[:8]},ensure_ascii=False),flush=True)
  results.extend(entries[:6])
 except Exception as e:print(json.dumps({'query':q,'error':str(e)},ensure_ascii=False),flush=True)
(P/'retry-search.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
