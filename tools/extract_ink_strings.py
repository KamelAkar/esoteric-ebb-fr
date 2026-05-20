"""Extract translatable text strings from an Ink JSON TextAsset, handling escapes."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

JSON_FILE = sys.argv[1]
EXISTING_TSV = sys.argv[2] if len(sys.argv) > 2 else None

content = open(JSON_FILE, encoding="utf-8").read()

# Match "^<text>" where text can contain escaped quotes (\") and other escapes
pattern = re.compile(r'"\^((?:[^"\\]|\\.)+)"')
matches = pattern.findall(content)

skip_patterns = re.compile(
    r"^(LOC_\d+|DC\d+|FC\d+|\.[A-Z]|XPGain|Minor|Major|wis|int|dex|str|cha|con|reply|"
    r"FirstLine|Jor|NoUI|PCAnimation|CameraAnimation|StopAmbient|GlossaryOff|GlossaryOn|"
    r"PlayMusic|music_|Cam)"
)

texts = []
seen = set()
for m in matches:
    s = m.strip()
    if not s or len(s) < 4:
        continue
    if not (" " in s or "." in s or "!" in s or "?" in s):
        continue
    if skip_patterns.match(s):
        continue
    if s in seen:
        continue
    seen.add(s)
    texts.append(s)

existing_en = set()
if EXISTING_TSV and Path(EXISTING_TSV).exists():
    for line in open(EXISTING_TSV, encoding="utf-8"):
        parts = line.rstrip("\r\n").split("\t")
        if len(parts) == 3:
            existing_en.add(parts[1])

missing = [t for t in texts if t not in existing_en]
print(f"Total extracted: {len(texts)}")
print(f"Already translated: {len(existing_en)}")
print(f"Missing from translation: {len(missing)}")
print()
for i, t in enumerate(missing, 1):
    # Show with escapes unescaped for readability
    display = t.replace('\\"', '"').replace("\\\\", "\\")
    print(f"{i:3d}. {display!r}")
