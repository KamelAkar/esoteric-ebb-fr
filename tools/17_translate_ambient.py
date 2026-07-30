"""Réinjecte les traductions FR des popups d'ambiance manqués.

Lit translations/_ambient_fr_done.tsv (level, path_id, french), charge chaque
level concerné, remplace le champ `text` du MonoBehaviour popup d'ambiance
correspondant, re-sérialise (UnityPy + typetree IL2CPP) et écrit dans le jeu
+ le staging dist.

Le bug manette était Steam Input, PAS la re-sérialisation — donc re-sérialiser
les levels est sûr. Voir memory/reference_gamepad_steam_input.md.
"""
import os, sys, csv, shutil
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

sys.stdout.reconfigure(encoding="utf-8")
GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
GD = f"{GAME}/Esoteric Ebb_Data"
ST = "dist/EsotericEbb-FR-Patch-v1.3.6/Esoteric Ebb_Data"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

gen = TypeTreeGenerator("6000.1.17f1")
gen.load_il2cpp(open(f"{GAME}/GameAssembly.dll", "rb").read(),
                open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read())
_o = gen.get_nodes
gen.get_nodes = lambda a, f: _o(a[:-4] if a.endswith('.dll') else a, f)

# charge les traductions groupées par level
by_level = {}
with open("translations/_ambient_fr_done.tsv", encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter='\t'):
        by_level.setdefault(int(row["level"]), {})[int(row["path_id"])] = row["french"]

tmp = "build_tmp/amb_out"
total_applied = 0
for lvl, mapping in sorted(by_level.items()):
    p = f"{GD}/level{lvl}"
    env = UnityPy.load(p)
    env.typetree_generator = gen
    applied = 0
    for o in env.objects:
        if o.type.name != "MonoBehaviour" or o.path_id not in mapping:
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if "text" not in tt:
            continue
        tt["text"] = mapping[o.path_id]
        o.save_typetree(tt)
        applied += 1
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    env.save(out_path=tmp)
    out = os.path.join(tmp, os.listdir(tmp)[0])
    shutil.copy(out, p)              # jeu
    shutil.copy(out, f"{ST}/level{lvl}")  # staging
    total_applied += applied
    print(f"level{lvl}: {applied}/{len(mapping)} popups traduits")

shutil.rmtree(tmp, ignore_errors=True)
print(f"\nTOTAL: {total_applied} popups d'ambiance traduits et réinjectés (jeu + staging)")
