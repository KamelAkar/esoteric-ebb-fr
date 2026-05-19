# Limitations connues

État vérifié visuellement sur v1.2.2 le 2026-05-19.

## Ce qui est traduit (~99%)

- ✅ 100% des dialogues narratifs Ink (~70 000 lignes)
- ✅ Glossaire complet
- ✅ Descriptions de sorts (D&D 5e VF)
- ✅ Objectifs de quêtes
- ✅ Dons, classes, items, livres, magazines
- ✅ Stats : Force / Dextérité / Constitution / Intelligence / Sagesse / Charisme
- ✅ Résultats de checks : `DD N : Succès` / `Échec`
- ✅ Dates : `mars 22 an 27 EP`
- ✅ Format XP : `XP gagnée : +5xp !`
- ✅ Descriptions longues (repos court, effets, Notes de Session)
- ✅ Mois, jours, factions politiques (Errant, Apolitique)
- ✅ `[Don vide]`, suffix `' reçu.` après ramassage d'objet
- ✅ Crédits, mentions légales, message de fin
- ✅ Onglets inventaire patchés 2026-05-19 : Casques / Babioles / Consomm. / Livres / Cléricaux
- ✅ Placeholder glossaire vide : `[Ce glossaire est vide.]`

## Labels qui restent en anglais

Ces strings sont utilisées comme **clés de binding C#** dans le code. Les patcher fait crasher le jeu ou casser les saves.

| Label EN (observé in-game) | Souhait FR        | Raison du blocage                                                  |
|----------------------------|-------------------|--------------------------------------------------------------------|
| `Inventory`                | Inventaire        | STRSEC repoint freeze l'UI inventaire (utilisé par reflection)     |
| `Day` / `Day 1` titre      | Jour / Jour 1     | Patche casse la substitution de variables                          |
| `Level` (HUD) / `Lv 1 Cleric` | Niveau         | Patche casse le save preview                                       |
| `Cleric/Wizard/Rogue/Druid/Bard/Barbarian` | (idem) | Casse le save preview du menu principal                       |
| `Quit`                     | Quitter           | Patche risqué (binding bouton UI)                                  |
| `You` / `YOU` (speaker)    | Toi / TOI         | Patche risqué                                                      |

### Labels qui restent en anglais (état au 2026-05-19)

**Onglets inventaire bloqués** (testés et confirmés casser inventory loading si patchés en metadata — voir liste `BROKEN` dans `tools/02_apply_metadata.py`) :
- `All Items` (idx 2633)
- `Weaponry` (idx 13125)
- `Key Items` (idx 7540)
- `Food`, `Texts`, `Inventory`, `Spells`, `Collected Spells`, `Prepared Spells`, `Questing`, `Difficulty Class`

**Onglets journal/glossaire** : `City`, `Skills`, `Esoterics`, `Folk`, `Geography` — **pas dans la metadata**, source réelle non identifiée (.assets probablement). Candidats à investigation `dotnet-deploy tmptext` ou recherche TMP_Text dans les sharedassets.

**Noms de sorts** (description traduite, seul le titre reste EN) : `Cure Wounds`, etc. Idx 4502 dans metadata existe mais patcher cette entrée n'a aucun effet visuel (testé) — le titre est sourcé ailleurs (probablement TMP asset).

## Limitations narratives

- **`one single time` dans Quest_34** : le template français contient `$WIZARD fois` où `$WIZARD` est substitué par une chaîne anglaise hardcodée (`"one single time"` / `"two times"`). Fix possible en réécrivant le template FR pour éviter la dépendance.

- **Anciens saves** : les labels stockés dans les fichiers .sav (autosaves d'avant patch) restent en anglais. Les nouvelles sauvegardes utilisent les nouveaux formats.

## Limitations architecturales

- **Ordre `mars 22` au lieu de `22 mars`** : la concaténation se fait dans le code C# (`month + " " + day`). Réordonner exigerait modifier `GameAssembly.dll` (hors scope).

- **TMP_Text_SetCharArray_Hook3 (XUnity)** : ce hook échoue sur Unity 6, raison pour laquelle on a abandonné l'approche BepInEx + XUnity au profit du patching direct.

## Catégorie "à explorer"

Pistes pour itérations futures :

- **Recompilation IL2CPP partielle** : modifier `GameAssembly.dll` via Il2CppDumper + un éditeur d'assembleur. Permettrait de fixer l'ordre des dates et certains labels bloqués.
- **AssetsTools.NET pour TMP m_text** : étendre `dotnet-deploy.exe` pour parser et patcher chirurgicalement les `m_text` de TMP sans toucher aux `m_Name`. Reste pertinent pour `City/Skills/Esoterics/Folk/Geography` (onglets journal — absents de metadata) et les noms de sorts (`Cure Wounds` etc., titres sourcés hors metadata).
- **Mod Studio plugin** : développer un plugin BepInEx custom (Il2CppInterop direct) qui hooke les méthodes problématiques. Lourd à maintenir entre mises à jour du jeu.
