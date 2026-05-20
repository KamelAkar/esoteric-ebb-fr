"""Patch UI labels in level files via length-prefixed string replacement.

Unity .assets format for strings:
  [4-byte LE length][N bytes content][padding to next 4-byte boundary]

We can replace strings where TOTAL slot size (4 + N + pad) is UNCHANGED.
"""
import struct
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data")
BACKUP_DIR = REPO_ROOT / "assets_backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def slot_size(content_len):
    """Total bytes for a length-prefixed string slot, padded to 4 bytes."""
    raw = 4 + content_len
    return (raw + 3) & ~3  # round up to multiple of 4


# (english_bytes, french_string) — french encoded as UTF-8
# REQUIREMENT: slot_size(len_eng) == slot_size(len_fr_utf8)
# NOTE: Helmets/Behold/Trifle/Examine standalone NOT found length-prefixed
# in any asset (verified 2026-05-19) — they appear as prefixes of GameObject
# names (BeholdOpen, BeholdClosed etc.) and ARE patched via metadata instead
# (see tools/02_apply_metadata.py). Kept for reference but no-op here.
PATCHES = [
    (b'Garden Apple', 'Pomme Jardin'),  # 16 → 16 ✓ (4+12+0 == 4+12+0) item display name
    (b'Crowns', 'Écus'),                # 12 → 12 ✓ currency name

    # ---- Items courants (batch conservateur 2026-05-20, slot-aligned) ----
    (b'Boots', 'Bottes'),                       # 12 → 12 ✓
    (b'Cloak', 'Manteau'),                      # 12 → 12 ✓
    (b'Bottle', 'Fiole'),                       # 12 → 12 ✓
    (b'Dagger', 'Dague'),                       # 12 → 12 ✓
    (b'Bag of Holding', 'Sac sans Fond'),       # 20 → 20 ✓
    (b'Bracers of Thievery', 'Brassards de Voleur'),  # 24 → 24 ✓
    (b'Belt of Dwarvenkind', 'Ceinture des Nains'), # 24 → 24 ✓
    (b'Bronze Shield', 'Bouclier Bronze'),      # 20 → 20 ✓
    (b'Ancient Tome', 'Tome Ancien'),           # 16 → 16 ✓
    (b'Broken Sword', 'Lame Brisée'),           # 16 → 16 ✓ (é=2B)
    (b'Bottle of Milk', 'Fiole de Lait'),       # 20 → 20 ✓
    (b'Amulet of Annihilation', "Amulette d'Annihilation"),  # 28 → 28 ✓
    (b'Empty Efreeti Bottle', "Fiole d'Efrit Vide"),   # 24 → 24 ✓
    (b'Filled Efreeti Bottle', "Fiole d'Efrit Remplie"), # 28 → 28 ✓
    (b'Adamantine Warhammer', 'Marteau Adamantin'),    # 24 → 24 ✓
    (b'Crusader\'s Mantle', 'Manteau du Croisé'),       # 24 → 24 ✓

    # ---- Sorts: TESTÉS et CASSANT le compteur Sorts Préparés/Tours/Sorts ----
    # (b'Cure Wounds', 'Soin Plaies'),    # casse X placeholder dans Grimoire
    # (b'Mage Hand', 'Main du Mage'),     # idem
]


def patch_file(path):
    data = bytearray(path.read_bytes())
    changes = 0

    for eng, fr_str in PATCHES:
        fr = fr_str.encode('utf-8')
        eng_slot = slot_size(len(eng))
        fr_slot = slot_size(len(fr))
        if eng_slot != fr_slot:
            print(f"  [ALIGN] {eng!r}: slot mismatch ({eng_slot} vs {fr_slot}) — skip")
            continue

        # Search for [length=len(eng)][eng bytes]
        pattern = struct.pack('<I', len(eng)) + eng
        pos = 0
        while True:
            i = data.find(pattern, pos)
            if i < 0:
                break
            # Write new length + new content + null pad to fill slot
            new_len_field = struct.pack('<I', len(fr))
            new_slot = bytearray(eng_slot)
            new_slot[0:4] = new_len_field
            new_slot[4:4+len(fr)] = fr
            # bytes 4+len(fr)..end remain zero (null pad)
            data[i:i+eng_slot] = bytes(new_slot)
            changes += 1
            pos = i + eng_slot

    if changes > 0:
        bak = BACKUP_DIR / path.name
        if not bak.exists():
            shutil.copy(path, bak)
        path.write_bytes(data)
        print(f"  {path.name}: {changes} replacements")
    return changes


def main():
    target_files = (
        ['resources.assets', 'globalgamemanagers.assets']
        + [f'sharedassets{i}.assets' for i in range(0, 30)]
        + [f'level{i}' for i in range(0, 30)]
    )
    total = 0
    for fname in target_files:
        path = GAME_DATA / fname
        if not path.exists():
            continue
        n = patch_file(path)
        total += n
    print(f"\nTotal replacements: {total}")


if __name__ == '__main__':
    main()
