import argparse, concurrent.futures, hashlib, html, json, pathlib, re, time, urllib.parse, urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).parent
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read(4000000)
        charset = response.headers.get_content_charset()
        if not charset:
            match = re.search(br'charset\s*=\s*["\x27]?([\w-]+)', data[:10000], re.I)
            charset = match.group(1).decode() if match else 'utf-8'
        try:
            decoded = data.decode(charset, errors='replace')
        except LookupError:
            decoded = data.decode('utf-8', errors='replace')
        return decoded, response.url

class Plain(HTMLParser):
    def __init__(self):
        super().__init__(); self.out=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ['script','style','noscript']: self.skip += 1
        elif tag in ['p','div','br','li','h1','h2','h3','section','article']: self.out.append('\n')
    def handle_endtag(self,tag):
        if tag in ['script','style','noscript'] and self.skip: self.skip -= 1
    def handle_data(self,data):
        if not self.skip: self.out.append(data)

def plain(raw):
    p=Plain(); p.feed(raw)
    return re.sub(r'\n\s*\n+', '\n', re.sub(r'[ \t]+',' ',''.join(p.out))).strip()

def search(query):
    raw,_ = fetch('https://www.bing.com/search?' + urllib.parse.urlencode({'q':query,'count':50}))
    entries=[]
    for block in re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>',raw,re.S):
        m=re.search(r'<h2[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',block,re.S)
        if not m: continue
        url=html.unescape(m.group(1)); title=plain(m.group(2))
        if 'bing.com/ck/a' in url:
            args=urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            encoded=args.get('u',[''])[0]
            if encoded.startswith('a1'):
                import base64
                try: url=base64.urlsafe_b64decode(encoded[2:]+'===').decode()
                except Exception: pass
        if url.startswith('http') and 'bing.com' not in urllib.parse.urlparse(url).netloc:
            entries.append({'title':title,'url':url,'query':query,'snippet':plain(block)})
    return entries

def read(entry):
    try:
        raw, final=fetch(entry['url']); text=plain(raw)
        title_match=re.search(r'<title[^>]*>(.*?)</title>',raw,re.S|re.I)
        title=plain(title_match.group(1)) if title_match else entry['title']
        digest=hashlib.sha256(text.encode()).hexdigest()
        fname=digest[:16]+'.txt'; (ROOT/'pages').mkdir(exist_ok=True)
        (ROOT/'pages'/fname).write_text(text,encoding='utf-8')
        return dict(entry, page_title=title,final_url=final,length=len(text),sha256=digest,text_file='pages/'+fname,status='read',text=text)
    except Exception as e:
        return dict(entry,status='failed',error=str(e))

def run(job):
    config=json.loads((ROOT/(job+'.json')).read_text(encoding='utf-8'))
    candidates={}
    for query in config['queries']:
        try:
            entries=search(query)
            print(json.dumps({'query':query,'results':len(entries)},ensure_ascii=False),flush=True)
            for e in entries: candidates.setdefault(e['url'],e)
        except Exception as e: print(json.dumps({'query':query,'error':str(e)},ensure_ascii=False),flush=True)
    if config.get('urls'):
        for u in config['urls']: candidates.setdefault(u,{'url':u,'title':u,'query':'direct'})
    (ROOT/(job+'-candidates.json')).write_text(json.dumps(list(candidates.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(read,candidates.values()):
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k not in ['text','snippet']},ensure_ascii=False),flush=True)
    (ROOT/(job+'-results.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('job'); args=parser.parse_args(); run(args.job)
