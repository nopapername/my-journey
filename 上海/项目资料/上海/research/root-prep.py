from pathlib import Path
import json
p=Path(r'D:\web3\code_project\旅游规划\上海\research')
rows=json.loads((p/'selected-review.json').read_text(encoding='utf-8'))
for r in rows[0::4]:
    (p/f"root-{r['id']}.txt").write_text(f"ARTICLE {r['id']}\nTITLE {r['title']}\nURL {r['url']}\n"+r['core_text'],encoding='utf-8')
(p/'review-metadata.json').write_text(json.dumps([{'id':r['id'],'title':r['title'],'url':r['url'],'group':i%4,'chars':len(r['core_text'])} for i,r in enumerate(rows)],ensure_ascii=False,indent=2),encoding='utf-8')
print([(r['id'],len(r['core_text'])) for r in rows[0::4]])
