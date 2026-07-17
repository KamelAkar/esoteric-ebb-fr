"""Extract distinct English ambient-popup `.text` fields from all level files
(MonoBehaviours with PopupBox/BoonPopup/NeutralPopup + a `text` field).
Writes a TSV of distinct English texts for translation.
"""
import sys
import os
import re
import shutil

sys.stdout.reconfigure(encoding="utf-8")
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
GD = f"{GAME}/Esoteric Ebb_Data"
DEP = ["globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
       "resources.assets", "resources.assets.resS"]


def is_en(s):
    return bool(re.search(r"\b(the|and|of|is|are|a|an|to|you|it|his|its|was|were|this|that|there|with|for)\b", s, re.I)) \
        and not re.search(r"[éèêàçùôîâûœ«»]", s)


def main():
    gen = TypeTreeGenerator("6000.1.17f1")
    gen.load_il2cpp(open(f"{GAME}/GameAssembly.dll", "rb").read(),
                    open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read())
    _o = gen.get_nodes
    gen.get_nodes = lambda a, f: _o(a[:-4] if a.endswith(".dll") else a, f)
    seen = {}
    for i in range(25):
        lvl = f"backups/TRANSLATED_LEVELS/level{i}"
        if not os.path.exists(lvl):
            continue
        ctx = f"build_tmp/actx_{i}"
        os.makedirs(ctx, exist_ok=True)
        for f in DEP:
            dst = os.path.join(ctx, f)
            if not os.path.exists(dst):
                try:
                    os.link(f"{GD}/{f}", dst)
                except Exception:
                    shutil.copy(f"{GD}/{f}", dst)
        shutil.copy(lvl, os.path.join(ctx, f"level{i}"))
        env = UnityPy.load(os.path.join(ctx, f"level{i}"))
        env.typetree_generator = gen
        cnt = 0
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                t = obj.read_typetree()
            except Exception:
                continue
            if not isinstance(t, dict):
                continue
            if "text" in t and ("PopupBox" in t or "BoonPopup" in t or "NeutralPopup" in t):
                tx = t["text"]
                if isinstance(tx, str) and len(tx.strip()) > 3 and is_en(tx) and tx not in seen:
                    seen[tx] = True
                    cnt += 1
        shutil.rmtree(ctx, ignore_errors=True)
        print(f"level{i}: +{cnt} new distinct (total {len(seen)})")
    with open("translations/_ambient_en.tsv", "w", encoding="utf-8", newline="\n") as f:
        for tx in seen:
            f.write(tx.replace("\t", " ").replace("\n", "\\n") + "\n")
    print(f"\nTotal distinct English ambient texts: {len(seen)}")


if __name__ == "__main__":
    main()
