"""Revert item-name translations in asset DATA (FR -> EN), slot-preserving.

Bug: the game stores item names as KEYS (currency counting, icon lookup, save
serialization). Translating "Crowns"->"Écus" etc. in the data breaks the economy
(crowns vanish, can't be spent, purchase text struck through) and item icons
(empty slots), while NOT even translating the visible name. So we revert them all
to English keys. Item display stays English but WORKS.

Dialogue text (Ink JSON) keeps its French "écus"/"couronnes" — those are inside
larger length-prefixed strings, never matched by the standalone item-name pattern.
"""
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

GAME_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data")

# (english, french) — same list that 04_ui_patch applied; we reverse it.
ITEM_NAMES = [
    ("Garden Apple", "Pomme Jardin"),
    ("Crowns", "Écus"),
    ("Boots", "Bottes"),
    ("Cloak", "Manteau"),
    ("Bottle", "Fiole"),
    ("Dagger", "Dague"),
    ("Bag of Holding", "Sac sans Fond"),
    ("Bracers of Thievery", "Brassards de Voleur"),
    ("Belt of Dwarvenkind", "Ceinture des Nains"),
    ("Bronze Shield", "Bouclier Bronze"),
    ("Ancient Tome", "Tome Ancien"),
    ("Broken Sword", "Lame Brisée"),
    ("Bottle of Milk", "Fiole de Lait"),
    ("Amulet of Annihilation", "Amulette d'Annihilation"),
    ("Empty Efreeti Bottle", "Fiole d'Efrit Vide"),
    ("Filled Efreeti Bottle", "Fiole d'Efrit Remplie"),
    ("Adamantine Warhammer", "Marteau Adamantin"),
    ("Crusader's Mantle", "Manteau du Croisé"),
]


def slot_size(n):
    return (4 + n + 3) & ~3


def revert_file(path):
    data = bytearray(path.read_bytes())
    changes = 0
    for eng, fr in ITEM_NAMES:
        eb = eng.encode("utf-8")
        fb = fr.encode("utf-8")
        if slot_size(len(eb)) != slot_size(len(fb)):
            continue
        slot = slot_size(len(fb))
        needle = struct.pack("<I", len(fb)) + fb  # current (French) length-prefixed
        pos = 0
        while True:
            i = data.find(needle, pos)
            if i < 0:
                break
            ns = bytearray(slot)
            struct.pack_into("<I", ns, 0, len(eb))
            ns[4:4 + len(eb)] = eb
            data[i:i + slot] = ns
            changes += 1
            pos = i + slot
    if changes:
        path.write_bytes(data)
        print(f"  {path.name}: {changes} item names reverted FR->EN")
    return changes


def main():
    targets = (
        ["resources.assets", "globalgamemanagers.assets"]
        + [f"sharedassets{i}.assets" for i in range(30)]
        + [f"level{i}" for i in range(30)]
    )
    total = 0
    for fname in targets:
        p = GAME_DATA / fname
        if p.exists():
            total += revert_file(p)
    print(f"\nTotal item names reverted: {total}")


if __name__ == "__main__":
    main()
