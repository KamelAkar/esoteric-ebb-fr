"""Patch faction/party display names in .assets files.

Strategy: scan .assets files for length-prefixed strings (Unity TextAsset/MonoBehaviour format)
containing faction names, and replace them with French equivalents.

Length-prefixed strings in Unity .assets:
- 4-byte little-endian length prefix
- Then UTF-8 string bytes
- Then padding to 4-byte boundary
"""
import struct
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data")
BACKUP_DIR = Path(r"C:\Users\Ravnow\Documents\esoteric-ebb-fr\assets_backups")
BACKUP_DIR.mkdir(exist_ok=True)

# Faction display name translations
# Format: (english_bytes, french_bytes) — french MUST be ≤ english in byte length
FACTION_PATCHES = [
    (b'Freestrider', 'Errant'.encode('utf-8')),
    (b'FREESTRIDER', 'ERRANT'.encode('utf-8')),
    (b'Apolitical', 'Apolitique'[:10].encode('utf-8')),  # 10=10
    (b'APOLITICAL', 'APOLITIQUE'[:10].encode('utf-8')),
]


def patch_file(path):
    """Replace length-prefixed faction names in this file."""
    data = bytearray(path.read_bytes())
    changes = 0

    for eng, fr in FACTION_PATCHES:
        eng_len = len(eng)
        # Build the length-prefixed pattern: [4-byte LE length][eng bytes]
        length_prefix = struct.pack('<I', eng_len)
        pattern = length_prefix + eng

        pos = 0
        while True:
            i = data.find(pattern, pos)
            if i < 0:
                break
            # IMPORTANT: keep length prefix UNCHANGED (Unity pads to 4-byte boundary).
            # Just overwrite the string bytes with French + null padding.
            for j in range(eng_len):
                data[i + 4 + j] = fr[j] if j < len(fr) else 0
            changes += 1
            pos = i + 4 + eng_len

    if changes > 0:
        # Backup
        bak = BACKUP_DIR / path.name
        if not bak.exists():
            shutil.copy(path, bak)
        path.write_bytes(data)
        print(f"  {path.name}: {changes} replacements")
    return changes


def main():
    target_files = (
        ['resources.assets']
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
