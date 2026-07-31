# -*- coding: utf-8 -*-
"""Affiche les valeurs EN de level_todo_map.json PAS ENCORE traduites dans
level_translations.json. Usage: python build_tmp/level_show_remaining.py [field] [N]
- field: filtrer sur un champ précis (ex: .Description) ou 'all'
- N: nombre max à afficher (défaut 60)
Format de sortie: @@KEY@@[field] valeur   (KEY = index stable dans le map)
"""
import json, sys, os
m = json.load(open('build_tmp/level_todo_map.json', encoding='utf-8'))
tr_path = 'build_tmp/level_translations.json'
tr = json.load(open(tr_path, encoding='utf-8')) if os.path.exists(tr_path) else {}
field = sys.argv[1] if len(sys.argv) > 1 else 'all'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
items = list(m.items())  # ordre stable (insertion = ordre du json)
rem = [(i, v, locs[0][2]) for i, (v, locs) in enumerate(items)
       if v not in tr and (field == 'all' or locs[0][2] == field)]
print(f"RESTANT (field={field}): {len(rem)} / total non traduit {sum(1 for v in m if v not in tr)} / total {len(m)}")
for i, v, f in rem[:N]:
    print(f"@@{i}@@[{f}] {v}")
