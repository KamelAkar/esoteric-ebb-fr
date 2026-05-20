"""Generate dotnet-deploy textasset patches from dialogs_fr.tsv.

Reads dialogs_fr.tsv (key/en/fr columns), finds each row in Dialogs.json
(the CSV TextAsset), and generates substring replacements.

Strategy: for each key, locate its row in Dialogs.json and replace the
entire row content. This avoids CSV escaping ambiguity.
"""
import sys
import csv
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent

# Load translations
translations = {}
with open(REPO / "translations" / "dialogs_fr.tsv", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    header = next(reader)
    for row in reader:
        if len(row) < 3:
            continue
        key, en, fr = row[0], row[1], row[2]
        translations[key] = (en, fr)

print(f"Loaded {len(translations)} translations", file=sys.stderr)

# Load Dialogs.json content
dialogs_path = REPO / "backups" / "Dialogs.json"
content = dialogs_path.read_text(encoding="utf-8")
lines = content.split("\n")

# Build line index: key -> raw line
key_to_line = {}
for line in lines:
    # Find first comma to extract key (assumes key has no comma)
    if not line or line.startswith("Key,"):
        continue
    comma_idx = line.find(",")
    if comma_idx == -1:
        continue
    key = line[:comma_idx]
    key_to_line[key] = line

print(f"Found {len(key_to_line)} keys in Dialogs.json", file=sys.stderr)

# Generate patches
patches = []
not_found = []
already_translated = []

for key, (en, fr) in translations.items():
    if key not in key_to_line:
        not_found.append(key)
        continue
    old_line = key_to_line[key]
    # Build new line: replace EN column with FR text
    # Format: key,speaker,area,type,EN,...  (EN is the 5th field)
    # Use csv.writer to properly escape FR text
    import io
    fields = next(csv.reader([old_line]))
    if len(fields) < 5:
        not_found.append(key)
        continue
    # Check current EN cell
    current_en = fields[4]
    if current_en == fr:
        already_translated.append(key)
        continue
    fields[4] = fr
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="")
    writer.writerow(fields)
    new_line = buf.getvalue()

    patches.append(("Dialogs", old_line, new_line))

print(f"Generated {len(patches)} patches", file=sys.stderr)
print(f"Not found: {len(not_found)}", file=sys.stderr)
print(f"Already translated (skipped): {len(already_translated)}", file=sys.stderr)
if not_found:
    print(f"Sample not found: {not_found[:5]}", file=sys.stderr)

# Write patches TSV
out_path = REPO / "translations" / "dialogs_patches.tsv"
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    for name, old, new in patches:
        # Make sure no tabs/newlines in old/new
        if "\t" in old or "\n" in old or "\t" in new or "\n" in new:
            print(f"WARN: special chars in patch for {old[:50]}", file=sys.stderr)
            continue
        f.write(f"{name}\t{old}\t{new}\n")

print(f"Wrote {out_path}", file=sys.stderr)
