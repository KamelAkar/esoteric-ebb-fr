import sys, os, shutil, json, collections
sys.stdout.reconfigure(encoding="utf-8")
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb"
DATA = GAME + "/Esoteric Ebb_Data"
DEP_FILES = ["globalgamemanagers", "globalgamemanagers.assets", "globalgamemanagers.assets.resS",
             "resources.assets", "resources.assets.resS"]

def make_gen():
    gen = TypeTreeGenerator("6000.1.17f1")
    gen.load_il2cpp(open(f"{GAME}/GameAssembly.dll", "rb").read(),
                    open("backups/VANILLA_FULL/il2cpp_data/Metadata/global-metadata.dat", "rb").read())
    _orig = gen.get_nodes
    gen.get_nodes = lambda a, f: _orig(a[:-4] if a.endswith(".dll") else a, f)
    return gen

def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[]")   # collapse list index for field-name grouping
    elif isinstance(node, str):
        if node.strip():
            yield (path, node)

# field names that are clearly NOT display text
SKIP_FIELDS = {".m_Name", ".m_Script", ".m_GameObject", ".m_CorrespondingSourceObject",
               ".m_PrefabInstance", ".m_PrefabAsset"}

def is_noise(field, val):
    if field in SKIP_FIELDS:
        return True
    if val.startswith(("event:/", "{", "guid", "GUID")) or "://" in val:
        return True
    if len(val) < 3:
        return True
    # pure identifier (no spaces, camelCase / snake / path)
    if " " not in val and ("/" in val or "_" in val or val.count(".") >= 2):
        return True
    return False

gen = make_gen()
ctx = "build_tmp/ctx_extract"
os.makedirs(ctx, exist_ok=True)
for f in DEP_FILES:
    dst = os.path.join(ctx, f)
    if not os.path.exists(dst):
        try: os.link(os.path.join(DATA, f), dst)
        except Exception: shutil.copy(os.path.join(DATA, f), dst)

records = []            # (level, path_id, field, value)
field_counter = collections.Counter()
for idx in range(25):
    lvl = os.path.join(ctx, f"level{idx}")
    shutil.copy(os.path.join(DATA, f"level{idx}"), lvl)
    env = UnityPy.load(lvl)
    env.typetree_generator = gen
    n = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            t = obj.read_typetree()
        except Exception:
            continue
        if not isinstance(t, dict):
            continue
        for field, val in walk(t):
            if is_noise(field, val):
                continue
            records.append((idx, obj.path_id, field, val))
            field_counter[field] += 1
            n += 1
    print(f"level{idx}: {n} champs string collectés", flush=True)
    del env
    import gc; gc.collect()

json.dump(records, open("build_tmp/level_strings_all.json", "w", encoding="utf-8"), ensure_ascii=False)
print("\nTOTAL enregistrements:", len(records))
print("champs distincts:", len(field_counter))
print("\n=== top champs (nom . -> count) ===")
for f, c in field_counter.most_common(40):
    print(f"  {c:>6}  {f}")
