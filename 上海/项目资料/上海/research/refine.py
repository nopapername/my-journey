from pathlib import Path
import json,re,urllib.parse
P=Path(__file__).parent
rows=json.loads((P/'review-candidates.json').read_text(encoding='utf-8'))
exclude_ids=set([1,2,10,11,12,13,14,25,27,28,29,30,31,32,33,34,35,38,39,40,41,42,43,64,69,70,71,72,73,74,75,76,77,80,82,83,84,85,86,87,88,89,90,92,93,94,95,96,97,98,99,100,101,102,108,109,110,111,112,113,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,167,168,169,170,174,175,179,187,191,248,254,255,256,257,259,262])
selected=[r for r in rows if r['id'] not in exclude_ids and 'trip.com/' not in r['url']]
for r in selected:
 t=r['text']; u=r['url']
 if 'travelchinaguide' in u:
  idx=t.find('Home /')
  if idx>=0:t=t[idx:]
  ends=[t.find(x) for x in ['Questions & Answers','Leave a Reply','Recommended Tours','About Us'] if t.find(x)>300]
  if ends:t=t[:min(ends)]
 elif 'chinahighlights' in u:
  idx=t.find('Home\n')
  if idx>=0:t=t[idx:]
  end=t.find('Start\n Your\n Journey')
  if end>300:t=t[:end]
 r['core_text']=t
(P/'selected-review.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
for b in range(4):
 group=selected[b::4]
 for chunk in range((len(group)+3)//4):
  rs=group[chunk*4:chunk*4+4]
  packet='\n\n'.join('ARTICLE '+str(r['id'])+'\nTITLE '+r['title']+'\nURL '+r['url']+'\n'+r['core_text'] for r in rs)
  (P/f'read-{b}-{chunk}.txt').write_text(packet,encoding='utf-8')
 print('GROUP',b,'COUNT',len(group),'CHUNKS',(len(group)+3)//4)
print('TOTAL',len(selected)); print(json.dumps([{'id':r['id'],'title':r['title']} for r in selected],ensure_ascii=False))

