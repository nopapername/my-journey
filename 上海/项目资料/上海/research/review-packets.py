from pathlib import Path
import json,re,urllib.parse
P=Path(__file__).parent
rows=json.loads((P/'review-candidates.json').read_text(encoding='utf-8'))
exclude=['weather/january','weather/february','weather/march','weather/april','weather/may','weather/june','weather/july','weather/august','weather/december','weather-january','weather-february','weather-march','weather-april','weather-may','weather-june','weather-july','weather-august','weather-december','visa-free','picture/','video.','/package/tour','/group/','/package/shanghai/12','/package/shanghai/09','/package/shanghai/10d','/package/shanghaitour','/package/suzhou','/package/shanghai.htm','/map/','trip.com/','hong-kong-disney','tokyo-','california','walt-disney','paris','shanghai.gov.cn/','shanghaidisneyresort.com/','meet-in-shanghai.net/cn/','yugarden.com','history.htm','economy.htm','geography.htm','area_zip','events.htm','worldexpo','/summer','/winter','travels/','thepaper.cn','chinawondersguide','chinahighlights.com/travelguide']
selected=[]
for r in rows:
 if any(x in r['url'] for x in exclude):continue
 if len(r['text'])<1200:continue
 selected.append(r)
# Prefer Shanghai travel guide detail pages and article text; remove obvious non-guides during human review.
print('TOTAL',len(selected))
for b in range(4):
 packet=[]
 for r in selected[b::4]:
  t=r['text']; u=r['url']
  if 'travelchinaguide' in u:
   idx=t.find('Home\n')
   if idx>=0:t=t[idx:]
   ends=[t.find(x) for x in ['- Last updated','Questions & Answers','Leave a Reply','China Tour Packages','Select Travel Date'] if t.find(x)>200]
   if ends:t=t[:min(ends)+200]
  elif 'chinahighlights' in u:
   idx=t.find('Home\n')
   if idx>=0:t=t[idx:]
   end=t.find('Start\n Your\n Journey')
   if end>300:t=t[:end]
  elif 'loongwander' in u or 'gochina' in u or 'greentour' in u:pass
  # Full core text preserved for review, not a search snippet.
  packet.append({'id':r['id'],'title':r['title'],'url':u,'text':t})
 (P/f'packet{b}.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
 print('BATCH',b,'COUNT',len(packet),'CHARS',sum(len(x['text']) for x in packet))
print(json.dumps([{'id':r['id'],'title':r['title'],'url':r['url']} for r in selected],ensure_ascii=False))
