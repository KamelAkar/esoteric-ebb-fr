"""Translate the glossary Responses baked into the level files.

The game reads glossary passive-check reveals from a MonoBehaviour field
`GlossaryTerms[i].Response` INSIDE each level file (NOT the resources CSV — that
copy is unused for these). We build an English->FR map from the resources CSV
(vanilla EN vs translated FR, by ID) and apply it to every level's Response field
via UnityPy + IL2CPP typetree, then re-serialize.

Usage: python tools/13_translate_level_glossary.py <in_levels_dir> <out_dir>
"""
import sys
import os
import shutil

sys.stdout.reconfigure(encoding="utf-8")
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
GD = f"{GAME}/Esoteric Ebb_Data"
DEP = ["globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
       "resources.assets", "resources.assets.resS"]

# Stat display names shown in the dice-check badge (fields Nickname / SelectInfoTitle).
# Selection is by 3-letter code (str/dex/...), so these are display-only -> safe.
STAT_NAMES = {
    "Strength": "Force", "Dexterity": "Dextérité", "Constitution": "Constitution",
    "Intelligence": "Intelligence", "Wisdom": "Sagesse", "Charisma": "Charisme",
}


def make_gen():
    gen = TypeTreeGenerator("6000.1.17f1")
    gen.load_il2cpp(open(f"{GAME}/GameAssembly.dll", "rb").read(),
                    open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read())
    _o = gen.get_nodes
    gen.get_nodes = lambda a, f: _o(a[:-4] if a.endswith(".dll") else a, f)
    return gen


def build_map():
    import csv, io
    def gloss(path):
        env = UnityPy.load(path)
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            d = obj.read()
            if d.m_Name == "GlossaryTerms":
                sc = d.m_Script
                txt = bytes(sc).decode("utf-8") if isinstance(sc, (bytes, bytearray)) else sc
                rows = list(csv.reader(io.StringIO(txt)))
                EN = rows[0].index("ENGLISH")
                return {r[0]: r[EN] for r in rows[1:] if len(r) > EN}
        return {}
    van = gloss("backups/VANILLA_FULL/resources.assets")
    fr = gloss(f"{GD}/resources.assets")
    m = {}
    for gid, en in van.items():
        f = fr.get(gid, "")
        if en and f and en != f:
            m[en] = f
    return m


def main():
    in_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    print("building EN->FR glossary map...")
    gmap = build_map()
    print(f"  {len(gmap)} entries")
    gen = make_gen()
    total = 0
    for i in range(25):
        lvl = os.path.join(in_dir, f"level{i}")
        if not os.path.exists(lvl):
            continue
        # resume support: skip levels already produced
        if os.path.exists(os.path.join(out_dir, f"level{i}")):
            print(f"level{i}: already done, skipped")
            continue
        ctx = os.path.join("build_tmp", f"gtx_{i}")
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
        applied = 0
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                t = obj.read_typetree()
            except Exception:
                continue
            if not isinstance(t, dict):
                continue
            changed = False
            # glossary responses
            if isinstance(t.get("GlossaryTerms"), list):
                for e in t["GlossaryTerms"]:
                    if isinstance(e, dict) and e.get("Response") in gmap:
                        e["Response"] = gmap[e["Response"]]
                        changed = True
                        applied += 1
            # dice-check stat display names
            for fld in ("Nickname", "SelectInfoTitle"):
                if t.get(fld) in STAT_NAMES:
                    t[fld] = STAT_NAMES[t[fld]]
                    changed = True
                    applied += 1
            if changed:
                obj.save_typetree(t)
        if applied:
            sd = os.path.join(out_dir, f"_s{i}")
            os.makedirs(sd, exist_ok=True)
            env.save(out_path=sd)
            shutil.move(os.path.join(sd, f"level{i}"), os.path.join(out_dir, f"level{i}"))
            shutil.rmtree(sd, ignore_errors=True)
        else:
            shutil.copy(lvl, os.path.join(out_dir, f"level{i}"))
        shutil.rmtree(ctx, ignore_errors=True)
        print(f"level{i}: {applied} glossary responses translated")
        total += applied
    print(f"\nTotal glossary responses translated: {total}")


if __name__ == "__main__":
    main()
