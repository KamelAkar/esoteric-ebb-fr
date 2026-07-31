# -*- coding: utf-8 -*-
"""Affiche les chaînes de _BLOCKED_typetree_517.json pas encore traduites dans blocked_fr.json.
Usage: python build_tmp/blocked_show_remaining.py [N] [filter]
 N = nb max (défaut 40) ; filter = 'feat'|'quest'|'bio'|'all' (défaut all)
Sortie: @@KEY@@ <json de la chaîne EN>  (KEY = index dans la liste blocked triée)
"""
import json, sys
b = sorted(json.load(open('translations/level_fr/_BLOCKED_typetree_517.json', encoding='utf-8')))
import os
fr = json.load(open('build_tmp/blocked_fr.json', encoding='utf-8')) if os.path.exists('build_tmp/blocked_fr.json') else {}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
filt = sys.argv[2] if len(sys.argv) > 2 else 'all'
def cat(s):
    if s.startswith('FEAT') or s.startswith('SECRET FEAT') or ' - ' in s[:40]: return 'feat'
    if s.startswith(('You ', 'Your ', 'The pale man', 'Speak', 'Find', 'Locate', 'Head', 'Return', 'Talk')): return 'quest'
    return 'bio'
rem = [(i, s) for i, s in enumerate(b) if s not in fr and (filt == 'all' or cat(s) == filt)]
print(f"RESTANT (filter={filt}): {len(rem)} | total non traduit {sum(1 for s in b if s not in fr)}/{len(b)} | traduit {len(fr)}")
for i, s in rem[:N]:
    print(f"@@{i}@@ {json.dumps(s, ensure_ascii=False)}")
