"""Repoint strings in the IL2CPP 'strings' section (type/enum names).

For names that don't fit in-place: append new string at end of strings section,
update all u32 references to the old relative offset → new relative offset,
extend stringSize, shift subsequent sections.
"""
import struct
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

SRC_LIVE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat")
SRC = Path(__file__).resolve().parent.parent / "metadata_strings" / "global-metadata.dat.patched"  # read POST metadata_apply.py
OUT = SRC_LIVE  # write directly to game

# Hardcoded relative offsets within strings section (from original backup dump).
# These are stable across in-place patches (in-place doesn't shift content).
KNOWN_OFFSETS = {
    'Wisdom':    0xA6483,
    'Dexterity': 0xA645F,
    'Behold':    0xA9C07,
    'Trifle':    0xA9C21,
    'Inventory': 0xABAA8,
}

HEADER_SIZE = 0x100
N_SECTIONS = (HEADER_SIZE - 8) // 8


# Strings to repoint in 'strings' section.
STRSEC_REPOINTS = [
    ('Wisdom', 'Sagesse'),
    ('Dexterity', 'Dextérité'),
    ('Behold', 'Examiner'),
    ('Trifle', 'Chaparder'),
    # ('Inventory', 'Inventaire'),  # BREAKS inventory UI — class/method name in stringSize
]


def find_strsec_string(strsec_data, needle):
    """Find a null-terminated string in the section. Returns relative offset."""
    pos = 0
    while True:
        i = strsec_data.find(needle, pos)
        if i < 0: return -1
        # Must be at start (preceded by \0 or section start)
        if i == 0 or strsec_data[i-1] == 0:
            return i
        pos = i + 1


def parse_sections(data):
    sanity, version = struct.unpack('<II', data[:8])
    assert sanity == 0xFAB11BAF
    sections = []
    for i in range(N_SECTIONS):
        hdr_off = 8 + i * 8
        f_off, sz = struct.unpack('<ii', data[hdr_off:hdr_off+8])
        sections.append([hdr_off, f_off, sz])
    return version, sections


def main():
    raw = bytearray(SRC.read_bytes())
    version, sections = parse_sections(raw)
    sOff = sections[2][1]
    sSize = sections[2][2]
    print(f"strings section: 0x{sOff:X} (size 0x{sSize:X})")

    appended = bytearray()  # new strings to add at end of section
    repoints = []  # (old_rel_offset, new_rel_offset, label)

    for name, replacement in STRSEC_REPOINTS:
        old_rel = KNOWN_OFFSETS.get(name)
        if old_rel is None:
            print(f"[SKIP] {name}: no known offset")
            continue
        new_bytes = replacement.encode('utf-8') + b'\0'
        new_rel = sSize + len(appended)  # offset within EXTENDED section
        appended.extend(new_bytes)
        repoints.append((old_rel, new_rel, replacement))
        print(f"[PLAN] {name} @ 0x{old_rel:X} → '{replacement}' @ 0x{new_rel:X}")

    if not repoints:
        print("Nothing to do.")
        return

    # Count u32 references to verify safety
    for old_rel, new_rel, label in repoints:
        old_le = struct.pack('<i', old_rel)
        hits = []
        pos = 0
        while True:
            i = raw.find(old_le, pos)
            if i < 0: break
            hits.append(i)
            pos = i + 1
        # Filter: only 4-byte aligned hits (typical for struct fields)
        aligned = [h for h in hits if h % 4 == 0]
        print(f"  '{label}': {len(hits)} total u32 occurrences, {len(aligned)} 4-byte aligned")

    # Step 1: write new strings into appended buffer
    # Step 2: replace u32 references (only at 4-byte aligned positions, to reduce false positives)
    n_replacements = 0
    for old_rel, new_rel, label in repoints:
        old_le = struct.pack('<i', old_rel)
        new_le = struct.pack('<i', new_rel)
        # Scan whole file, replace at aligned positions
        pos = 0
        while True:
            i = raw.find(old_le, pos)
            if i < 0: break
            if i % 4 == 0:
                raw[i:i+4] = new_le
                n_replacements += 1
            pos = i + 1
    print(f"  Replaced {n_replacements} u32 references")

    # Step 3: insert appended bytes at end of strings section
    insert_at = sOff + sSize
    new_raw = bytearray(raw[:insert_at]) + appended + bytearray(raw[insert_at:])

    # Step 4: update section sizes and offsets
    sections[2][2] = sSize + len(appended)
    delta = len(appended)
    for i in range(3, N_SECTIONS):
        if sections[i][1] >= insert_at:
            sections[i][1] += delta
    for hdr_off, f_off, sz in sections:
        struct.pack_into('<ii', new_raw, hdr_off, f_off, sz)

    print(f"\nFile size: {len(raw):,} → {len(new_raw):,} (+{delta})")
    OUT.write_bytes(new_raw)
    print(f"Saved to {OUT}")


if __name__ == '__main__':
    main()
