from pathlib import Path
from collect import fetch, plain
import json

p = Path(__file__).parent
url = 'https://www.hsay.com/introduce/index.htm?v=1.7.1'
try:
    raw, final = fetch(url)
    body = plain(raw)
    (p/'brand-check.json').write_text(json.dumps({'url':url,'final':final,'text':body},ensure_ascii=False,indent=2),encoding='utf-8')
    print(body)
except Exception as e:
    print(type(e).__name__, str(e))
