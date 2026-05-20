"""Compute strings in JSON that aren't yet in the TSVs."""
import re
import sys
import ast

sys.stdout.reconfigure(encoding="utf-8")

json_file = sys.argv[1]
tsv_files = sys.argv[2:]

content = open(json_file, encoding="utf-8").read()
pattern = re.compile(r'\\"([^\\]+(?:\\.[^\\]*)*?)\\"')
all_quoted = set()
for m in pattern.finditer(content):
    s = m.group(1)
    if len(s) >= 3:
        all_quoted.add(s)

existing = set()
for tsv in tsv_files:
    for line in open(tsv, encoding="utf-8"):
        parts = line.rstrip("\r\n").split("\t")
        if len(parts) == 3:
            f = parts[1]
            existing.add(f)
            # Also try stripped of \" surroundings
            if f.startswith('\\"') and f.endswith('\\"'):
                existing.add(f[2:-2])

missing = [s for s in all_quoted if s not in existing]
print(f"All quoted strings: {len(all_quoted)}")
print(f"Existing entries:   {len(existing)}")
print(f"Missing:            {len(missing)}")
print()
for s in sorted(missing):
    print(repr(s))
