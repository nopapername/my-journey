from pathlib import Path
import json,re,hashlib,html
P=Path(__file__).parent
rows=json.loads((P/'crawl-results.json').read_text(encoding='utf-8'))
for file in ['city-results.json','disney-results.json','food-results.json']:
 if (P/file).exists():
  for row in json.loads((P/file).read_text(encoding='utf-8')):
   if row.get('status')=='read':
    row['title']=row.get('page_title',row.get('title','')); rows.append(row)
seen=set(); clean=[]
for r in rows:
 if r.get('status')!='read' or r.get('length',0)<700:continue
 url=r.get('final_url',r['url']).split('#')[0]
 if any(x in url for x in ['verify.','baike.','map.','hotels.ctrip','shanghai.gov.cn/nw','tours/','tour/']):continue
 text=r.get('text','')
 if not text or not any(w in (r.get('title','')+' '+text[:8000]).lower() for w in ['shanghai','上海','迪士尼','外滩','豫园','陆家嘴']):continue
 sig=hashlib.sha256(re.sub(r'\s+','',text).encode()).hexdigest()
 if url in seen or sig in seen:continue
 seen.update([url,sig]); r['id']=len(clean)+1; r['date']='未确认'; clean.append(r)
(P/'review-candidates.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2),encoding='utf-8')
for batch in range(4):
 selected=clean[batch::4]
 blocks=[]
 for r in selected:
  t=r['text']
  # Strip repeated site navigation while preserving relevant article paragraphs.
  if 'Home\n' in t:t=t[t.find('Home\n'):]
  # Budgeted review packet, always includes title, url and content; source remains full in cache.
  blocks.append({'id':r['id'],'title':r['title'],'url':r['url'],'text':t[:7500]})
 (P/f'review-batch-{batch}.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidates':len(clean),'read_pages':len([x for x in rows if x.get('status')=='read']),'titles':[{'id':r['id'],'title':r['title'],'url':r['url'],'length':r['length']} for r in clean]},ensure_ascii=False))
