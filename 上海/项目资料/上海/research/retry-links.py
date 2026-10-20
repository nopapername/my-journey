from collect import fetch,plain
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import json,sys,re
P=Path(__file__).parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.href=None;self.text=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.text=[]
 def handle_data(self,d):
  if self.href:self.text.append(d)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.links.append({'url':self.href,'label':''.join(self.text).strip()});self.href=None
url=sys.argv[1]
raw,final=fetch(url)
l=Links();l.feed(raw)
links=[dict(x,url=urljoin(final,x['url'])) for x in l.links]
record={'url':url,'final':final,'text':plain(raw),'links':links}
(P/'retry-disney-home.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'url':final,'text':record['text'][:10000],'links':[x for x in links if re.search(r'规则|须知|实名|交通|运营|门票|policy|rules|ticket|transport',x['label']+' '+x['url'],re.I)]},ensure_ascii=False))
