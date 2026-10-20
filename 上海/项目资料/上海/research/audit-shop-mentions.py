"""Count distinct reviewed Xiaohongshu notes mentioning candidate venues.

Mentions are discovery signals, not independent endorsements or quality votes.
"""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parent
reviews = json.loads((root / "xhs-v2-reviews.json").read_text(encoding="utf-8"))
bodies = {row["id"]: row["body"] for row in json.loads(
    (root / "xhs-v2-read-cache.json").read_text(encoding="utf-8"))}
aliases = {
    "瀚祥本帮面馆": ["瀚祥"],
    "蒋掌柜": ["蒋掌柜"],
    "APOLI ITABAKERY": ["APOLI", "Apoli"],
    "大壶春": ["大壶春"],
    "南翔馒头店": ["南翔馒头"],
    "沈大成": ["沈大成"],
    "光明邨": ["光明邨", "光明村"],
    "味香斋": ["味香斋"],
    "茂隆餐厅": ["茂隆"],
    "红宝石": ["红宝石"],
    "红茶公司": ["红茶公司", "Charlietown"],
    "OT另茶": ["OT另茶", "OT 另茶"],
    "椿田熟成茶行": ["椿田"],
    "栗其": ["栗其"],
    "阿嬷手作": ["阿嬷手作"],
    "多抓鱼": ["多抓鱼"],
    "Wiggle Wiggle": ["Wiggle Wiggle"],
    "in the PARK": ["in the PARK"],
    "GOODBAI": ["GOODBAI"],
    "蕾虎": ["蕾虎", "LABELHOOD"],
    "Badmarket": ["Badmarket"],
    "fRUITYSHOP": ["fRUITYSHOP"],
    "LOOKNOW": ["LOOKNOW"],
    "sunflour": ["sunflour"],
    "ALTER": ["ALTER"],
    "思南公馆": ["思南公馆", "思南"],
    "复兴公园": ["复兴公园"],
    "新天地": ["新天地"],
    "外滩源": ["外滩源"],
    "武康路": ["武康路"],
    "安福路": ["安福路"],
}
for name, terms in aliases.items():
    codes = []
    for review in reviews:
        if not review["countable"]:
            continue
        body = bodies.get(review["id"], "")
        if any(re.search(re.escape(term), body, re.I) for term in terms):
            codes.append(review["code"])
    print(f"{name}\t{len(codes)}\t{','.join(codes)}")
