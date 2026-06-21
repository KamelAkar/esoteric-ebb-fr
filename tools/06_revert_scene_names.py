"""Revert ONLY the Unity scene-NAME strings (FR -> EN) in the previously-translated
level files, keeping every other translation (menu, char creation, stats, items,
factions, dialogue) intact.

The previous translator re-serialized the level files to translate EVERYTHING
(which works fine for display/GameObject names) but ALSO translated the build-
settings scene names used by SceneManager.LoadScene(). French scene names don't
exist in build settings -> "scene not found". This reverts just those names.

Slot-preserving: replace the length-prefixed French name with the English name
(new length + content + null pad) inside the SAME 4-byte-aligned slot, so file
size and all internal offsets are unchanged.

Usage: python tools/06_revert_scene_names.py <fr_levels_dir> <out_dir>
"""
import sys
import os
import struct

sys.stdout.reconfigure(encoding="utf-8")

# French scene name -> English build-settings name (verified 1:1 by occurrence count).
# Lower Lair / Visken's Lair / Tolstad / Rollermill / Askanii-Reeds / Waterlane View
# were NOT translated (kept English) -> no entry needed.
FR_TO_EN = {
    "Jardin Gobelin": "Goblin Garden",
    "Sphinx Ivre": "Drunk Sphinx",
    "Entrepôt de la Guilde": "Guild Warehouse",
    "Nid de Darrow": "Darrow's Nest",
    "Tour de Garde": "Guard Tower",
    "Bureau de Snurre": "Snurre's Office",
    "Trou de Simii": "Simii's Hole",
    "Salon de Thé": "Tea Shop",
    "Tunnel Secret": "Secret Tunnel",
    "Temple d'Urth": "Temple of Urth",
    "Croisée du Pilier": "Pillar Crossing",
    "Cité d'En Bas": "City Below",
    "Vieille Prison": "Old Prison",
    "Croisée de Jor": "Jor's Crossroad",
    "Chez Lisa": "Lisa's Place",
    "Logis de Snell": "Snell's Pad",
    "Chemin de la Côte d'En Bas": "Undercoast Path",
}


def slot_size(content_len):
    return (4 + content_len + 3) & ~3


def revert_file(path, out_path):
    data = bytearray(open(path, "rb").read())
    reverts = 0
    for fr, en in FR_TO_EN.items():
        fr_b = fr.encode("utf-8")
        en_b = en.encode("utf-8")
        fr_slot = slot_size(len(fr_b))
        if 4 + len(en_b) > fr_slot:
            print(f"  [SKIP] {fr!r}->{en!r}: EN too long for slot ({4+len(en_b)} > {fr_slot})")
            continue
        needle = struct.pack("<I", len(fr_b)) + fr_b
        pos = 0
        while True:
            i = data.find(needle, pos)
            if i < 0:
                break
            new_slot = bytearray(fr_slot)
            struct.pack_into("<I", new_slot, 0, len(en_b))
            new_slot[4:4 + len(en_b)] = en_b
            data[i:i + fr_slot] = new_slot
            reverts += 1
            pos = i + fr_slot
    open(out_path, "wb").write(data)
    return reverts


def main():
    fr_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for i in range(0, 25):
        fp = os.path.join(fr_dir, f"level{i}")
        op = os.path.join(out_dir, f"level{i}")
        if not os.path.exists(fp):
            continue
        n = revert_file(fp, op)
        total += n
        print(f"level{i}: {n} scene-name occurrences reverted FR->EN")
    print(f"\nTotal scene-name occurrences reverted: {total}")


if __name__ == "__main__":
    main()
