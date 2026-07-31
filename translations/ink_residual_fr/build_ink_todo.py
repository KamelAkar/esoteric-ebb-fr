# -*- coding: utf-8 -*-
import re, glob, json, os
STEAM = r'C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb/Esoteric Ebb_Data'
tok = re.compile(rb'"\^((?:\\.|[^"\\])*)"')
EN = re.compile(r"\b(the|you|your|and|with|that|have|this|what|are|for|would|about|can|will|don|to|of|is|a|he|she|it|they|not|do|no|yes)\b", re.I)
FR = re.compile(r"[éèàçêâîôûùœ«»]|\b(vous|tu|le|la|les|une|des|est|pour|avec|pas|que|qui|ne|se|ce|vos|ton|oui|non|je|tout|mais|dans|es|au|du|il|elle|sur|un|te|ta|si)\b", re.I)
PREF = re.compile(r"^(\.[A-Za-z0-9_]+(?:[<>=!]=?-?\d+)?-)")

def has_ctrl(s):
    return any(ord(c) < 9 or (13 < ord(c) < 32) for c in s)

todo = {}   # displayed_text -> set(prefix)
for f in sorted(glob.glob(STEAM + '/sharedassets*.assets')):
    d = open(f, 'rb').read()
    for m in tok.finditer(d):
        raw = m.group(1)
        if b'\xef\xbf\xbd' in raw:
            continue
        try:
            s = json.loads('"' + raw.decode('utf-8') + '"')   # unescape propre
        except Exception:
            continue
        if has_ctrl(s):
            continue
        mp = PREF.match(s)
        prefix = mp.group(1) if mp else ""
        text = s[len(prefix):]
        body = text.strip()
        if len(body) < 6 or ' ' not in body:
            continue
        if EN.search(body) and not FR.search(body):
            todo.setdefault(text, set()).add(prefix)

out = {t: sorted(list(p)) for t, p in todo.items()}
json.dump(out, open('build_tmp/ink_todo_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('textes affichés EN distincts:', len(out))
print('mots ~', sum(len(t.split()) for t in out))
# variété de préfixes
from collections import Counter
pc = Counter()
for ps in out.values():
    for p in ps:
        pc[p if p else '(sans prefixe)'] += 1
print('préfixes distincts:', len(pc))
for p, c in pc.most_common(15):
    print(f'  {c:>4}  {p!r}')
