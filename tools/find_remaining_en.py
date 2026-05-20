"""Find any remaining English strings in Dialogs CSV using broader heuristics."""
import sys
import csv
import re

sys.stdout.reconfigure(encoding="utf-8")

# Re-dump latest Dialogs from live game
import subprocess
# Already dumped to /tmp earlier, fallback to backups
import os
DIALOGS = r"C:/Users/Ravnow/AppData/Local/Temp/Dialogs_v2.json"
if not os.path.exists(DIALOGS):
    DIALOGS = "backups/Dialogs.json"

# Comprehensive English word list (function words + common content words)
EN_WORDS = set("""
a an the and or but if then else when where why how what who which while because since
i you he she it we they me him her us them my your his their our its
am is are was were be been being have has had having do does did doing
can could would should will shall may might must
not no yes okay ok sure fine
this that these those there here
on in at to of for with by from about into onto upon under over above below
go come went came going coming get got give gave take took make made
say said tell told ask asked know knew think thought see saw look looked
want need feel felt try tried hear heard help helped find found
back forward up down out away
just only really very too also even still already yet
all any some many much more most less few several
something nothing anything everything
people person man woman boy girl thing place time day night
good bad great okay big small new old young
maybe perhaps never always sometimes often soon later
god gods damn fuck shit hell crap fucking
yeah yep nope huh wait stop hey hi hello bye
oh ah um uh well now then so therefore
through after before during between among
quest cleric guard hero shop tea wizard rogue barbarian
""".lower().split())

# French characters
FR_CHARS = set("éèêàçùôîûïëÉÈÊÀÇÔÎÛÏ«»œŒ")
FR_WORDS = set("""
le la les un une des de du et ou mais si donc car car ni or
je tu il elle on nous vous ils elles me te se moi toi
mon ma mes ton ta tes son sa ses notre votre leur
être avoir faire dire aller voir savoir vouloir venir
suis es est sommes êtes sont étais était étaient
ne pas plus jamais rien
ici là où quand comment pourquoi
oui non peut peut-être
""".lower().split())


def classify(text):
    """Return ('fr', 'en', 'mixed', 'other')."""
    if not text or not text.strip():
        return "empty"
    # Strip tags
    stripped = re.sub(r"<[^>]+>", "", text)
    # Find words (alphabetic only)
    words = re.findall(r"[A-Za-zÀ-ÿœŒ']+", stripped.lower())
    if not words:
        return "other"

    has_fr_char = any(c in FR_CHARS for c in text)
    en_count = sum(1 for w in words if w in EN_WORDS)
    fr_count = sum(1 for w in words if w in FR_WORDS)

    if has_fr_char and en_count >= 2:
        return "mixed"
    if has_fr_char or fr_count >= 1:
        return "fr"
    if en_count >= 1:
        return "en"
    return "other"


# Process Dialogs
with open(DIALOGS, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    en_idx = header.index("EN")

    counts = {"fr": 0, "en": 0, "mixed": 0, "other": 0, "empty": 0}
    en_examples = []
    mixed_examples = []
    for row in reader:
        if len(row) <= en_idx:
            continue
        text = row[en_idx]
        cls = classify(text)
        counts[cls] += 1
        if cls == "en" and len(en_examples) < 100:
            en_examples.append((row[0], text))
        if cls == "mixed" and len(mixed_examples) < 50:
            mixed_examples.append((row[0], text))

print("Classification:")
for k, v in counts.items():
    print(f"  {k}: {v}")
print()
print(f"=== EN-only examples (first 100 of {counts['en']}) ===")
for key, text in en_examples:
    print(f"{key}\t{text}")
print()
print(f"=== Mixed examples (first 50 of {counts['mixed']}) ===")
for key, text in mixed_examples:
    print(f"{key}\t{text}")
