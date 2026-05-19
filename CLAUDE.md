# Contexte pour Claude Code

Ce projet produit un **patch de traduction française pour Esoteric Ebb** (jeu Unity 6 IL2CPP). Le patch s'installe en drag-and-drop dans le dossier Steam — **aucun runtime mod (BepInEx, XUnity) requis**.

## État du projet

**~99% du texte est en français.** Reste ~10-15 labels UI courts (1-2 mots) qui résistent car utilisés comme clés de binding C#. Voir `docs/KNOWN_LIMITATIONS.md`.

## Localisation du jeu

Le jeu vit dans :
```
C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\
```

Les fichiers patchés sont dans `Esoteric Ebb_Data/` :
- `il2cpp_data/Metadata/global-metadata.dat` — strings hardcodés du code C#
- `resources.assets` — UI/glossaire/UI prefabs
- `sharedassets{0..N}.assets` — contenu Ink, descriptions
- `level{0..24}` — données de scène, faction labels, action verbs

## Architecture de la pipeline

```
translations/*.tsv  ──►  tools/*.py  ──►  fichiers du jeu modifiés
                       (in-place + repoint avec backups auto)
```

3 pipelines indépendantes, à appliquer dans l'ordre :

1. **`02_apply_metadata.py`** — patche `global-metadata.dat` (string literals + STRSEC section)
2. **`03_strsec_repoint.py`** — repoint des noms d'enum dans la section `string` (Sagesse/Dextérité/Examiner)
3. **`04_ui_patch_assets.py`** + **`faction_patch_assets.py`** — find/replace byte-level dans `.assets` + `level*`

## Commandes essentielles

```bash
# Dump initial (à refaire si update du jeu)
python tools/01_dump_metadata.py

# Pipeline standard après édition des TSV
python tools/02_apply_metadata.py
cp metadata_strings/global-metadata.dat.patched "$STEAM/Esoteric Ebb_Data/il2cpp_data/Metadata/global-metadata.dat"
python tools/03_strsec_repoint.py
python tools/04_ui_patch_assets.py
python tools/faction_patch_assets.py
```

**$STEAM** = `"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb"` (avec quotes à cause de l'espace).

## Règles cruciales

### 1. Toujours backupper avant patcher

Les scripts le font automatiquement à la première exécution dans `backups/`. Ne pas supprimer ces fichiers.

### 2. Quitter complètement le jeu entre tests

La metadata IL2CPP est lue **une seule fois** au démarrage du process Unity. "Retour menu" en jeu ne suffit PAS — il faut Steam → Quitter, puis relancer.

### 3. Ne PAS patcher les clés de binding

Les chaînes mono-mot (`Inventory`, `Spells`, `Cleric`, `Day`, `Helms`, `Wizard`, etc.) sont souvent utilisées par le code C# comme :
- Clés de comparaison : `if (state == "Cleric")`
- Noms de GameObject : `GameObject.Find("Inventory")`
- Clés de format binding

Les patcher casse les saves, l'UI, ou les transitions. Si tu veux essayer quand même, **fais une seule entrée à la fois et test immédiatement**.

### 4. Format des TSV

`translations/metadata_patches.tsv` :
```
idx	english	french	notes
752	' Added.	' reçu.	in-place
```
- `idx` : index de la string dans `stringLiteral` (cf. `tools/01_dump_metadata.py`)
- `english` : texte attendu (vérification de sécurité)
- `french` : remplacement souhaité
- `notes` : commentaire libre

Les lignes `# ...` sont des commentaires.

### 5. Caractères UTF-8 et tailles d'octets

Compter en **octets UTF-8**, pas en caractères :
- `é` = 2 octets, `è` = 2 octets, `à` = 2 octets, `ç` = 2 octets, `É` = 2 octets
- `Sagesse` = 7 octets (ASCII) — pas 6
- `Dextérité` = 11 octets (2× é)

In-place possible si `len(fr_utf8) ≤ len(eng)`. Sinon → repoint automatique.

## Approches qui ont échoué (ne PAS retenter)

- **BepInEx + XUnity.AutoTranslator** : abandonné. Sur Unity 6, le hook `TMP_Text_SetCharArray_Hook3` échoue, et activer les flags MonoMod casse TOUS les hooks. Trop instable + package lourd.
- **Patcher `Cleric` / `Wizard` / `Day` / `Level` dans metadata** : casse le save preview du menu (X placeholders).
- **STRSEC repoint de `Inventory`** : freeze l'UI inventaire à l'ouverture.
- **Changer la longueur d'un slot Unity** (`Freestrider` → `Errant` avec length=6) : décale les pointeurs internes, le jeu crash au chargement.

## État BepInEx actuel

Le dossier `BepInEx/` peut être présent dans `$STEAM/` (rémanent des essais précédents). Si le loader `winhttp.dll` est renommé en `.disabled`, BepInEx ne charge pas. C'est le mode de fonctionnement cible pour la v1.0.

Voir `docs/PIPELINE.md`, `docs/METADATA_PATCHING.md`, `docs/ASSETS_PATCHING.md`, `docs/KNOWN_LIMITATIONS.md` pour les détails techniques.

## Pour le packaging Nexus v1.0

À implémenter (script `05_package_zip.py` à venir) :
1. Copier les fichiers patchés du jeu vers `dist/EsotericEbb-FR-Patch-v1.0/`
   - `Esoteric Ebb_Data/il2cpp_data/Metadata/global-metadata.dat`
   - `Esoteric Ebb_Data/resources.assets`
   - `Esoteric Ebb_Data/sharedassets{0..N}.assets`
   - `Esoteric Ebb_Data/level{0..24}`
2. Inclure `LISEZ_MOI.txt` (instructions FR)
3. Zipper → `dist/EsotericEbb-FR-Patch-v1.0.zip` (~50 MB attendu)
4. Upload Nexus
