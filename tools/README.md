# Outils de la pipeline

## Outils Python (workflow principal)

Tous les scripts utilisent des chemins absolus pointant vers le dossier Steam d'Esoteric Ebb. Adapte en tête de chaque fichier si nécessaire.

### `01_dump_metadata.py`

Dump toutes les chaînes du `global-metadata.dat` dans un TSV. À lancer une seule fois (ou après une mise à jour du jeu).

```bash
python tools/01_dump_metadata.py
# Sortie : metadata_strings/all_strings.tsv (~20 000 lignes)
#          metadata_strings/candidates.tsv (filtrées)
```

### `02_apply_metadata.py`

Applique les patches `translations/metadata_patches.tsv`. Gère automatiquement :
- **In-place** quand le français ≤ longueur originale
- **Repoint** quand le français dépasse (append + décalage des sections)
- Backup automatique vers `backups/global-metadata.dat.backup` à la 1ère exécution

```bash
python tools/02_apply_metadata.py
# Sortie : metadata_strings/global-metadata.dat.patched
# Puis copier vers le jeu :
cp metadata_strings/global-metadata.dat.patched "$STEAM/Esoteric Ebb_Data/il2cpp_data/Metadata/global-metadata.dat"
```

### `03_strsec_repoint.py`

Repointing de la section `string` (noms d'enum/réflexion) du metadata. À utiliser pour les labels affichés via `Enum.ToString()` (stats, interactions).

```bash
python tools/03_strsec_repoint.py
# Écrit directement dans le jeu (post-02_apply_metadata)
```

### `04_ui_patch_assets.py`

Find/replace byte-level dans les `.assets` et `level*`. Contraintes :
- Slot size (4 + content + padding mod 4) doit rester identique entre EN et FR
- Backup auto vers `backups/`

```bash
python tools/04_ui_patch_assets.py
```

### `faction_patch_assets.py`

Variante du précédent qui garde la longueur originale et padde le contenu avec des nulls. Utilisé pour Freestrider → Errant.

## Outil C# (`dotnet-deploy/`)

Wrapper autour de [AssetsTools.NET](https://github.com/nesrak1/AssetsTools.NET) avec plusieurs modes :

| Mode         | Description                                            |
|--------------|--------------------------------------------------------|
| `inspect`    | Liste types et TextAssets dans un .assets              |
| `textasset`  | Patche un TextAsset par nom (replace m_Script)         |
| `tmptext`    | Patche m_text de TextMeshPro spécifiquement (pas m_Name)|
| `inkbulk`    | Bulk substring replace dans tous les TextAssets        |
| `menuctx`    | Patche MonoBehaviour avec filtres include/exclude      |
| `menusmart`  | Comme menuctx, skip les références C# typées           |
| `findtext`   | Cherche chaînes dans MonoBehaviour fields              |
| `findobj`    | Trouve l'objet contenant un offset                     |

### Build

```bash
cd tools/dotnet-deploy
dotnet build -c Release
```

L'exécutable est généré dans `tools/dotnet-deploy/bin/Release/net*/`.

### Utilisation

```bash
# Inspecter
./dotnet-deploy inspect "$STEAM/Esoteric Ebb_Data/resources.assets"

# Patcher un TextAsset
./dotnet-deploy textasset "$STEAM/Esoteric Ebb_Data/resources.assets" GlossaryTerms.csv

# Patcher m_text de TMP (par valeur exacte)
./dotnet-deploy tmptext "$STEAM/Esoteric Ebb_Data/level1" "Helms" "Casques"
```

## Ordre d'exécution typique

```bash
# Une seule fois après update du jeu :
python tools/01_dump_metadata.py

# À chaque modification des traductions :
python tools/02_apply_metadata.py
cp metadata_strings/global-metadata.dat.patched "$STEAM/Esoteric Ebb_Data/il2cpp_data/Metadata/global-metadata.dat"

python tools/03_strsec_repoint.py
python tools/04_ui_patch_assets.py
python tools/faction_patch_assets.py

# Test (Steam → quitter le jeu → relancer)
```
