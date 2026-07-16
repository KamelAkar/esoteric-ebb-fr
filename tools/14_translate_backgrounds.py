"""Translate the 18 character-creation backgrounds (PCBackgrounds[].name/.desc)
baked into level0's MonoBehaviour, via UnityPy + IL2CPP typetree.

Selection is by index (PCBackgroundIndex), so the name is display-only -> safe.

Usage: python tools/14_translate_backgrounds.py <in_level0> <out_level0>
"""
import sys
import os
import json
import shutil

sys.stdout.reconfigure(encoding="utf-8")
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
GD = f"{GAME}/Esoteric Ebb_Data"
DEP = ["globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
       "resources.assets", "resources.assets.resS"]


def main():
    in_lvl, out_lvl = sys.argv[1], sys.argv[2]
    fr = json.load(open("translations/backgrounds_fr.json", encoding="utf-8"))
    gen = TypeTreeGenerator("6000.1.17f1")
    gen.load_il2cpp(open(f"{GAME}/GameAssembly.dll", "rb").read(),
                    open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read())
    _o = gen.get_nodes
    gen.get_nodes = lambda a, f: _o(a[:-4] if a.endswith(".dll") else a, f)

    ctx = "build_tmp/bgtx"
    os.makedirs(ctx, exist_ok=True)
    for f in DEP:
        dst = os.path.join(ctx, f)
        if not os.path.exists(dst):
            try:
                os.link(f"{GD}/{f}", dst)
            except Exception:
                shutil.copy(f"{GD}/{f}", dst)
    shutil.copy(in_lvl, os.path.join(ctx, "level0"))
    env = UnityPy.load(os.path.join(ctx, "level0"))
    env.typetree_generator = gen
    applied = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            t = obj.read_typetree()
        except Exception:
            continue
        if not (isinstance(t, dict) and "PCBackgrounds" in t and isinstance(t["PCBackgrounds"], list)):
            continue
        changed = False
        for e in t["PCBackgrounds"]:
            if isinstance(e, dict) and e.get("name") in fr:
                tr = fr[e["name"]]
                if e.get("desc"):
                    e["desc"] = tr["desc"]
                e["name"] = tr["name"]
                changed = True
                applied += 1
        if changed:
            obj.save_typetree(t)
    if applied:
        sd = "build_tmp/_bgsave"
        os.makedirs(sd, exist_ok=True)
        env.save(out_path=sd)
        shutil.move(os.path.join(sd, "level0"), out_lvl)
        shutil.rmtree(sd, ignore_errors=True)
    else:
        shutil.copy(in_lvl, out_lvl)
    shutil.rmtree(ctx, ignore_errors=True)
    print(f"backgrounds translated: {applied}")


if __name__ == "__main__":
    main()
