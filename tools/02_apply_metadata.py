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

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat")
OUT = REPO_ROOT / "metadata_strings" / "global-metadata.dat.patched"
BAK = REPO_ROOT / "metadata_strings" / "global-metadata.dat.backup"
OUT.parent.mkdir(parents=True, exist_ok=True)

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
    (2974, 'August', 'août'),  # 5<6 in-place (â=2B) — mot complet
    (4816, 'December', 'décembre'),  # 9>8 REPOINT — corrige le 'e' coupé
    (5868, 'February', 'février'),
    (7489, 'January', 'janvier'),
    (7506, 'July', 'juillet'),  # 7>4 REPOINT — mot complet
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
    # NOTE: previous (6424, 'Helms', 'Casques') was the WRONG index — actual displayed
    # label is at idx 6423 ('Helmets'). Validated visually 2026-05-19.
    (6423, 'Helmets', 'Casques'),       # 7=7 in-place
    (12134, 'Trinkets', 'Babioles'),    # 8=8 in-place
    (4234, 'Consumables', 'Consommables'),  # 12>11 REPOINT — mot complet (avant: 'Consomm.')
    (7794, 'Literature', 'Livres'),     # 10>6 in-place shorter
    (4074, 'Clericals', 'Cléricaux'),   # 9<10 REPOINT (+1 byte)
    (13527, '[Empty Feat Slot]', '[Don vide]'),
    (13632, '[This glossary is empty.]', '[Ce glossaire est vide.]'),  # 25>24 in-place
    # (4502, 'Cure Wounds', 'Soins'),  # no-op visually — title comes from another source
    # (3925, 'Cantrip', 'Tour de magie'),  # breaks spellbook count — keep removed

    # ---- Action verbs (interaction icons: dialog, eye, hand on world objects) ----
    # Validated visually 2026-05-19 on temple stone interactable.
    (3018, 'BEHOLD', 'VOIR'),           # 6>4 in-place
    (3110, 'Behold', 'Voir'),           # 6>4 in-place
    (5498, 'Examine', 'Examiner'),      # 7<8 REPOINT
    (10914, 'TRIFLE', 'PIQUER'),        # 6=6 in-place
    (12129, 'Trifle', 'Piquer'),        # 6=6 in-place
    (5318, 'Engage', 'Parler'),         # 6=6 in-place (speech bubble action)
    (7853, 'Look', 'Voir'),             # 4=4 in-place
    (8948, 'Open', 'Ouvrir'),           # 4<6 REPOINT
    (9592, 'Read', 'Lire'),             # 4=4 in-place
    (161, ' (Leave.)', ' (Partir.)'),   # 9<10 REPOINT — suffix des options de dialogue
    (7667, 'Leave', 'Partir'),          # 5<6 REPOINT — verbe d'action standalone

    # ---- UI verbs (Back/Cancel/Cast/Hide/Next/No/Push/Throw) ----
    # Patchés 2026-05-19, smoke test passé (jeu charge save sans crash).
    (3045, 'Back', 'Retour'),           # 4<6 REPOINT
    (3540, 'Cancel', 'Annuler'),        # 6<7 REPOINT
    (3955, 'Cast', 'Lancer'),           # 4<6 REPOINT — lancer sort
    (6469, 'Hide', 'Cacher'),           # 4<6 REPOINT
    (8492, 'Next', 'Suivant'),          # 4<7 REPOINT
    (8500, 'No', 'Non'),                # 2<3 REPOINT
    (9463, 'Push', 'Pousser'),          # 4<7 REPOINT — pousser objet
    (11967, 'Throw', 'Lancer'),         # 5<6 REPOINT — lancer combat

    # ---- Inventory tabs initially marked "broken" by previous Claude — RETESTED 2026-05-19 ----
    # Le commentaire historique disait que ces patches cassent l'inventaire.
    # Test cette session : FAUX. Inventaire navigue normalement, tous slots accessibles.
    # (Peut-être que previous Claude testait sur un mauvais idx ou mal observé.)
    (2633, 'All Items', 'Tout'),        # 9>4 in-place
    (13125, 'Weaponry', 'Armement'),    # 8=8 in-place
    (7540, 'Key Items', 'Clés'),        # 9>5 in-place (Clé=4 chars + s)
    (5986, 'Food', 'Vivres'),           # 4<6 REPOINT
    (11034, 'Texts', 'Textes'),         # 5<6 REPOINT
    (9500, 'Questing', 'Quêtes'),       # 8>7 (ê=2B) in-place
    (4956, 'Difficulty Class', 'Difficulté de Sort'),  # 16<19 REPOINT (validé 2026-05-20 — tooltip Grimoire)
    (4098, 'Collected Spells', 'Sorts Collectés'),     # 16=16 in-place (validé idem)
    (9344, 'Prepared Spells', 'Sorts Préparés'),       # 15<16 REPOINT (validé idem)
    (2240, '<i>one single time</i>', '<i>une unique fois</i>'),  # 22=22 in-place — résout le bug Quest_34
    # (4535, 'DC', 'DD'),  # DISABLED 2026-05-20 — patcher littéral "DC" → "DD" casse le stripping du préfixe DC dans choices Ink

    # ---- Time of day + action verbs (smoke test passé 2026-05-19) ----
    (5178, 'EVENING', 'SOIR'),          # 7>4 in-place
    (7942, 'MORNING', 'MATIN'),         # 7>5 in-place
    (8363, 'NIGHT', 'NUIT'),            # 5>4 in-place
    (2441, 'AFTERNOON', 'TANTÔT'),      # 9>7 (Ô=2B) in-place
    (2473, 'ASSASSINATIONS', 'ASSASSINATS'),  # 14>11 in-place
    # (9551, 'ROLL', 'JET'),  # DISABLED 2026-05-20 — même bug que DC→DD : casse le stripping du préfixe ROLL dans choices Ink
    (7497, 'Journal Updated', 'Journal mis à jour'),  # repoint 15<18 (notif HUD)

    # ---- Factions politiques manquantes (Agrarian/Arcanist/Azgalist) ----
    # Symétrie avec FREESTRIDER→ERRANT, APOLITICAL→APOLITIQUE déjà patchés.
    (2442, 'AGRARIAN', 'AGRARIEN'),     # 8=8 in-place
    (2464, 'ARCANIST', 'ARCANISTE'),    # 8<9 repoint
    (2491, 'AZGALIST', 'AZGALISTE'),    # 8<9 repoint
    (2811, 'Arcanist', 'Arcaniste'),    # 8<9 repoint
    (3006, 'Azgalist', 'Azgaliste'),    # 8<9 repoint
    (12051, 'Touch', 'Toucher'),        # 5<7 repoint — verbe d'action

    # ---- Day format (HUD bas-droit + save preview) ----
    # DISTINCTION CRITIQUE: idx 4737 'Day' standalone casse save preview (Clerc XX/DebugArea).
    # Idx 4738 'Day ' (avec espace) + idx 4739 'Day 1' (spécifique) SONT safe.
    (4738, 'Day ', 'Jour '),            # 4<5 repoint — format "Day N" -> "Jour N"
    (4739, 'Day 1', 'Jour 1'),          # 5<6 repoint — préview save day 1 spécifique

    # ---- Level format (similaire à Day, idx 7734 'Level ' safe) ----
    (7734, 'Level ', 'Niveau '),        # 6<7 repoint — HUD "Lv X Cleric"

    # ---- Dialogues narrateur Cleric ----
    (13586, '[Lone Cleric] ', '[Seul Clerc] '),
    (13630, '[The Cleric] ', '[Le Clerc] '),
    (13631, '[The Cleric] Rolled ', '[Le Clerc] Lance '),
    (2238, '<i>Morning</i>, Cleric.', '<i>Matin</i>, Clerc.'),
    (2788, 'Appreciate it, Cleric.', 'Merci, Clerc.'),
    (7533, 'Keep that up, Cleric!', 'Continue, Clerc !'),
    (11053, 'Thank you, Cleric.', 'Merci, Clerc.'),

    # ---- Tooltips Grimoire (3 hovers : Sorts Collectés/Préparés/Difficulté Sort) ----
    (11268,
     'The amount of spells in your spellbook. You can gain more by collecting and memorizing spell scrolls.',
     'Le nombre de sorts en votre grimoire. Acquérez-en plus en collectant et mémorisant des parchemins.'),
    (11269,
     'The amount of spells you currently have prepared. You can prepare spells by visiting a shrine at any time.\n\n The amount you can prepare is: 2 + your class level + your intelligence modifier.',
     "Le nombre de sorts actuellement préparés. Vous pouvez préparer vos sorts à un autel à tout moment.\n\n Le nombre maximum : 2 + niveau de classe + modificateur d'Intelligence."),
    (11902,
     'This is the DC a target has to achieve when rolling a save against one of your spells. \n\n The DC is: 8 + your wisdom or intelligence modifier (whichever is highest) + your proficiency bonus.',
     "C'est le DD qu'une cible doit atteindre pour résister à un de vos sorts. \n\n Le DD est : 8 + votre modificateur de Sagesse ou Intelligence (le plus haut) + votre bonus de maîtrise."),

    # ---- Popups bourse (Stockage Profond) ----
    (419, ' items found at the bottom of the pouch!', ' objets trouvés au fond de la bourse !'),
    (8905, 'One item found at the bottom of the pouch!', 'Un objet trouvé au fond de la bourse !'),
    (12213, 'Turn pouch inside out? This will empty all stored items into your inventory.',
            'Vider la bourse ? Tous les objets stockés iront dans votre inventaire.'),

    # ---- CONFIRMÉS CASSER LE JEU (à NE PAS patcher en metadata) ----
    # (7260, 'Inventory', 'Inventaire') — slots inventaire disparaissent (binding key)
    # (10499, 'Spells', 'Sorts') — Grimoire affiche "X SORTS" au lieu du compte
    # NOTE: Collected/Prepared Spells RE-TESTÉS 2026-05-20 isolément = OK !
    # Le faux positif venait probablement du patch Spells (idx 10499) ou Inventory
    # (idx 7260) dans la même batch test. Repointed avec FR complète maintenant.

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
    (10500, 'Spells to Prepare: ', 'Sorts à préparer : '),  # REPOINT — mot complet (avant: 'prép.')
    (6501, 'Hit Dice +1', 'Dés de Vie +1'),

    # ---- Inventory/UI count formats ----
    (221, ' Cantrips\\n', ' Tours\\n'),
    (255, ' Spells', ' Sorts'),

    # ---- Categorical labels (testing — single-word strings are riskier as they may be used as keys) ----
    (10701, 'Success', 'Succès'),
    (5850, 'Failure', 'Échec'),

    # ---- Full descriptions (longer format strings, safe) ----
    (65, '\\nSpend 1 hour to recover. Gain (1d8) HP, remove 1 level of exhaustion, and restore 1 spell slot. After resting, all dice checks are unlocked.',
         '\\nProfite d\'1h pour récupérer. Gagne (1d8) PV, retire 1 niveau d\'épuisement, restaure 1 emplacement de sort. Les jets se débloquent.'),
    (10502, 'Spend 1 hour to recover. Gain (1d8) HP, remove 1 level of exhaustion, and restore 1 spell slot.',
            'Passe 1h à récupérer. Gagne (1d8) PV, retire 1 niveau d\'épuisement, restaure 1 emplacement de sort.'),
    (10503, 'Spend 1 hour to recover. Gain (1d8) HP, remove 1 level of exhaustion, and restore 1 spell slot. After resting, all dice checks are unlocked.',
            'Profite d\'1h pour récupérer. Gagne (1d8) PV, retire 1 niveau d\'épuisement, restaure 1 emplacement de sort. Les jets se débloquent.'),

    # ---- Previously oversized — now FULL FRENCH via repoint ----
    (9816, 'Resurgent: Regain 2 uses of spent Hit Dice.', 'Renaissant : Récupère 2 usages de Dés de Vie.'),
    (8983, 'Out of Hit Dice.', 'Plus de Dés de Vie.'),
    (6501, 'Hit Dice +1', 'Dés de Vie +1'),

    # ---- Other dynamic UI ----
    (375, ' healing. You lose a level of exhaustion.', ' soin. Niveau d\'épuisement +1.'),
    (5317, 'Energized: Get rid of 1 level of Exhaustion.', 'Énergisé : -1 niv. d\'épuisement.'),

    # ---- Notes de session (load game recap, par Chris le dev) — REPOINT (FR plus long) ----
    (48, "\\n\\nOh, and remember: there's still that heavy table to be flipped inside the tea shop. Bring Snell, he should be able to help.",
         "\\n\\nOh, et n'oublie pas : il reste cette lourde table à renverser dans le salon de thé. Emmène Snell, il devrait pouvoir aider."),
    (112, " \\n\\nAnd then there's that masked assassin. You have NO CLUE who has it out for you.",
          " \\n\\nEt puis il y a cet assassin masqué. Tu n'as AUCUNE IDÉE de qui en a après toi."),
    (116, " \\n\\nBut you're still in Visken's Lair. I mean- the lichhouse. I mean- the local mortuary. So, uh, go outside!",
          " \\n\\nMais tu es toujours dans le Repaire de Visken. Enfin — la lichhouse. Enfin — la morgue locale. Alors, euh, sors !"),
    (210, " And finally, you've descended straight into the City Below. Esoteric hallways full of traps. Secrets around every corner. Monsters <i>crawling</i> up from the depths.\\n\\nSomehow, you just know: someone or <i>something</i> is trying to keep you from discovering the truth. You need to keep looking. Search every corner. Talk with every person. Look into the political bullshit above and the esoteric madness below. Eventually you'll find a way forward...",
          " Et enfin, tu es descendu droit dans la Cité Inférieure. Des couloirs ésotériques pleins de pièges. Des secrets à chaque coin. Des monstres <i>rampant</i> depuis les profondeurs.\\n\\nD'une manière ou d'une autre, tu le sais : quelqu'un ou <i>quelque chose</i> tente de te cacher la vérité. Tu dois continuer à chercher. Fouille chaque recoin. Parle à chaque personne. Penche-toi sur les conneries politiques d'en haut et la folie ésotérique d'en bas. Tu finiras par trouver un chemin..."),
    (211, " And finally, you've descended straight into the City Below. Esoteric hallways full of traps. Secrets around every corner. Monsters <i>crawling</i> up from the depths.\\n\\nSomeone or <i>something</i> is trying to keep you from discovering the truth. And now you've found it: a secret passage, leading far, far down into the wilds of the Undercoast. Search every corner. Talk with every person. Look into the political bullshit above and the esoteric madness below. Eventually you'll find a way forward...",
          " Et enfin, tu es descendu droit dans la Cité Inférieure. Des couloirs ésotériques pleins de pièges. Des secrets à chaque coin. Des monstres <i>rampant</i> depuis les profondeurs.\\n\\nQuelqu'un ou <i>quelque chose</i> tente de te cacher la vérité. Et maintenant tu l'as trouvé : un passage secret, menant loin, très loin dans les contrées sauvages de la Sous-Côte. Fouille chaque recoin. Parle à chaque personne. Penche-toi sur les conneries politiques d'en haut et la folie ésotérique d'en bas. Tu finiras par trouver un chemin..."),
    (257, " Then there's that weird masked assassin. You have NO CLUE who has it out for you. But somebody does.",
          " Et puis il y a cet étrange assassin masqué. Tu n'as AUCUNE IDÉE de qui en a après toi. Mais quelqu'un, oui."),
    (265, " You had a little chat with Visken, the pale-faced local mortician.",
          " Tu as eu une petite discussion avec Visken, le pâle croque-mort local."),
    (584, '"You pulling an all nighter? ...Alright. Let\'s do this."',
          '« Tu fais une nuit blanche ? ...D\'accord. Allons-y. »'),
    (1038, "(And you're a... <i>Beefy Cleric</i>? Alright. I don't judge. It's your character.)",
           "(Et tu es un... <i>Clerc Costaud</i> ? D'accord. Je ne juge pas. C'est ton personnage.)"),
    (2658, "Alright, so- last time you got through the whole intro sequence. Just a day ago a local tea shop exploded, and it's your job to figure out why. For some reason, you woke up at the bottom of a morgue. Great start.",
           "Bon, alors — la dernière fois, tu as traversé toute la séquence d'intro. Il y a juste un jour, un salon de thé local a explosé, et c'est ton boulot de comprendre pourquoi. Pour une raison quelconque, tu t'es réveillé au fond d'une morgue. Beau début."),
    (2747, "And then... there's <i>Iomestra</i>. You didn't really run into her, did you?",
           "Et puis... il y a <i>Iomestra</i>. Tu ne l'as pas vraiment croisée, hein ?"),
    (2874, "As for Visken, your little adventure is nothing to him. Obviously.",
           "Quant à Visken, ta petite aventure n'est rien pour lui. Évidemment."),
    (6544, "I can't wait to see what you do next.\\n<i>-Christoffer Bodegård</i>",
           "J'ai hâte de voir ce que tu fais ensuite.\\n<i>-Christoffer Bodegård</i>"),
    (7435, "It's almost time. We're nearing the end. Last time you found Meriadoc, the <i>star witness</i> you've been looking for all campaign. He told you about this invisible smoking person who 'entered into the Pillar'. As crazy as it sounds, you're certain: you need to follow. \\n\\nYou need to find a way into the Pillar of Jor.",
           "C'est presque l'heure. On approche de la fin. La dernière fois, tu as trouvé Meriadoc, le <i>témoin clé</i> que tu cherchais depuis toute la campagne. Il t'a parlé de cette personne fumante invisible qui « est entrée dans le Pilier ». Aussi fou que ça paraisse, tu es certain : tu dois suivre.\\n\\nTu dois trouver un moyen d'entrer dans le Pilier de Jor."),
    (11976, "Time to play another session! Though if you see this message, that means I actually couldn't pull up any info about what happened last session. That means something went terribly wrong. Either I messed up somewhere, or you meddled with the save file. If you see this, and you <i>didn't</i> touch any save file, then feel free to let me know! <i>-Chris</i>",
            "C'est l'heure d'une autre session ! Bon, si tu vois ce message, ça veut dire que je n'ai pas pu récupérer d'info sur la session précédente. Donc quelque chose a très mal tourné. Soit j'ai foiré quelque part, soit tu as bidouillé le fichier de sauvegarde. Si tu vois ça et que tu <i>n'as pas</i> touché à un fichier de sauvegarde, n'hésite pas à me prévenir ! <i>-Chris</i>"),
    (13499, "[But I promise: you'll be able to delve <i>much</i> deeper on release day. -Chris]",
            "[Mais promis : tu pourras explorer <i>bien</i> plus profond le jour de la sortie. -Chris]"),

    # ---- Tier de difficulté des jets (badge DC en jeu) ----
    (3978, 'Challenging', 'Difficile'),    # 11 → 9 in-place
    (4735, 'Daunting',    'Pénible'),      # 8 → 8 (P-é(2)-n-i-b-l-e = 8 bytes UTF-8) in-place
    (5207, 'Effortless',  'Trivial'),      # 10 → 7 in-place
    (8088, 'Medium',      'Moyen'),        # 6 → 5 in-place
    (10323, 'Simple',     'Simple'),       # 6 → 6 same (no change but documented)
    # 'Impossible' (idx 6767) reste 'Impossible' en FR — pas de patch

    # ---- Notes de session — additional Chris narrator strings (group 100-280) ----
    (113, " \\n\\nAs it looks now, there's only one more place to look: <i>The City Below</i>. Your star witness, this <i>Frank son of Frank</i>, seems to have been heading that way. It's time to follow, down into the Below...",
          " \\n\\nPour l'instant, il ne reste qu'un seul endroit à examiner : <i>La Cité Inférieure</i>. Ton témoin clé, ce <i>Frank fils de Frank</i>, semble s'y être rendu. Il est temps de suivre, là-bas en bas..."),
    (114, " \\n\\nBeyond that, you also found the owner. That bird was trying to <i>ship himself</i> across the Coast. Luckily you got to him before his crate got spirited away.",
          " \\n\\nEn plus, tu as aussi trouvé le propriétaire. Cet oiseau essayait de <i>s'expédier</i> à travers la Côte. Heureusement tu l'as eu avant que sa caisse ne soit emportée."),
    (115, " \\n\\nBeyond that, you've also got the owner to track down. From what you've heard about this guy, he could have already left the city. Though maybe if you're lucky you can catch him before he hops onto the next ship down on Waterlane.",
          " \\n\\nEn plus, il te reste à pister le propriétaire. D'après ce que tu as entendu sur ce gars, il a peut-être déjà quitté la cité. Avec un peu de chance, tu pourras le rattraper avant qu'il monte dans le prochain bateau à Waterlane."),
    (117, " \\n\\nEverything about this <i>stinks</i>.",
          " \\n\\nTout ça <i>pue</i>."),
    (118, " \\n\\nFirst off, you still need to get inside. The entrance is in the middle of the big, open outside-area. If you find yourself stuck, there probably should be some other ways of getting inside...",
          " \\n\\nPour commencer, tu dois encore entrer. L'entrée est au milieu de la grande zone ouverte. Si tu te retrouves coincé, il devrait y avoir d'autres moyens d'entrer..."),
    (119, " \\n\\nI should've made it more clear: the City Below - the <i>dungeon</i> - well, that's more of a <i>level 3+</i> area.\\n\\nThen again, if you're feeling lucky... you could always try again?",
          " \\n\\nJ'aurais dû être plus clair : la Cité Inférieure — le <i>donjon</i> — eh bien, c'est plutôt une zone <i>niveau 3+</i>.\\n\\nCela dit, si tu te sens chanceux... tu peux toujours réessayer ?"),
    (120, " \\n\\nThough since you've already gotten into the Tea Shop... well, he's not gonna help you out <i>that</i> much.",
          " \\n\\nCela dit, vu que tu es déjà entré dans le Salon de Thé... eh bien, il ne va pas <i>tant</i> t'aider que ça."),
    (212, " And of course, you also took a look down into the City Below, which you'll have to return to later.",
          " Et bien sûr, tu as aussi jeté un œil dans la Cité Inférieure, où il faudra revenir plus tard."),
    (258, " Then you went out to explore the city. Now, Tolstad is a pretty big place, but just the tiny snippet that you're focused on already has a ton of people around, you had a ton to look at. Now, you still need to find that goblin chieftain...",
          " Puis tu es sorti explorer la cité. Bon, Tolstad est un endroit assez grand, mais juste le petit fragment sur lequel tu te concentres a déjà une tonne de gens autour, tu avais une tonne à examiner. Maintenant, tu dois encore trouver cette cheffe gobeline..."),
    (266, " You should probably report the dead elf to Lady Sageleaf. Unless you're gonna just skip that whole thing.",
          " Tu devrais sans doute signaler l'elfe mort à Lady Sageleaf. À moins que tu sautes complètement ce truc."),
    (583, '"You planning on staying up all night? Maybe you shouldn\'t, Cleric."',
          '« Tu comptes veiller toute la nuit ? Tu devrais peut-être pas, Clerc. »'),

    # ---- Cleric ending notes (3261-3267) ----
    (3261, "But your Azgal-cleric will surely find purpose in the cause.",
           "Mais ton Clerc-Azgal trouvera sûrement un sens dans la cause."),
    (3262, "But your Freestrider-cleric will surely prosper in this modern world. Or at least get a job.",
           "Mais ton Clerc-Errant prospérera sûrement dans ce monde moderne. Ou au moins trouvera un boulot."),
    (3263, "But your Party-loyal cleric will surely find a place among his peers.",
           "Mais ton clerc fidèle-au-Parti trouvera sûrement sa place parmi ses pairs."),
    (3265, "But your cleric will surely rise above it all, as <i>God-Wizard-King</i>.",
           "Mais ton clerc s'élèvera sûrement au-dessus de tout, en tant que <i>Dieu-Mage-Roi</i>."),
    (3266, "But your poor, poor Appleboy-Agrarian will surely find some peace out in the Hills.",
           "Mais ton pauvre, pauvre Appleboy-Agrarien trouvera sûrement un peu de paix dans les Collines."),
    (3267, "But your wonderfully apolitical cleric will surely find himself at home in the chaos.",
           "Mais ton clerc merveilleusement apolitique se sentira sûrement chez lui dans le chaos."),

    # ---- Late game session notes (11811, 13416, 13421, 13422) ----
    (11811, "Then there are questions surrounding those 'Lost Mines' Akzel was looking for. That sounds like a higher tier dungeon to me.",
            "Et puis il y a des questions autour de ces « Mines Perdues » qu'Akzel cherchait. Ça sonne comme un donjon de niveau supérieur."),
    (13416, "You woke up in a morgue. It's the day after a local tea shop exploded, and it's your job to figure out why. So far, you've explored the city and picked up a snarky goblin sidekick. Great stuff. Now it's time for the real deal: as the sun falls upon the city, you <i>know</i>: the Coinlord is waiting.\\n\\nNot literally, he's not the kind of guy to ever wait for anybody, but you've got a meeting with him. Sometime, anytime, after midnight. Just don't leave him waiting all the way till dawn...",
            "Tu t'es réveillé dans une morgue. C'est le lendemain d'une explosion dans un salon de thé local, et c'est ton boulot de comprendre pourquoi. Jusqu'ici, tu as exploré la cité et ramassé un acolyte gobelin caustique. Du beau travail. Maintenant c'est l'heure du vrai défi : alors que le soleil tombe sur la cité, tu <i>sais</i> : le Seigneur de la Monnaie attend.\\n\\nPas littéralement, c'est pas le genre de gars à attendre qui que ce soit, mais tu as un rendez-vous avec lui. Un moment, n'importe quand, après minuit. Ne le fais juste pas attendre jusqu'à l'aube..."),
    (13421, "You've arrived in Tolstad (via waking up in a morgue), you've picked up a goblin sidekick, and now... well, now you need to focus on the actual job. <i>The Tea Shop that Blew Up</i>.",
            "Tu es arrivé à Tolstad (en te réveillant dans une morgue), tu as ramassé un acolyte gobelin, et maintenant... eh bien, il est temps de te concentrer sur le vrai boulot. <i>Le Salon de Thé qui a Sauté</i>."),
    (13422, "You've awoken in a morgue. You've gotten a goblin sidekick. This was supposed to be a simple job - figure out why a local tea shop exploded. Now you're standing here, the image lingering in the back of your skull: <i>a dead elf</i>. It's rare enough to see a <i>live</i> elf.",
            "Tu t'es réveillé dans une morgue. Tu as récupéré un acolyte gobelin. C'était censé être un boulot simple — comprendre pourquoi un salon de thé local a explosé. Maintenant tu te tiens ici, l'image persistante au fond de ton crâne : <i>un elfe mort</i>. C'est déjà assez rare de voir un elfe <i>vivant</i>."),
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
        # ---- Journal section enum names (validés 2026-05-19, mêmes mécanique que stats) ----
        (b'City\0', 'Cite'),         # 4=4 (no accent to fit slot)
        (b'Skills\0', 'Talent'),     # 6=6 (corrigé : 'Doués' n'avait pas le bon sens)
        (b'Folk\0', 'Gens'),         # 4=4
        (b'Esoterics\0', 'Mystères'),  # 9 UTF-8 fits 9
        (b'Geography\0', 'Régions'),   # 8 UTF-8 fits 9
        (b'History\0', 'Annales'),   # 7=7 (corrigé : 'Histor.' était abrégé)
        (b'Language\0', 'Langue'),   # 6 fits 8
        (b'Politics\0', 'Pouvoir'),  # 7 fits 8 (corrigé : 'Politiq.' était abrégé)
        (b'Religion\0', 'Religion'), # 8=8 same
        (b'Nature\0', 'Nature'),     # 6=6 same
        (b'Literature\0', 'Romans'), # 6 fits 10 (corrigé : 'Lectures' moins juste)
        # ---- Spell name (Bless) — tentative, observer si compteur Grimoire reste OK ----
        (b'Bless\0', 'Béni'),  # 5 UTF-8 (B-é-n-i, é=2B) fits 5
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

    # ---- STRSEC patches DÉSACTIVÉS 2026-05-26 (HOTFIX v1.3.4) ----
    # La section 'strings' contient les noms de TYPES/CLASSES/MÉTHODES de réflexion .NET,
    # PAS seulement des noms d'enum d'affichage. Les patcher par byte-match casse la
    # résolution de scripts et de scènes :
    #   - "Bless" (52? non, 2) → cassait le script du sort Bless (log : "referenced script Bless missing")
    #   - "History" = 52 occurrences, "Language" = 26 → corrompait des dizaines de noms
    #     de types/méthodes de réflexion → "scene not found", map cassée, zones inaccessibles.
    # Report joueurs Nexus (zones inaccessibles, Goblin Garden "scene not found", map coupée).
    # L'affichage FR des stats/journal vient des patches stringLiteral (idx), qui restent actifs.
    # patch_strings_section(raw, version, sOff, sSize)
    print("[STRSEC] DÉSACTIVÉ (cassait la résolution de scripts/scènes) — voir hotfix v1.3.4")
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
