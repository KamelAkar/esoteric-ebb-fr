"""Find all backslash-escaped quoted strings in Ink JSON: \"text\"."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

content = open(sys.argv[1], encoding="utf-8").read()

# Look for \"...\" sequences (raw bytes: backslash quote text backslash quote)
pattern = re.compile(r'\\"([^\\]+(?:\\.[^\\]*)*?)\\"')
seen = set()
for m in pattern.finditer(content):
    s = m.group(1)
    if s in seen or len(s) < 3:
        continue
    seen.add(s)
    print(repr(s))
