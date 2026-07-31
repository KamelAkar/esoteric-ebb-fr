# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
"""Affiche les textes Ink EN pas encore dans build_tmp/ink_fr.json.
Usage: python build_tmp/ink_show_remaining.py [N] [filtre-prefixe]
 N = max (défaut 50). filtre = sous-chaîne de préfixe (ex '.Snell') ou 'all'.
Sortie: @@KEY@@ <json texte>   (KEY = index dans sorted(ink_todo_map keys))
"""
import json, sys, os
todo = sorted(json.load(open('build_tmp/ink_todo_map.json', encoding='utf-8')).keys())
tmap = json.load(open('build_tmp/ink_todo_map.json', encoding='utf-8'))
fr = json.load(open('build_tmp/ink_fr.json', encoding='utf-8')) if os.path.exists('build_tmp/ink_fr.json') else {}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 50
filt = sys.argv[2] if len(sys.argv) > 2 else 'all'
rem = [(i, t) for i, t in enumerate(todo) if t not in fr and (filt == 'all' or any(filt in p for p in tmap[t]))]
print(f"RESTANT (filtre={filt}): {len(rem)} | total non traduit {sum(1 for t in todo if t not in fr)}/{len(todo)} | traduit {len(fr)}")
for i, t in rem[:N]:
    print(f"@@{i}@@ {json.dumps(t, ensure_ascii=False)}")
