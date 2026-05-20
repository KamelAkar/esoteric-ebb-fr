"""Extract DC/ROLL-prefixed choice strings from Ink JSON."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

content = open(sys.argv[1], encoding='utf-8').read()

# Match "^...DC...stuff...end" — handle escape with negative lookbehind on backslash
# Simpler approach: match "^...string..." where ... can be anything except an unescaped "
pattern = re.compile(r'"\^((?:\\"|[^"])*)"')
all_matches = pattern.findall(content)

dc = [m for m in all_matches if re.match(r'^(DC|ROLL)\d+ ', m)]
print(f"Total ^-strings: {len(all_matches)}")
print(f"DC/ROLL choices: {len(dc)}")
print()
for d in sorted(set(dc)):
    print(repr(d))
