"""Extract untranslated and partially-translated rows from Dialogs CSV."""
import sys
import csv
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("backups/Dialogs.json", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    en_idx = header.index("EN")

    untranslated = []
    mixed = []

    en_words = re.compile(r"\b(the|and|you|your|have|this|that|with|for|are|don't|I'm|won't|isn't|goin|going|would|could|should|will|just|like|over|here|there|what|when|where|something|nothing|anything|every|never|always)\b", re.IGNORECASE)
    french_chars = set("éèêàçùôîûïëÉÈÊÀÇÔÎÛÏ«»")

    for row in reader:
        if len(row) <= en_idx:
            continue
        en_text = row[en_idx]
        if not en_text.strip():
            continue

        has_fr = any(c in en_text for c in french_chars)
        has_en = bool(en_words.search(en_text))

        if has_fr and has_en:
            mixed.append((row[0], row[1], row[2], row[3], en_text))
        elif has_en and not has_fr:
            untranslated.append((row[0], row[1], row[2], row[3], en_text))

print(f"# MIXED FR/EN ({len(mixed)} rows) ===")
for key, speaker, area, type_, text in mixed:
    print(f"{key}\t{speaker}\t{area}\t{type_}\t{text}")
print()
print(f"# UNTRANSLATED EN ({len(untranslated)} rows) ===")
for key, speaker, area, type_, text in untranslated:
    print(f"{key}\t{speaker}\t{area}\t{type_}\t{text}")
