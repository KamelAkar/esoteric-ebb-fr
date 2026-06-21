"""Translate character-creation UI labels in level0 (slot-preserving).

Only short labels that fit the original Unity slot are translated. The long lore
paragraphs cannot be translated this way (they would need re-serialization, which
corrupts the level file — see the v1.3.4 crash). They stay English.
"""
import struct
import shutil
from pathlib import Path

STEAM = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data")
BACKUP_DIR = Path(__file__).resolve().parent.parent / "assets_backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# (english, french) — french UTF-8 bytes must fit english slot = (4+len+3)&~3 - 4
PATCHES = [
    ("Strength", "Force"),          # 8 max8
    ("Dexterity", "Dextérité"),     # 9 max12 ; 11
    ("Wisdom", "Sagesse"),          # 6 max8 ; 7
    ("Charisma", "Charisme"),       # 8 max8
    # Constitution / Intelligence identical in FR -> skip
    ("Proficient", "Maîtrisé"),     # 10 max12 ; 9
    ("Proficiencies", "Compétences"),  # 13 max16 ; 12
    ("Randomize", "Au hasard"),     # 9 max12 ; 9
    ("Return", "Retour"),           # 6 max8
    ("RETURN", "RETOUR"),           # 6 max8
    ("Pre-Built", "Prédéfini"),     # 9 max12 ; 10
    ("Background Focus", "Historique"),  # 16 max16 ; 10
]


def slot(L):
    return (4 + L + 3) & ~3


def patch_file(path):
    data = bytearray(path.read_bytes())
    changes = 0
    for eng, fr in PATCHES:
        eb = eng.encode("utf-8")
        fb = fr.encode("utf-8")
        es = slot(len(eb))
        if 4 + len(fb) > es:
            print(f"  [SKIP] {eng!r}->{fr!r}: too long")
            continue
        needle = struct.pack("<I", len(eb)) + eb
        pos = 0
        while True:
            i = data.find(needle, pos)
            if i < 0:
                break
            ns = bytearray(es)
            struct.pack_into("<I", ns, 0, len(fb))
            ns[4:4 + len(fb)] = fb
            data[i:i + es] = ns
            changes += 1
            pos = i + es
    if changes:
        bak = BACKUP_DIR / (path.name + ".pre-cc")
        if not bak.exists():
            shutil.copy(path, bak)
        path.write_bytes(data)
    return changes


def main():
    total = 0
    for i in range(0, 25):
        p = STEAM / f"level{i}"
        if not p.exists():
            continue
        n = patch_file(p)
        total += n
        if n:
            print(f"level{i}: {n} char-creation labels translated")
    print(f"\nTotal char-creation labels translated: {total}")


if __name__ == "__main__":
    main()
