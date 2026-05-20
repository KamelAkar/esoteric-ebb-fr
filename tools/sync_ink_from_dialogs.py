"""Synchronize Ink JSON TextAssets with FR translations from Dialogs CSV.

For each TextAsset, parses Ink JSON to extract (text, LOC_N) pairs.
For each pair, builds key = <TextAssetName>_<N> and looks up FR in Dialogs.
If Ink text differs from Dialogs FR, generates patch entry.

Usage: python sync_ink_from_dialogs.py <sharedassets_file> <out_tsv>
"""
import sys
import csv
import json
import re
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DOTNET = REPO / "tools" / "dotnet-deploy" / "bin" / "Debug" / "net8.0" / "dotnet-deploy.exe"
DIALOGS_PATH = Path(r"C:/Users/Ravnow/AppData/Local/Temp/Dialogs_check.json")

def load_dialogs():
    """Load Dialogs CSV: returns dict key → fr_text."""
    result = {}
    with open(DIALOGS_PATH, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        en_idx = header.index("EN")
        for row in reader:
            if len(row) <= en_idx:
                continue
            result[row[0]] = row[en_idx]  # EN col contains FR text
    return result


def list_text_assets(assets_path):
    """List TextAssets in an assets file via dotnet-deploy."""
    result = subprocess.run(
        [str(DOTNET), "listta", assets_path],
        capture_output=True, text=True, encoding="utf-8"
    )
    assets = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line: continue
        parts = line.split(None, 1)
        if len(parts) != 2: continue
        size, name = parts
        try: int(size)
        except: continue
        assets.append(name)
    return assets


def dump_text_asset(assets_path, name):
    """Dump a TextAsset's m_Script."""
    out_path = Path(f"/tmp/{name}.json")
    subprocess.run(
        [str(DOTNET), "dumpta", assets_path, name, str(out_path)],
        capture_output=True
    )
    if out_path.exists():
        return out_path.read_text(encoding="utf-8", errors="replace")
    return None


def extract_text_loc_pairs(ink_content):
    """Extract (text, loc_n) pairs from Ink JSON.

    Pattern: "^TEXT ","#","^LOC_N","/#" — TEXT followed by LOC tag.
    """
    pairs = []
    # Match `"^TEXT ","#","^LOC_N","/#"` — text then # tags then LOC_N
    # Use a regex that captures text and LOC number, allowing for intermediate tags
    # Simplified: find every "^<text>" followed eventually by "^LOC_<n>"
    pattern = re.compile(r'"\^((?:\\"|[^"])+?)"(?:,"#",[^]]*?)?"\^LOC_(\d+)"')
    for m in pattern.finditer(ink_content):
        text = m.group(1)
        loc = int(m.group(2))
        # Skip technical tags
        if text.startswith(('.', 'FirstLine', 'Jor', 'NoUI', 'PlayMusic', 'Camera', 'PCAnimation', 'StopAmbient', 'GlossaryOff', 'GlossaryOn', 'Cam')):
            continue
        pairs.append((text, loc))
    return pairs


def build_patches(asset_name, ink_content, dialogs):
    """Build list of (find, replace) patches for this asset."""
    pairs = extract_text_loc_pairs(ink_content)
    patches = []
    for text, loc in pairs:
        key = f"{asset_name}_{loc}"
        if key not in dialogs:
            continue
        fr = dialogs[key]
        # Compare: Ink text (unescaped) vs Dialogs FR
        # Ink has \" which represents " in actual text content
        ink_text_unescaped = text.replace('\\"', '"').replace('\\\\', '\\')
        if ink_text_unescaped == fr:
            continue
        if ink_text_unescaped.strip() == fr.strip():
            continue
        # The Ink JSON has the original (escaped) form; the Dialogs has the rendered form
        # To patch: replace ink_text raw with dialogs FR raw, but apply Ink-style escaping to FR
        fr_escaped = fr.replace('\\', '\\\\').replace('"', '\\"')
        # The Ink text in JSON is wrapped in "^TEXT ", so we match including the ^ and trailing space
        # Some Ink texts end with space, some don't. Let's preserve trailing space.
        ink_has_trail_space = text.endswith(' ')
        fr_with_trail = fr_escaped + (' ' if ink_has_trail_space else '')
        patches.append((text, fr_with_trail))
    return patches


def main():
    if len(sys.argv) < 3:
        print("Usage: sync_ink_from_dialogs.py <assets_file> <out_tsv>")
        return 1
    assets_path = sys.argv[1]
    out_tsv = sys.argv[2]

    print(f"Loading Dialogs...", file=sys.stderr)
    dialogs = load_dialogs()
    print(f"  {len(dialogs)} keys loaded", file=sys.stderr)

    print(f"Listing TextAssets in {assets_path}...", file=sys.stderr)
    assets = list_text_assets(assets_path)
    print(f"  {len(assets)} assets found", file=sys.stderr)

    all_patches = []
    for asset in assets:
        # Filter to scene/NPC Inks (skip technical)
        if not re.match(r'^[A-Z]', asset): continue
        if asset in ('SheetInfo', 'GlossaryTerms', 'JournalTexts', 'Popups', 'UIElements',
                    'SpellTexts', 'Dialogs', 'ItemTexts', 'PerformanceTestRunSettings',
                    'Dons', 'LineBreaking Leading Characters', 'PerformanceTestRunInfo',
                    'LineBreaking Following Characters', 'QuestPoints'):
            continue
        content = dump_text_asset(assets_path, asset)
        if not content:
            continue
        patches = build_patches(asset, content, dialogs)
        if patches:
            print(f"  {asset}: {len(patches)} patches", file=sys.stderr)
            for find, repl in patches:
                all_patches.append((asset, find, repl))

    print(f"Total: {len(all_patches)} patches", file=sys.stderr)
    with open(out_tsv, "w", encoding="utf-8", newline="\n") as f:
        for name, find, repl in all_patches:
            if "\t" in find or "\n" in find or "\t" in repl or "\n" in repl:
                continue
            f.write(f"{name}\t{find}\t{repl}\n")
    print(f"Wrote {out_tsv}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main() or 0)
