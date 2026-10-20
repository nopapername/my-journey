from pathlib import Path
import re,html,json,importlib.util,urllib.parse
p=Path(r'D:\web3\code_project\旅游规划\上海\research')
raw=(p/'next-1.html').read_text(encoding='utf-8')
for match in re.finditer(r'<a[^>]+href=["\x27]([^"\x27]+)["\x27][^>]*>(.*?)</a>',raw,re.S):
 text=re.sub('<[^>]+>','',match.group(2)).strip()
 if text and (any(x in text for x in ['上海','游','武康','攻略','奶茶']) or len(text)>15):
  print(json.dumps({'url':html.unescape(match.group(1)),'title':html.unescape(text[:150])},ensure_ascii=False))
s=importlib.util.spec_from_file_location('tc',p/'collect.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
for q in ['武康路 安福路 买手店 攻略','上海 美食 奶茶 桂源铺 攻略','上海迪士尼 游记 攻略']:
 url='https://www.baidu.com/s?'+urllib.parse.urlencode({'wd':q,'rn':50})
 raw,final=m.fetch(url)
 (p/('baidu-'+str(len(list(p.glob('baidu-*.html'))))+'.html')).write_text(raw,encoding='utf-8')
 print(json.dumps({'query':q,'text':m.plain(raw)[:7000],'mu':re.findall(r'\bmu=["\x27]([^"\x27]+)',raw)},ensure_ascii=False))
