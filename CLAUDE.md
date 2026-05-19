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

## Conventions de traduction (à respecter pour toute nouvelle entrée)

### Registre et voix

- **Vouvoiement** par défaut : règles du jeu, UI, voix divines, NPCs formels
- **Tutoiement intime** : voix intérieures ↔ personnage joueur, et Snell (gobelin compagnon) ↔ joueur

### Style général — registre soutenu et légèrement littéraire

Esoteric Ebb s'inspire de **Disco Elysium** : narration en deuxième personne, dialogues philosophico-absurdes, voix intérieures qui commentent l'action, humour pince-sans-rire. La traduction française doit refléter ce ton :

- **Registre soutenu mais pas pompeux** : phrases bien construites, vocabulaire précis, sans surcharge. Privilégier les tournures littéraires aux formulations plates.
  - ✓ « Le silence retombe sur la pièce, lourd comme un manteau humide. »
  - ✗ « C'est silencieux maintenant. »

- **Archaïsmes occasionnels** quand le contexte s'y prête (voix divines, vieilles inscriptions, NPCs érudits, scènes oniriques) : « point » au lieu de « pas » dans certaines constructions, « céans », « jadis », « moult », « sieur », inversions sujet-verbe pour effets dramatiques.
  - Voix divine : « Ainsi soit-il, mortel. Que ta quête ne souffre point d'entrave. »
  - Inscription antique : « Ci-gît celui qui osa défier les Arcanes. »

- **Humour préservé** : le jeu est souvent drôle (vulgarités assumées, observations absurdes, sarcasmes). NE PAS aseptiser. Garder le mordant.
  - ✓ « Putain de poète. » (pour "fucking poet")
  - ✓ « Roublard de Mes Deux » (pour "Dick-Ass Rogue" — déjà dans le glossaire établi)

- **Variété de voix** : chaque voix intérieure / NPC a un caractère. Adapter le registre :
  - Voix philosophiques → plus érudite, vocabulaire abstrait
  - Snell le gobelin → plus directe, familière, fautes assumées
  - Voix divines → solennelle, archaïsante
  - Narration → littéraire neutre

- **Préserver le rythme** : les phrases courtes des originaux restent courtes, les longues restent longues. Pas de fusion ni de découpage gratuit qui changerait la cadence.

- **Évocations sensorielles** : le texte original est souvent riche en images concrètes (odeurs, textures, atmosphères). Les traduire avec la même précision plutôt que de les généraliser.

### Terminologie D&D 5e VF officielle

Toujours utiliser les termes français officiels D&D 5e :

- Classes : **Clerc**, **Roublard**, **Magicien**, **Druide**, **Barde**, **Barbare**, **Paladin**, **Guerrier**, **Rôdeur**, **Moine**, **Ensorceleur**, **Occultiste**
- Stats : **Force / Dextérité / Constitution / Intelligence / Sagesse / Charisme**
- Sorts standards :
  - **Communication avec les Morts/Animaux/Plantes** (jamais "Parler aux Morts")
  - **Main du Mage**
  - **Dissipation de la Magie**
  - **Bénédiction**, **Bouclier de Foi**, **Soin des Blessures**
- **Dé de Vie / Dés de Vie** (jamais "Hit Die")
- **DD** (Difficulté) pas "CD" — `DD 15 : Succès` / `Échec`

### Noms propres du monde (NE PAS traduire)

- **Norvik**, **Tolstad**, **Snell**, **Strokeback**, **Visken**, **Modissa**, **Ettir**, **Jor**, **Pinja**, **Gorm** : noms propres conservés tels quels
- **Garde-d'Urth** (avec trait d'union, jamais "Garde d'Urth" ou "Urthguard")
- **Antre Inférieur** (traduction du lore, conservée — Lower Lair = nom de scène Unity à ne PAS toucher)
- Noms de scènes Unity (`Lower Lair`, `Visken's Lair`, `Upper Tolstad`…) : **JAMAIS patcher** — utilisés par le code pour charger les scènes

### Marqueurs techniques à préserver

Dans toute traduction, préserver intacts :
- Tags rich text TMP : `<b>`, `<i>`, `<size=N>`, `<color=#...>`, `<smallcaps>`, `<shake>`
- Placeholders de format : `{0}`, `{1}`, `$WIZARD`, `$CLERIC` (et autres `$VAR`)
- Textes en langues étrangères dans le narratif (Latin, espagnol archaïque, etc.) — laissés tels quels par choix d'auteur

### Style "polish"

- Espaces insécables/normales avant `:`, `;`, `!`, `?` selon convention française (le jeu rend les espaces normales acceptablement)
- Guillemets : `«` et `»` plutôt que `"..."` pour les citations dans le narratif (déjà en place dans les CSVs)
- Apostrophe typographique `'` PAS recommandée car parfois mal rendue par TMP — utiliser `'` ASCII

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
