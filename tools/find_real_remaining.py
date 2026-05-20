"""Find strings that are actually still in English (not false positives)."""
import sys
import csv
import re

sys.stdout.reconfigure(encoding="utf-8")

# Strict English detection: 3+ uppercase-or-multichar English-only words
STRONG_EN_WORDS = set("""
the and you your have has had this that with for are was were been being
will would could should can may might must shall don't won't isn't
i'm i've i'll you're you've you'll we're they're it's
look looked see saw know knew think thought want need feel felt
go went come came get got give gave take took make made
not yes okay sure fine
something nothing anything everything
people person thing place time
good bad great big small new old young here there what when where why how
just only really very even still already yet
fucking shit damn fuck hell crap
all any some many much more most less
boy girl man woman cleric hero shop tea wizard rogue
""".lower().split())

FR_CHARS = set("éèêàçùôîûïëÉÈÊÀÇÔÎÛÏ«»œŒ")

DIALOGS = r"C:/Users/Ravnow/AppData/Local/Temp/Dialogs_v2.json"

def is_likely_english(text):
    """Strict EN classifier - text dominated by English content."""
    stripped = re.sub(r"<[^>]+>", "", text)
    stripped = re.sub(r"\([^)]*\)", "", stripped)  # remove (action descriptors which may already be FR)
    words = re.findall(r"[A-Za-zÀ-ÿœŒ'-]+", stripped.lower())
    if not words:
        return False
    if any(c in FR_CHARS for c in text):
        # Has French chars - probably partially translated; only flag if >= 3 strong EN words
        en_count = sum(1 for w in words if w in STRONG_EN_WORDS)
        return en_count >= 3
    else:
        # No French chars - might be pure EN
        en_count = sum(1 for w in words if w in STRONG_EN_WORDS)
        return en_count >= 1


with open(DIALOGS, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    en_idx = header.index("EN")

    matches = []
    for row in reader:
        if len(row) <= en_idx:
            continue
        text = row[en_idx]
        if not text or len(text) < 5:
            continue
        if is_likely_english(text):
            matches.append((row[0], row[3], text))

print(f"# {len(matches)} likely-EN strings to translate", file=sys.stderr)
for key, type_, text in matches:
    print(f"{key}\t{type_}\t{text}")
