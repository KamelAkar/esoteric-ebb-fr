"""Extract all DC/FC/ROLL-prefixed choice strings from Ink JSON."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

content = open(sys.argv[1], encoding='utf-8').read()

pattern = re.compile(r'"\^((?:\\"|[^"])*)"')
all_matches = pattern.findall(content)

choices = [m for m in all_matches if re.match(r'^(DC|FC|ROLL)\d+ [a-z]+-', m)]

print(f"Total ^-strings: {len(all_matches)}")
print(f"Skill-check choices: {len(choices)}")
print()
for c in sorted(set(choices)):
    print(c)
