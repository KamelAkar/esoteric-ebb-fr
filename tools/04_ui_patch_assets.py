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
PATCHES = [
    (b'Helmets', 'Casques'),     # 11 → 11 ✓ (4+7+1 == 4+7+1)
    (b'Behold', 'Examiner'),     # 12 → 12 ✓ (4+6+2 == 4+8+0)
    (b'Trifle', 'Piquer'),       # 12 → 12 ✓ (4+6+2 == 4+6+2)
    (b'Examine', 'Examiner'),    # 12 → 12 ✓ (4+7+1 == 4+8+0)
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
