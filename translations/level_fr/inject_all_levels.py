# -*- coding: utf-8 -*-
"""Injecte les traductions level (build_tmp/level_translations.json) dans les level files
via typetree. Remplacement RÉCURSIF par valeur exacte, restreint aux path_id présents dans
le todo map (sûr). BACKUP live d'abord. Déploie live + dist.

Usage: python build_tmp/inject_all_levels.py [level_indices...]   (défaut: tous ceux qui ont des trads)
"""
import sys, os, shutil, json, collections
sys.stdout.reconfigure(encoding="utf-8")
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
DATA = GAME + "/Esoteric Ebb_Data"
DIST = "dist/EsotericEbb-FR-Patch-v1.3.6/Esoteric Ebb_Data"
DEP_FILES = ["globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
             "resources.assets", "resources.assets.resS"]
BACKUP = "backups/levels_pretexte"
os.makedirs(BACKUP, exist_ok=True)

def make_gen():
    gen = TypeTreeGenerator("6000.1.17f1")
    gen.load_il2cpp(open(f"{GAME}/GameAssembly.dll", "rb").read(),
                    open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read())
    _orig = gen.get_nodes
    gen.get_nodes = lambda a, f: _orig(a[:-4] if a.endswith(".dll") else a, f)
    return gen

trans = json.load(open("build_tmp/level_translations.json", encoding="utf-8"))
tmap = json.load(open("build_tmp/level_todo_map.json", encoding="utf-8"))

# per level: set of target path_ids, and english->french restricted to translated
level_pids = collections.defaultdict(set)
for eng, locs in tmap.items():
    if eng in trans:
        for lvl, pid, field in locs:
            level_pids[lvl].add(pid)

def repl(node, changed):
    if isinstance(node, dict):
        return {k: repl(v, changed) for k, v in node.items()}
    if isinstance(node, list):
        return [repl(v, changed) for v in node]
    if isinstance(node, str) and node in trans:
        changed[0] += 1
        return trans[node]
    return node

targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else sorted(level_pids)
gen = make_gen()
ctx = "build_tmp/ctx_inject"
os.makedirs(ctx, exist_ok=True)
for f in DEP_FILES:
    dst = os.path.join(ctx, f)
    if not os.path.exists(dst):
        try: os.link(os.path.join(DATA, f), dst)
        except Exception: shutil.copy(os.path.join(DATA, f), dst)

for idx in targets:
    pids = level_pids.get(idx)
    if not pids:
        continue
    live = os.path.join(DATA, f"level{idx}")
    bak = os.path.join(BACKUP, f"level{idx}.before")
    if not os.path.exists(bak):
        shutil.copy(live, bak)
    lvl = os.path.join(ctx, f"level{idx}")
    shutil.copy(live, lvl)          # depuis le LIVE (préserve m_text FR v1.3.4)
    env = UnityPy.load(lvl)
    env.typetree_generator = gen
    total = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour" or obj.path_id not in pids:
            continue
        try:
            t = obj.read_typetree()
        except Exception:
            continue
        changed = [0]
        nt = repl(t, changed)
        if changed[0]:
            obj.save_typetree(nt)
            total += changed[0]
    if total == 0:
        print(f"level{idx}: déjà à jour (0 changement), ignoré", flush=True)
        del env
        import gc; gc.collect()
        continue
    save_dir = os.path.join(ctx, f"_save_{idx}")
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)
    env.save(out_path=save_dir)
    out = os.path.join(save_dir, f"level{idx}")
    if not os.path.exists(out):
        print(f"level{idx}: ATTENTION env.save n'a rien écrit malgré {total} changements", flush=True)
        del env
        import gc; gc.collect()
        continue
    shutil.copy(out, live)
    shutil.copy(out, os.path.join(DIST, f"level{idx}"))
    print(f"level{idx}: {total} champs remplacés -> déployé live+dist", flush=True)
    del env
    import gc; gc.collect()

print("Injection terminée pour:", targets)
