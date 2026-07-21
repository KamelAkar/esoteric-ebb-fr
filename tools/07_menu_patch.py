"""Translate main-menu / pause-menu UI strings in level files (slot-preserving).

These UI strings live in the level files (level0 = main menu, level1..24 = pause
menu overlay). We translate them with the SAME slot-preserving byte mechanism as
04_ui_patch (keep Unity's 4-byte-aligned slot, write new length + FR + null pad).

CRITICAL: never touch scene names (build-settings names) — only menu UI strings.
A few 4-byte strings (Quit, Exit, Save) have no French that fits a 4-byte slot and
stay English; translating them would require re-serializing the level file, which
shifts internal pointers and breaks scene loading (the bug fixed in v1.3.4).
"""
import struct
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STEAM = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data")
BACKUP_DIR = REPO_ROOT / "assets_backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# (english, french) — french UTF-8 bytes must fit the english slot (= (4+len+3)&~3 - 4)
PATCHES = [
    ("Continue", "Reprise"),       # 8 -> max8 ; Reprise=7
    ("New Game", "Nouveau"),       # 8 -> max8 ; 7
    ("Load Game", "Charger"),      # 9 -> max12 ; 7
    ("Settings", "Options"),       # 8 -> max8 ; 7
    ("Credits", "Crédits"),        # 7 -> max8 ; 8 (é=2)
    # ("Resume", "Reprise"),   # NE PAS — peut servir de clé/action         # 6 -> max8 ; 7
    # ("Controls", "Touches"), # NE PAS — clé de binding potentielle       # 8 -> max8 ; 7
    ("Fullscreen", "Plein écran"), # 10 -> max12 ; 12
    ("Resolution", "Résolution"),  # 10 -> max12 ; 11
    ("Language", "Langue"),        # 8 -> max8 ; 6
    ("Video", "Vidéo"),            # 5 -> max8 ; 6
    # ("Cancel", "Annuler"),   # NE PAS — nom d'action input (casse la manette)         # 6 -> max8 ; 7
    ("Save Game", "Sauvegarder"),  # 9 -> max12 ; 11
    ("Delete", "Effacer"),         # 6 -> max8 ; 7
    ("Yes", "Oui"),                # 3 -> max4 ; 3
    ("No", "Non"),                 # 2 -> max4 ; 3
    # NOT translatable in-place (4-byte slot, no FR fits): Quit, Exit, Save, Audio(keep), Options(same)
]


def slot_size(content_len):
    return (4 + content_len + 3) & ~3


def patch_file(path):
    data = bytearray(path.read_bytes())
    changes = 0
    for eng, fr in PATCHES:
        eng_b = eng.encode("utf-8")
        fr_b = fr.encode("utf-8")
        eng_slot = slot_size(len(eng_b))
        if 4 + len(fr_b) > eng_slot:
            print(f"  [SKIP] {eng!r}->{fr!r}: FR too long for slot")
            continue
        needle = struct.pack("<I", len(eng_b)) + eng_b
        pos = 0
        while True:
            i = data.find(needle, pos)
            if i < 0:
                break
            # overwrite slot: new length + FR bytes + null pad to fill slot
            new_slot = bytearray(eng_slot)
            struct.pack_into("<I", new_slot, 0, len(fr_b))
            new_slot[4:4 + len(fr_b)] = fr_b
            data[i:i + eng_slot] = new_slot
            changes += 1
            pos = i + eng_slot
    if changes:
        bak = BACKUP_DIR / (path.name + ".pre-menu")
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
            print(f"level{i}: {n} menu strings translated")
    print(f"\nTotal menu strings translated: {total}")


if __name__ == "__main__":
    main()
