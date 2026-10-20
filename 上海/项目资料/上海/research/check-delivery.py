from pathlib import Path
from datetime import date,timedelta
import re,json,struct,zipfile

p=Path(__file__).parent.parent
main=(p/'上海10月下旬轻松旅行攻略.md').read_text(encoding='utf-8')
index=(p/'攻略来源索引.md').read_text(encoding='utf-8')
reviews=json.loads((p/'research/final-reviews.json').read_text(encoding='utf-8'))
xhs=json.loads((p/'research/xhs-reviewed.json').read_text(encoding='utf-8'))
checks=[]
for label,text in [('main',main),('index',index)]:
    assert '\ufffd' not in text
    assert text.count('```')%2==0
    checks.append((label,len(text)))
for relative in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',main):
    f=p/relative
    assert f.exists(),relative
    data=f.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    wh=struct.unpack('>II',data[16:24])
    checks.append((relative,wh))
assert len(reviews)==140
assert sum(r['countable'] for r in reviews)==113
assert '113 篇' in main and '113 篇' in index
assert len(xhs)==10
assert len({r['url'] for r in xhs})==10
assert all('?' not in r['url'] and 'xsec_' not in r['url'] for r in xhs)
assert len(re.findall(r'^\| X\d{2} \|',index,re.M))==10
assert len(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',main))==6
assert '6号楼1楼' in main and '275号5弄1楼' in main
assert '单人两天门票费合计' in main
assert 1200+960+240+210+400+0+300==3310
assert 3000+1680+400+490+800+600+600==7570
assert 1400+960+480+240+450+0+350==3880
assert 3500+1680+800+560+900+600+700==8740
assert date(2026,10,23).weekday()==4
assert (date(2026,10,27)-date(2026,10,23)).days==4
assert (date(2026,10,29)-date(2026,10,27)).days==2
assert (date(2026,10,30)-date(2026,10,27)).days==3
assert all(len(re.findall(r'^\| A\d{3}／',index,re.M))==113 for _ in [0])
local=[]
for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',main+'\n'+index):
    if link.startswith(('https://','http://','#')):continue
    assert (p/link).exists(),link
    local.append(link)
bundle=p/'上海10月下旬攻略与路线图.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for f in [p/'上海10月下旬轻松旅行攻略.md',p/'攻略来源索引.md',*sorted((p/'路线图').glob('*.png'))]:
        z.write(f,f.relative_to(p))
print(json.dumps({'checks':'passed','files':checks,'local_links':local,'reviewed':140,'accepted':113,'xhs_text_notes':len(xhs),'bundle':str(bundle)},ensure_ascii=False))
