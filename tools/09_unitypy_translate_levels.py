"""Full FR translation of level files via UnityPy + IL2CPP typetree (PROPER re-serialization).

Why this works where the previous translator's files crashed:
- The previous translator re-serialized with UABE using a WRONG TMP type layout
  -> "level corrupted / Position out of bounds" crash once a fixed scene loaded.
- Here we generate the EXACT typetree from THIS game's GameAssembly.dll +
  global-metadata.dat, then re-serialize VANILLA level files with the FR text.
  Correct typetree => correct layout => no crash.

We translate ONLY the TMP `m_text` field (the visible text: lore cards, menu,
stat labels, etc.), matched by PathID against the previous translator's FR files.
Scene-load names live in OTHER fields, so they are never touched -> scenes load.

Usage: python tools/09_unitypy_translate_levels.py <vanilla_dir> <fr_dir> <deps_dir> <out_dir>
"""
import sys
import os
import shutil

sys.stdout.reconfigure(encoding="utf-8")

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
DEP_FILES = [
    "globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
    "resources.assets", "resources.assets.resS",
]


def make_gen():
    gen = TypeTreeGenerator("6000.1.17f1")
    gen.load_il2cpp(
        open(f"{GAME}/GameAssembly.dll", "rb").read(),
        open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read(),
    )
    # UnityPy/TypeTreeGeneratorAPI version mismatch: strip the ".dll" it appends.
    _orig = gen.get_nodes
    gen.get_nodes = lambda a, f: _orig(a[:-4] if a.endswith(".dll") else a, f)
    return gen


def read_text_map(path, gen):
    env = UnityPy.load(path)
    env.typetree_generator = gen
    m = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            t = obj.read_typetree()
        except Exception:
            continue
        if isinstance(t, dict) and t.get("m_text"):
            m[obj.path_id] = t["m_text"]
    return m


def translate_level(van_path, fr_path, deps_dir, out_dir, gen, idx):
    # context dir: deps + the level being processed
    ctx_v = os.path.join("build_tmp", f"ctxv_{idx}")
    ctx_f = os.path.join("build_tmp", f"ctxf_{idx}")
    for ctx, lvl in [(ctx_v, van_path), (ctx_f, fr_path)]:
        os.makedirs(ctx, exist_ok=True)
        for f in DEP_FILES:
            dst = os.path.join(ctx, f)
            if not os.path.exists(dst):
                try:
                    os.link(os.path.join(deps_dir, f), dst)
                except Exception:
                    shutil.copy(os.path.join(deps_dir, f), dst)
        shutil.copy(lvl, os.path.join(ctx, f"level{idx}"))

    frmap = read_text_map(os.path.join(ctx_f, f"level{idx}"), gen)

    env = UnityPy.load(os.path.join(ctx_v, f"level{idx}"))
    env.typetree_generator = gen
    applied = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        if obj.path_id not in frmap:
            continue
        try:
            t = obj.read_typetree()
        except Exception:
            continue
        if not (isinstance(t, dict) and "m_text" in t):
            continue
        fr = frmap[obj.path_id]
        if fr and fr != t["m_text"]:
            t["m_text"] = fr
            obj.save_typetree(t)
            applied += 1
    save_dir = os.path.join(out_dir, f"_save_{idx}")
    os.makedirs(save_dir, exist_ok=True)
    env.save(out_path=save_dir)
    # env.save writes into a folder; move the level out
    saved = os.path.join(save_dir, f"level{idx}")
    final = os.path.join(out_dir, f"level{idx}")
    shutil.move(saved, final)
    shutil.rmtree(save_dir, ignore_errors=True)
    shutil.rmtree(ctx_v, ignore_errors=True)
    shutil.rmtree(ctx_f, ignore_errors=True)
    return applied


def main():
    van_dir, fr_dir, deps_dir, out_dir = sys.argv[1:5]
    os.makedirs(out_dir, exist_ok=True)
    print("Generating IL2CPP typetree...")
    gen = make_gen()
    print("OK")
    total = 0
    for i in range(0, 25):
        vp = os.path.join(van_dir, f"level{i}")
        fp = os.path.join(fr_dir, f"level{i}")
        if not (os.path.exists(vp) and os.path.exists(fp)):
            continue
        n = translate_level(vp, fp, deps_dir, out_dir, gen, i)
        total += n
        print(f"level{i}: {n} m_text translated")
    print(f"\nTotal m_text translated across all levels: {total}")


if __name__ == "__main__":
    main()
