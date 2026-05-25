"""Fix Ink JSON entries where ROLL/DC/FC prefix was stripped by sync.

For each affected entry, generate a patch that RESTORES the prefix.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent

# For each sharedassets index, parse its ink_sync TSV, identify stripped-prefix entries,
# and generate a "restore prefix" patch
# Préfixes de choix Ink :
#   ROLL<n> <stat>-    jet à dés (Wisdom, etc.)
#   DC<n> <stat>-      check à DC (skill check)
#   FC<n> <stat>-      check à FC (free check)
#   IROLL-             initiative de combat (PAS de nombre)
#   SPELL <name>-      lancer un sort
PREFIX_RE = re.compile(r'^((?:ROLL|DC|FC)\d+(?:\s+\w+)?-|IROLL-|SPELL\s+\w+-)')

per_file_patches = defaultdict(list)

for i in [0, 1, 2, 3, 4, 11, 12, 13, 14, 22, 23, 24]:
    sync_tsv = REPO / "translations" / f"ink_sync_{i}.tsv"
    if not sync_tsv.exists():
        continue
    fixes = []
    for line in sync_tsv.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        name, find_orig, repl_was = parts
        m = PREFIX_RE.match(find_orig)
        if not m:
            continue
        # Check if repl lost the prefix
        if PREFIX_RE.match(repl_was):
            continue
        prefix = m.group(1)
        # The current state of Ink has repl_was (without prefix)
        # We want to put the prefix back, so:
        # find = repl_was (current state)
        # new_repl = prefix + repl_was
        # Skip if repl_was contains prefix already (shouldn't happen)
        fixes.append((name, repl_was, prefix + repl_was))
    if fixes:
        per_file_patches[i] = fixes
        print(f"sharedassets{i}: {len(fixes)} prefix restorations", file=sys.stderr)

for i, fixes in per_file_patches.items():
    out_tsv = REPO / "translations" / f"ink_restore_prefix_{i}.tsv"
    with open(out_tsv, "w", encoding="utf-8", newline="\n") as f:
        for name, find, repl in fixes:
            if "\t" in find or "\n" in find or "\t" in repl or "\n" in repl:
                continue
            f.write(f"{name}\t{find}\t{repl}\n")
    print(f"Wrote {out_tsv}: {len(fixes)} entries", file=sys.stderr)

total = sum(len(v) for v in per_file_patches.values())
print(f"Total prefix restorations: {total}", file=sys.stderr)
