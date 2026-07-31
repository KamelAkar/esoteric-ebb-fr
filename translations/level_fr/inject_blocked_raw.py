# -*- coding: utf-8 -*-
"""Injecte des traductions dans les level files par REMPLACEMENT DE CHAÎNES BRUTES
(Unity aligned string) au niveau de l'objet, SANS typetree. Contourne les objets
dont le typetree est cassé (LocalizationManager, Idea...). env.save recalcule les
offsets du fichier -> le FR plus long est OK.

Entrée : build_tmp/blocked_fr.json = {english: french}
Usage : python build_tmp/inject_blocked_raw.py [level_indices...]  (défaut: tous)
Charge le level LIVE (préserve les 741 déjà injectés). Backup dans backups/levels_BLOCKED_pre/.
"""
import sys, os, shutil, struct, json
sys.stdout.reconfigure(encoding="utf-8")
import UnityPy

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
DATA = GAME + "/Esoteric Ebb_Data"
DIST = "dist/EsotericEbb-FR-Patch-v1.3.6/Esoteric Ebb_Data"
DEP = ["globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
       "resources.assets", "resources.assets.resS"]
BACKUP = "backups/levels_BLOCKED_pre"
os.makedirs(BACKUP, exist_ok=True)

trans = json.load(open("build_tmp/blocked_fr.json", encoding="utf-8"))
# precompute needle(bytes)->replacement(bytes) with aligned padding
PAIRS = []
for eng, fr in trans.items():
    eb = eng.encode("utf-8"); fb = fr.encode("utf-8")
    needle = struct.pack("<i", len(eb)) + eb
    repl = struct.pack("<i", len(fb)) + fb + b"\x00" * ((-len(fb)) % 4)
    eng_pad = (-len(eb)) % 4
    PAIRS.append((needle, eng_pad, repl))
# longest needle first (avoid partial overlaps)
PAIRS.sort(key=lambda p: -len(p[0]))

def edit_blob(blob):
    changed = 0
    for needle, eng_pad, repl in PAIRS:
        if needle not in blob:
            continue
        pieces = []; pos = 0
        while True:
            i = blob.find(needle, pos)
            if i < 0:
                pieces.append(blob[pos:]); break
            pieces.append(blob[pos:i])
            pieces.append(repl)
            pos = i + len(needle) + eng_pad
            changed += 1
        blob = b"".join(pieces)
    return blob, changed

targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else list(range(25))
ctx = "build_tmp/ctx_blocked"
os.makedirs(ctx, exist_ok=True)
for f in DEP:
    d = os.path.join(ctx, f)
    if not os.path.exists(d):
        try: os.link(os.path.join(DATA, f), d)
        except: shutil.copy(os.path.join(DATA, f), d)

for idx in targets:
    live = os.path.join(DATA, f"level{idx}")
    bak = os.path.join(BACKUP, f"level{idx}.before")
    if not os.path.exists(bak):
        shutil.copy(live, bak)
    lvl = os.path.join(ctx, f"level{idx}")
    shutil.copy(live, lvl)
    env = UnityPy.load(lvl)
    total = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        blob = obj.get_raw_data()
        # quick prefilter: any needle present?
        newblob, c = edit_blob(blob)
        if c:
            obj.set_raw_data(newblob)
            total += c
    if total == 0:
        print(f"level{idx}: 0 remplacement", flush=True)
        del env; import gc; gc.collect(); continue
    save_dir = os.path.join(ctx, f"_save_{idx}")
    if os.path.exists(save_dir): shutil.rmtree(save_dir)
    os.makedirs(save_dir)
    env.save(out_path=save_dir)
    out = os.path.join(save_dir, f"level{idx}")
    if not os.path.exists(out):
        print(f"level{idx}: ERREUR env.save n'a rien écrit ({total} chgts)", flush=True)
        del env; import gc; gc.collect(); continue
    shutil.copy(out, live)
    shutil.copy(out, os.path.join(DIST, f"level{idx}"))
    print(f"level{idx}: {total} chaînes brutes remplacées -> déployé live+dist", flush=True)
    del env; import gc; gc.collect()

print("Injection brute terminée pour:", targets)
