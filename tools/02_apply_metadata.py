"""Apply French translations to global-metadata.dat IL2CPP string literals.

Strategy: in-place byte replacement.
- If French_utf8 <= English_bytes: write French + pad with null, update length
- Else: print warning, skip (need shorter French)

Backup: writes to OUTPUT path, original untouched.
"""
import struct
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

SRC = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat")
OUT = Path(r"C:\Users\Ravnow\Documents\esoteric-ebb-fr\metadata_strings\global-metadata.dat.patched")
BAK = Path(r"C:\Users\Ravnow\Documents\esoteric-ebb-fr\metadata_strings\global-metadata.dat.backup")

# Substring patches: within specific string literal entries, replace ENG_SUB with FR_SUB
# Length constraint: FR_SUB UTF-8 bytes ≤ ENG_SUB bytes (else need full repointing)
SUBSTRING_PATCHES = [
    # Format: (string_index, english_substring, french_substring)
    # Both as bytes. FR may be shorter than ENG; we update length accordingly.

    # ---- DC results (Succès / Échec embedded in rich text format strings) ----
    (1837, b'Success', 'Succès'.encode('utf-8')),
    (1838, b'Success', 'Succès'.encode('utf-8')),
    (1839, b'Success', 'Succès'.encode('utf-8')),
    (5762, b'Success', 'Succès'.encode('utf-8')),
    (20110, b'Success', 'Succès'.encode('utf-8')),
    (1833, b'Failure', 'Échec'.encode('utf-8')),
    (1834, b'Failure', 'Échec'.encode('utf-8')),

    # ---- DC → DD inside format strings ----
    (5762, b'DC: Succ', b'DD: Succ'),       # nested in [DC: Success]
    (13664, b'DC ', b'DD '),                # [{0}  | DC {1}] {2}
    (20110, b'DC {1}', b'DD {1}'),          # {0} ...DC {1}: Success...

    # ---- xp! suffix ----
    (19991, b'xp!', b'XP'),                 # "xp!" → "XP" (shorter, cleaner)
]

# Whole-entry patches for date/quest formats — full English match required
DATE_PATCHES = [
    # idx, english_full, french_replacement (must be ≤ original UTF-8 bytes)
    (1736, '1st Day, ', 'Jour 1, '),
    (1792, '2nd Day, ', 'Jour 2, '),
    (1803, '3rd Day, ', 'Jour 3, '),
    (12792, 'Updated on ', 'Maj le '),
    (17910, 'nd, 27 PE', ' an 27 EP'),
    (18432, 'rd, 27 PE', ' an 27 EP'),
    (19259, 'th, 27 PE', ' an 27 EP'),
    # Months
    (8026, 'March', 'mars'),
    (8027, 'March ', 'mars '),
    (2790, 'April', 'avril'),
    (2974, 'August', 'août'),
    (4816, 'December', 'décembr'),
    (5868, 'February', 'février'),
    (7489, 'January', 'janvier'),
    (7506, 'July', 'juil'),
    (7508, 'June', 'juin'),
    (8078, 'May', 'mai'),

    # ---- Faction / party / role names (quest tracker labels) ----
    (5796, 'FREESTRIDER', 'ERRANT'),
    (6047, 'Freestrider', 'Errant'),
    (2456, 'APOLITICAL', 'APOLITIQUE'),
    (2780, 'Apolitical', 'Apolitique'),
    (3017, 'BEEFY CLERIC', 'CLERC COSTO'),

    # ---- HUD / menu labels (RISKY — Day/Level/Cleric break save template substitution) ----
    # Retiré : (4737, 'Day', ...), (4738, 'Day ', ...), (4739, 'Day 1', ...),
    #         (7734, 'Level ', ...), (4072, 'Cleric', ...)
    # Ces strings sont probablement utilisées comme clés de template par le moteur de save.

    # ---- Safe menu strings ----
    (9512, 'Quit to menu?', 'Retour menu ?'),

    # ---- DC prefix (THE missing piece — used standalone before DC value) ----
    (4536, 'DC ', 'DD '),
    (16155, 'dc ', 'dd '),

    # ---- HP suffix (damage/heal display "+1 HP" / "-1 HP") ----
    (233, ' HP', ' PV'),

    # ---- Save list format ----
    (4530, 'DAY {0} at {1}_{2}', 'JOUR {0}, {1}_{2}'),

    # ---- Stats display labels (REPOINT handles oversize) ----
    (10651, 'Strength', 'Force'),
    (4927, 'Dexterity', 'Dextérité'),  # 11 bytes > 9 — REPOINTED
    (4003, 'Charisma', 'Charisme'),
    (13174, 'Wisdom', 'Sagesse'),       # 7 bytes > 6 — REPOINTED
    # Constitution / Intelligence same length — no patch needed

    # ---- Inventory tab + slot labels ----
    (6424, 'Helms', 'Casques'),  # NOT in .assets — pure metadata literal — likely safe
    (13527, '[Empty Feat Slot]', '[Don vide]'),
    # (3925, 'Cantrip', 'Tour de magie'),  # breaks spellbook count — keep removed

    # ---- Notification suffix ("' Added.") ----
    (752, '\' Added.', '\' reçu.'),

    # ---- BROKEN: these patches break variable substitution / inventory loading ----
    # Used internally as binding keys. DO NOT PATCH.
    # (2633, 'All Items', ...), (5986, 'Food', ...), (7260, 'Inventory', ...),
    # (7540, 'Key Items', ...), (9500, 'Questing', ...), (11034, 'Texts', ...),
    # (13125, 'Weaponry', ...), (4098, 'Collected Spells', ...), (9344, 'Prepared Spells', ...),
    # (10499, 'Spells', ...), (4956, 'Difficulty Class', ...)

    # ---- Speaker label (idx 13338/13324 might be binding keys — REMOVED) ----
    # (13338, 'You', 'Toi'),
    # (13324, 'YOU', 'TOI'),

    # ---- Quit menu (RISKY — might be button name binding) ----
    # (9511, 'Quit', 'Quitter'),

    # ---- Session intro (Continue screen) — long Ink-style strings, safe ----
    (13375, 'You didn\'t make it far last time. That\'s my bad.',
            'T\'es pas allé loin avant. C\'est ma faute.'),
    (248, ' Ready for another round?\\n\\nIf you want a tip: prepare spells at the shrine, then heal yourself. And eat some apples. That should get you through the <i>lichhouse gauntlet</i>.',
          ' Prêt pour un autre round ?\\n\\nConseil : prépare des sorts à l\'autel, puis soigne-toi. Et mange des pommes. Tu passeras le <i>gantelet du lichhouse</i>.'),
]

# Translation table: (string_index, original_english, french)
# Will be validated against the actual dump for safety.
PATCHES = [
    # ---- Safe long format strings (clearly UI) ----
    (1926, '</b>.\\nGained experience: ', '</b>.\\nXP gagnée : '),
    (6136, 'Gained experience: +', 'XP gagnée : +'),
    (10501, 'Spend 1 Hit Die on a 1 hour short rest?', 'Dépenser 1 DV pour repos court 1h ?'),
    (3250, 'Burn an incense to regain a 1st level spellslot? You have ', 'Brûler un encens pour récupérer un slot lvl 1 ? Vous avez '),
    (9678, 'Reinvigorated: Regain 1 use of a spent Hit Dice.', 'Revigoré : Récupère 1 usage de DV dépensé.'),
    (9816, 'Resurgent: Regain 2 uses of spent Hit Dice.', 'Renaissant : Récupère 2 usages de DV dépensés.'),
    (8983, 'Out of Hit Dice.', 'Plus de Dés de Vie.'),
    (1737, '1st level Spellslots +', 'Slots de sort niv 1 +'),
    (1793, '2nd level Spellslots +', 'Slots de sort niv 2 +'),
    (1804, '3rd level Spellslots +', 'Slots de sort niv 3 +'),
    (10500, 'Spells to Prepare: ', 'Sorts à prép. : '),
    (6501, 'Hit Dice +1', 'Dés de Vie +1'),

    # ---- Inventory/UI count formats ----
    (221, ' Cantrips\\n', ' Tours\\n'),
    (255, ' Spells', ' Sorts'),

    # ---- Categorical labels (testing — single-word strings are riskier as they may be used as keys) ----
    (10701, 'Success', 'Succès'),
    (5850, 'Failure', 'Échec'),

    # ---- Full descriptions (longer format strings, safe) ----
    (65, '\\nSpend 1 hour to recover. Gain (1d8) HP, remove 1 level of exhaustion, and restore 1 spell slot. After resting, all dice checks are unlocked.',
         '\\nProfite d\'1h pour récupérer. Gagne (1d8) PV, retire 1 niv. d\'épuisement, restaure 1 sort. Les jets se débloquent.'),
    (10502, 'Spend 1 hour to recover. Gain (1d8) HP, remove 1 level of exhaustion, and restore 1 spell slot.',
            '1h pour récup. Gagne (1d8) PV, retire 1 niv. d\'épuisement, restaure 1 sort.'),
    (10503, 'Spend 1 hour to recover. Gain (1d8) HP, remove 1 level of exhaustion, and restore 1 spell slot. After resting, all dice checks are unlocked.',
            'Profite d\'1h pour récupérer. Gagne (1d8) PV, retire 1 niv. d\'épuisement, restaure 1 sort. Les jets se débloquent.'),

    # ---- Previously oversized — now FULL FRENCH via repoint ----
    (9816, 'Resurgent: Regain 2 uses of spent Hit Dice.', 'Renaissant : Récupère 2 usages de Dés de Vie.'),
    (8983, 'Out of Hit Dice.', 'Plus de Dés de Vie.'),
    (6501, 'Hit Dice +1', 'Dés de Vie +1'),

    # ---- Other dynamic UI ----
    (375, ' healing. You lose a level of exhaustion.', ' soin. Niveau d\'épuisement +1.'),
    (5317, 'Energized: Get rid of 1 level of Exhaustion.', 'Énergisé : -1 niv. d\'épuisement.'),
]


def parse_header(data):
    sanity, version = struct.unpack('<II', data[:8])
    assert sanity == 0xFAB11BAF
    sLitOff, sLitSize = struct.unpack('<ii', data[8:16])
    sLitDataOff, sLitDataSize = struct.unpack('<ii', data[16:24])
    return version, sLitOff, sLitSize, sLitDataOff, sLitDataSize


def get_string(data, sLitOff, sLitDataOff, idx):
    entry = sLitOff + idx * 8
    length, di = struct.unpack('<II', data[entry:entry+8])
    return length, di, data[sLitDataOff + di : sLitDataOff + di + length]


def decode_escaped(s):
    """Decode \\n / \\t from the input strings."""
    return s.encode().decode('unicode_escape').encode('latin-1').decode('utf-8', errors='replace')


def patch_strings_section(raw, version, sOff, sSize):
    """Patch enum names / reflection strings in the 'strings' section.
    Each string is null-terminated. We can replace in-place if new_bytes + \\0 fits in old slot.
    """
    section = raw[sOff:sOff+sSize]
    # (find_bytes, replace_with_str_no_null) — find must include null terminator
    patches = [
        (b'Success\0', 'Succès'),
        (b'Failure\0', 'Échec'),
        # Stats — likely safe (enum values stored as int in save, not string)
        (b'Strength\0', 'Force'),
        (b'Dexterity\0', 'Dextérit'),  # 9 bytes UTF-8 fits in 10 slot
        (b'Wisdom\0', 'Sage'),
        (b'Charisma\0', 'Charisme'),  # 8 bytes fits exact in 9 slot
        # Day/Level/Cleric retired — broke save preview earlier
    ]
    for needle, replacement in patches:
        new_bytes = replacement.encode('utf-8') + b'\0'
        if len(new_bytes) > len(needle):
            print(f"[STRSEC SKIP] {needle!r} → {replacement!r} ({len(new_bytes)} > {len(needle)})")
            continue
        # Find at boundaries (preceded by \0 or section start)
        pos = 0
        count = 0
        while True:
            i = section.find(needle, pos)
            if i < 0: break
            if i == 0 or section[i-1] == 0:
                # Patch in raw
                abs_off = sOff + i
                for j in range(len(needle)):
                    raw[abs_off + j] = new_bytes[j] if j < len(new_bytes) else 0
                count += 1
                print(f"[STRSEC OK] {needle!r:20s} → {replacement!r} at file 0x{abs_off:X}")
            pos = i + 1
        if count == 0:
            print(f"[STRSEC MISS] {needle!r} not found at boundaries")


HEADER_SIZE = 0x100
N_SECTIONS = (HEADER_SIZE - 8) // 8  # 31 sections


def apply_patch_with_repoint(raw, sLitOff, sLitDataOff, sLitDataSize, appended, idx, eng_bytes, fr_bytes, label=''):
    """Apply patch in-place if fits, else append to repoint buffer.
    Returns (changed_inplace_or_repointed_bool, was_repointed_bool)."""
    entry_off = sLitOff + idx * 8
    old_len, old_di = struct.unpack('<II', raw[entry_off:entry_off+8])
    abs_off = sLitDataOff + old_di
    current = bytes(raw[abs_off:abs_off+old_len])
    if current != eng_bytes:
        print(f"[{label} SKIP] idx={idx}: expected {eng_bytes!r}, got {current!r}")
        return False, False

    if len(fr_bytes) <= old_len:
        # In-place
        for i in range(old_len):
            raw[abs_off + i] = fr_bytes[i] if i < len(fr_bytes) else 0
        struct.pack_into('<I', raw, entry_off, len(fr_bytes))
        print(f"[{label} INPLACE] idx={idx}: {eng_bytes!r} → {fr_bytes!r} ({old_len}→{len(fr_bytes)})")
        return True, False

    # Repoint: append to end of data section, update entry
    new_di = sLitDataSize + len(appended)
    appended.extend(fr_bytes)
    struct.pack_into('<II', raw, entry_off, len(fr_bytes), new_di)
    print(f"[{label} REPOINT] idx={idx}: {eng_bytes!r} → {fr_bytes!r} ({old_len}→{len(fr_bytes)}) @ +0x{new_di:X}")
    return True, True


def main():
    # Read from backup if it exists (idempotent re-runs)
    src = BAK if BAK.exists() else SRC
    if not BAK.exists():
        shutil.copy(SRC, BAK)
        print(f"Backed up original to {BAK}")
    print(f"Reading source: {src}")
    raw = bytearray(open(src, 'rb').read())

    # Parse FULL header (31 sections)
    sanity, version = struct.unpack('<II', raw[:8])
    assert sanity == 0xFAB11BAF
    sections = []
    for i in range(N_SECTIONS):
        hdr_off = 8 + i * 8
        f_off, sz = struct.unpack('<ii', raw[hdr_off:hdr_off+8])
        sections.append([hdr_off, f_off, sz])

    sLitOff = sections[0][1]; sLitSize = sections[0][2]
    sLitDataOff = sections[1][1]; sLitDataSize_orig = sections[1][2]
    sOff = sections[2][1]; sSize = sections[2][2]
    print(f"Metadata v{version}")
    print(f"stringLiteral table: 0x{sLitOff:X} ({sLitSize//8} entries)")
    print(f"stringLiteralData:   0x{sLitDataOff:X} (size 0x{sLitDataSize_orig:X})")
    print(f"strings section:     0x{sOff:X} (size 0x{sSize:X})")
    print()

    # ---- STRSEC patches (in-place only — section format doesn't support repoint trivially) ----
    patch_strings_section(raw, version, sOff, sSize)
    print()

    appended = bytearray()  # bytes to append to end of stringLiteralData

    # ---- DATE_PATCHES (full replacement, with repoint if oversize) ----
    for idx, eng_template, fr_template in DATE_PATCHES:
        eng_bytes = decode_escaped(eng_template).encode('utf-8')
        fr_bytes = decode_escaped(fr_template).encode('utf-8')
        apply_patch_with_repoint(raw, sLitOff, sLitDataOff, sLitDataSize_orig, appended, idx, eng_bytes, fr_bytes, label='DATE')
    print()

    # ---- SUBSTRING_PATCHES (find sub-bytes in entry, replace; full new content via repoint if needed) ----
    for idx, eng_sub, fr_sub in SUBSTRING_PATCHES:
        entry = sLitOff + idx * 8
        length, di = struct.unpack('<II', raw[entry:entry+8])
        abs_off = sLitDataOff + di
        current = bytes(raw[abs_off:abs_off+length])
        if eng_sub not in current:
            print(f"[SUB SKIP] idx={idx}: {eng_sub!r} not in {current!r}")
            continue
        new_content = current.replace(eng_sub, fr_sub)
        # Treat as full replacement (in-place or repoint)
        apply_patch_with_repoint(raw, sLitOff, sLitDataOff, sLitDataSize_orig, appended, idx, current, new_content, label='SUB')
    print()

    # ---- PATCHES (full replacement, with repoint if oversize) ----
    for idx, eng_template, fr_template in PATCHES:
        eng_bytes = decode_escaped(eng_template).encode('utf-8')
        fr_bytes = decode_escaped(fr_template).encode('utf-8')
        apply_patch_with_repoint(raw, sLitOff, sLitDataOff, sLitDataSize_orig, appended, idx, eng_bytes, fr_bytes, label='MAIN')
    print()

    # ---- Final assembly: shift subsequent sections if we appended anything ----
    if appended:
        # Pad to 4-byte alignment so subsequent sections keep their alignment
        while len(appended) % 4 != 0:
            appended.append(0)
        insert_at = sLitDataOff + sLitDataSize_orig
        new_raw = bytearray(raw[:insert_at]) + appended + bytearray(raw[insert_at:])
        # Update stringLiteralData size
        sections[1][2] = sLitDataSize_orig + len(appended)
        # Shift all subsequent sections (index 2+) by len(appended)
        delta = len(appended)
        for i in range(2, N_SECTIONS):
            if sections[i][1] >= insert_at:
                sections[i][1] += delta
        # Write header
        for hdr_off, f_off, sz in sections:
            struct.pack_into('<ii', new_raw, hdr_off, f_off, sz)
        raw = new_raw
        print(f"Repointed: +{delta} bytes appended (4-aligned), {N_SECTIONS-2} subsequent sections shifted")

    OUT.write_bytes(raw)
    print(f"\nSaved to {OUT}")


if __name__ == '__main__':
    main()
