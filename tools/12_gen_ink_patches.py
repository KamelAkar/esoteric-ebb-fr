"""Generate inkbulk find/replace dicts (read-only UnityPy) to sync FR from Dialogs
into the Ink JSON. Writes one dict TSV per sharedasset; apply with dotnet inkbulk
(AssetsTools, which preserves the .resS unlike UnityPy's save).

Anchored replacement: find = `"^<text>"`, replace = `"^<fr>"` — precise, matches the
Ink text field exactly. Multi-line / tab-containing texts are skipped.
"""
import sys
import os
import re
import json

sys.stdout.reconfigure(encoding="utf-8")
import UnityPy

GD = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb/Esoteric Ebb_Data"
OUT = "build_tmp/ink_patches"
PAIR = re.compile(r'"\^((?:\\"|[^"])+?)"(?:,"#",[^\]]*?)?"\^LOC_(\d+)"')
SKIP_PREFIX = ('.', 'FirstLine', 'Jor', 'NoUI', 'PlayMusic', 'Camera',
               'PCAnimation', 'StopAmbient', 'GlossaryOff', 'GlossaryOn', 'Cam')
# Dice-check prefix the game parser strips (must be preserved verbatim on the FR side)
ROLL_PREFIX = re.compile(r'^((?:(?:ROLL|DC|FC)\d+\s+\w+-)+|IROLL-|SPELL\s+[^-]+-)')


def load_fr(only):
    import csv, io
    env = UnityPy.load(f"{GD}/resources.assets")
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        d = obj.read()
        if d.m_Name == "Dialogs":
            sc = d.m_Script
            txt = bytes(sc).decode("utf-8") if isinstance(sc, (bytes, bytearray)) else sc
            rows = list(csv.reader(io.StringIO(txt)))
            return {r[0]: r[4] for r in rows[1:] if len(r) > 4 and r[0] in only}
    return {}


def main():
    only = set(json.load(open(sys.argv[1], encoding="utf-8")).keys())
    fr_map = load_fr(only)
    os.makedirs(OUT, exist_ok=True)
    total = 0
    manifest = []
    for i in range(30):
        p = f"{GD}/sharedassets{i}.assets"
        if not os.path.exists(p):
            continue
        env = UnityPy.load(p)
        pairs = []
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            try:
                d = obj.read()
                sc = d.m_Script
                content = bytes(sc).decode("utf-8", "replace") if isinstance(sc, (bytes, bytearray)) else sc
            except Exception:
                continue
            if "inkVersion" not in content[:200]:
                continue
            name = d.m_Name
            for m in PAIR.finditer(content):
                text, loc = m.group(1), m.group(2)
                if text.startswith(SKIP_PREFIX):
                    continue
                key = f"{name}_{loc}"
                if key not in fr_map:
                    continue
                fr = fr_map[key]
                # Preserve any dice-check prefix present in the Ink text (the CSV FR
                # is the prefix-less base translation). Prepend the Ink's prefix.
                pm = ROLL_PREFIX.match(text)
                if pm and not ROLL_PREFIX.match(fr):
                    fr = pm.group(1) + fr
                ink_un = text.replace('\\"', '"').replace('\\\\', '\\')
                if ink_un.strip() == fr.strip():
                    continue
                fr_esc = fr.replace('\\', '\\\\').replace('"', '\\"')
                if text.endswith(' ') and not fr_esc.endswith(' '):
                    fr_esc += ' '
                find = '"^' + text + '"'
                repl = '"^' + fr_esc + '"'
                # inkbulk splits on tab and converts \n/\r/\t — skip anything containing them
                if any(c in find or c in repl for c in ('\t', '\n', '\r')):
                    continue
                if '\\n' in find or '\\r' in find or '\\t' in find:
                    continue
                pairs.append((find, repl))
        if pairs:
            # dedup
            seen = {}
            for f, r in pairs:
                seen[f] = r
            fn = os.path.join(OUT, f"sharedassets{i}.tsv")
            with open(fn, "w", encoding="utf-8", newline="\n") as fh:
                for f, r in seen.items():
                    fh.write(f"{f}\t{r}\n")
            manifest.append(i)
            total += len(seen)
            print(f"sharedassets{i}: {len(seen)} patches")
    open(os.path.join(OUT, "manifest.json"), "w").write(json.dumps(manifest))
    print(f"\nTotal patches: {total}, sharedassets: {manifest}")


if __name__ == "__main__":
    main()
