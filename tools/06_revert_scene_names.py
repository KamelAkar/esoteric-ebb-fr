"""HOTFIX: revert Unity scene-NAME strings in level files back to English.

The previous translator translated ALL build-settings scene names (Goblin Garden,
Lower Lair, etc.) to French inside the level files. Scene-LOAD references use these
exact strings to call SceneManager.LoadScene(name); with French names the engine
fails with "Scene not found".

Level files are slot-preserving (same byte size vanilla vs patched), so we do a
POSITIONAL revert: for every length-prefixed scene-name string in the VANILLA file,
copy its exact slot bytes (4-byte length + content + padding) into the patched file
at the same offset. This restores scene names to English while preserving every
other translation (factions, item names, action verbs, dialogue).

Usage: python tools/06_revert_scene_names.py <vanilla_dir> <patched_dir> <out_dir>
"""
import sys
import os
import struct

sys.stdout.reconfigure(encoding="utf-8")

SCENE_NAMES = [
    "MainMenu", "DebugArea", "Lower Lair", "Visken's Lair", "Tolstad",
    "Darrow's Nest", "Guard Tower", "Rollermill", "Tea Shop", "Secret Tunnel",
    "Temple of Urth", "Drunk Sphinx", "Goblin Garden", "Guild Warehouse",
    "Pillar Crossing", "Simii's Hole", "Snell's Pad", "Snurre's Office",
    "Askanii-Reeds", "Waterlane View", "City Below", "Lisa's Place",
    "Old Prison", "Undercoast Path", "Jor's Crossroad",
]


def slot_size(content_len):
    # Unity length-prefixed string: 4-byte length + content, padded to 4-byte boundary
    return 4 + ((content_len + 3) & ~3)


def revert_file(van_path, pat_path, out_path):
    van = van_path.read_bytes() if hasattr(van_path, "read_bytes") else open(van_path, "rb").read()
    pat = bytearray(open(pat_path, "rb").read())
    if len(van) != len(pat):
        print(f"  SKIP {os.path.basename(pat_path)}: size mismatch {len(van)} vs {len(pat)}")
        return 0
    reverts = 0
    for name in SCENE_NAMES:
        sb = name.encode("utf-8")
        prefix = struct.pack("<I", len(sb))
        needle = prefix + sb  # length-prefixed occurrence in vanilla
        ss = slot_size(len(sb))
        pos = 0
        while True:
            i = van.find(needle, pos)
            if i < 0:
                break
            # i points at the length prefix. Copy the whole vanilla slot to patched.
            van_slot = van[i:i + ss]
            if bytes(pat[i:i + ss]) != van_slot:
                pat[i:i + ss] = van_slot
                reverts += 1
            pos = i + 1
    open(out_path, "wb").write(pat)
    return reverts


def main():
    van_dir, pat_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for i in range(0, 25):
        vf = os.path.join(van_dir, f"level{i}")
        pf = os.path.join(pat_dir, f"level{i}")
        of = os.path.join(out_dir, f"level{i}")
        if not (os.path.exists(vf) and os.path.exists(pf)):
            continue
        n = revert_file(vf, pf, of)
        total += n
        print(f"level{i}: {n} scene-name slots reverted to English")
    print(f"\nTotal scene-name slots reverted: {total}")


if __name__ == "__main__":
    main()
