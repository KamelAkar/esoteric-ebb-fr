# Patcher les fichiers `.assets` et `level*`

## Contexte

Unity stocke les ressources dans `Esoteric Ebb_Data/` :

- `resources.assets` — TextAssets globaux, prefabs UI, glossaire
- `sharedassets{0..N}.assets` — assets par scène (TMP texts, Ink JSON, etc.)
- `level{0..N}` — données de scène (GameObjects, composants, MonoBehaviours)
- `globalgamemanagers.assets` — configuration globale Unity

## Format des chaînes

Unity stocke les strings en **length-prefixed avec alignement 4 octets** :

```
┌────────────┬──────────────┬─────────────┐
│ 4B length  │ N bytes UTF8 │ pad to mod4 │
└────────────┴──────────────┴─────────────┘
```

Exemple `"Helmets"` (7 bytes) → `07 00 00 00 48 65 6C 6D 65 74 73 00` (12 bytes total : 4 + 7 + 1 pad).

## Stratégies de patch

### A. Remplacement même-taille de slot

Si `slot_size(eng) == slot_size(fr)` (incluant padding) :
- Change le champ `length`
- Réécris le contenu UTF-8
- Padde avec `\0` jusqu'à la prochaine frontière 4-octets

Exemples valides :
- `Behold` (6, slot=12) → `Examiner` (8, slot=12) ✓
- `Helmets` (7, slot=12) → `Casques` (7, slot=12) ✓
- `Trifle` (6, slot=12) → `Piquer` (6, slot=12) ✓

### B. Remplacement longueur inchangée + padding

Pour `Freestrider` (11 bytes, slot=16) → `Errant` (6 bytes) :
- **Garder length=11** (sinon casse l'alignement Unity)
- Écrire `Errant\0\0\0\0\0` (6 + 5 nulls dans les 11 octets de contenu)
- La string s'affiche `Errant` car C# termine à `\0`

### C. Remplacement avec shift (longueur différente, slot différent)

⚠️ **À ÉVITER** — nécessite de décaler toutes les données suivantes ET de mettre à jour tous les pointeurs internes Unity. Souvent casse le chargement.

Pour les cas où c'est nécessaire (rare), utiliser `dotnet-deploy.exe` qui parse correctement le format Unity via AssetsTools.NET.

## Pièges courants

- **Plusieurs occurrences** : un même texte peut apparaître comme :
  - `m_text` de `TextMeshProUGUI` (display UI)
  - `m_Name` de `GameObject` (utilisé par `GameObject.Find()`)
  - Asset name interne

  Patcher TOUTES les occurrences sans distinction casse les lookups de GameObjects.

- **JSON dans TextAssets** : les fichiers Ink JSON contiennent des refs `"^.Freestrider_*"` qui ne sont PAS des labels affichés mais des clés de variables narratives. Les patcher casse le runtime Ink.

- **C# Class names** : tout ce qui ressemble à un identifier valide (`HelmetEquipSTR`, `BeholdSheetClose`) est probablement utilisé par reflection.

## Heuristiques de sécurité

Patcher uniquement quand :

1. Le slot reste de la même taille totale (4 + content + pad mod 4)
2. La string n'est PAS un identifier valide (`[A-Z][a-z]*[A-Z][a-z]*` pattern → souvent une classe)
3. La string ne contient PAS de `.` (paths Unity comme `UnityEngine.UI`)
4. La string contient idéalement un espace, un caractère spécial, ou une ponctuation (= texte UI)

Pour les cas ambigus → utiliser `dotnet-deploy.exe` qui distingue `m_text` de `m_Name` via le typage AssetsTools.NET.

## Outils

- `tools/04_ui_patch_assets.py` — find/replace byte-level générique (rapide, batch)
- `tools/dotnet-deploy/` — C# avec AssetsTools.NET, parse les types Unity (lent mais précis)
