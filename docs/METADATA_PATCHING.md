# Patcher `global-metadata.dat` (IL2CPP)

## Contexte

Esoteric Ebb tourne sur Unity 6 IL2CPP. Le code C# est compilé en C++ natif (`GameAssembly.dll`), et toutes les chaînes littérales du code vivent dans `Esoteric Ebb_Data/il2cpp_data/Metadata/global-metadata.dat`.

XUnity.AutoTranslator a des hooks instables sur Unity 6 (`TMP_Text_SetCharArray_Hook3` échoue), donc on ne peut pas intercepter ces strings à l'exécution. **La solution propre est de patcher directement le fichier metadata.**

## Format du fichier

Header de 256 octets contenant 31 paires `(offset, size)` pour chaque section IL2CPP :

| Index | Section                  | Description                              |
|------:|--------------------------|------------------------------------------|
| 0     | `stringLiteral`          | Table d'index : `(length, dataIndex)`    |
| 1     | `stringLiteralData`      | Bytes UTF-8 des littéraux du code C#     |
| 2     | `string`                 | Noms de types/méthodes/champs/enums      |
| 3..30 | typeDefinitions, etc.    | Autres structures IL2CPP                 |

Les chaînes dans `stringLiteralData` sont **packées** (pas de séparateur). Chaque entrée d'index pointe vers `dataOffset` et lit `length` octets.

Les chaînes dans `string` (section 2) sont **null-terminated**, accédées par offset relatif depuis le début de la section.

## Stratégies de patch

### A. In-place (longueur ≤ originale)

Le plus simple. Pour idx `N` qui pointe vers `"Hit Dice +1"` (11 octets), on peut écrire `"DV +1"` (5 octets) :

1. Écrire `"DV +1\0\0\0\0\0\0"` (5 octets + 6 nulls) dans le slot
2. Mettre à jour le champ `length` de l'entrée d'index → 5

Le runtime lit `length` octets et obtient `"DV +1"`. Aucune section décalée.

### B. Repoint (longueur > originale)

Quand le français est plus long, on étend la section.

1. Append le nouveau texte à la fin de `stringLiteralData`
2. Mettre à jour `dataIndex` (vers la nouvelle position) et `length`
3. **Étendre `stringLiteralDataSize`** dans le header
4. **Décaler tous les offsets** des sections 2..30 dans le header
5. **Padder à 4 octets** pour préserver l'alignement (sinon les références u32 deviennent désalignées)

Le runtime lit dynamiquement les offsets depuis le header, donc le décalage est transparent.

### C. STRSEC repoint (section `string`)

Plus délicat car cette section n'a pas d'index table — chaque nom est référencé par son offset u32 disséminé dans d'autres structures (`typeDefinitions`, `fieldDefinitions`, etc.).

1. Append le nouveau nom (null-terminated) à la fin de la section `string`
2. **Scan global du fichier** pour les occurrences u32 de l'ancien offset (alignées sur 4 octets)
3. Remplacer ces u32 par le nouvel offset
4. Étendre `stringSize`, décaler les sections suivantes

Ça marche pour Wisdom → Sagesse, Dexterity → Dextérité, etc. (testé : 3 références u32 chacun).

## Patches risqués

⚠️ **Ne PAS patcher** les chaînes utilisées comme :

- Clés de comparaison C# : `if (status == "Cleric")` — casserait les saves créés avec l'ancien nom
- Noms de classes/composants Unity : `GameObject.Find("Inventory")` — `null` après patch
- Clés de format binding : `BindingPath("Spells.count")` — bind échoue

Heuristique : un mot seul (`Inventory`, `Spells`, `Cleric`, `Day`) est probablement une clé. Multi-mots (`[Don vide]`, `Spend 1 hour to recover...`) sont safe.

## Outils

- `tools/01_dump_metadata.py` — extrait tous les literals dans `translations/all_strings.tsv`
- `tools/02_apply_metadata.py` — applique `translations/metadata_patches.tsv` (in-place + repoint auto)
- `tools/03_strsec_repoint.py` — applique `translations/strsec_patches.tsv` (section string)

Tous les outils backupent vers `backups/` à la première exécution et lisent depuis là, donc ré-exécutables sans corruption cumulative.
