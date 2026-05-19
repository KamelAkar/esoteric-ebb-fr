# Pipeline de génération du patch

## Vue d'ensemble

```
┌─ source-data/ui-original/*.csv ─┐
│  source-data/strings_master.csv │   sources de traduction
└─────────────────┬───────────────┘
                  │
                  ▼ (édition manuelle / scripts ad-hoc)
                  │
         ┌────────┴────────┐
         ▼                 ▼
    translations/      translations/
    metadata_*.tsv     assets_*.tsv
         │                 │
         │                 │
         ▼                 ▼
    tools/02_apply_   tools/04_ui_patch_
    metadata.py       assets.py
         │                 │
         ▼                 ▼
    global-metadata.dat   level*.assets
         (patchés dans Esoteric Ebb_Data/)
```

## Workflow type

### 1. Dump initial des sources

À faire une seule fois après une mise à jour du jeu :

```bash
python tools/01_dump_metadata.py
# Génère : translations/all_strings.tsv
#          translations/candidates.tsv (filtrées)
```

### 2. Édition des traductions

Éditer les fichiers TSV dans `translations/` :

- `metadata_patches.tsv` — patches du `global-metadata.dat` (string literals)
- `strsec_patches.tsv` — repointing des noms d'enum / réflexion
- `ui_patches.tsv` — patches length-prefixed dans les `.assets` / `level*`

Format TSV : `idx<TAB>english<TAB>french<TAB>notes`.

### 3. Application

```bash
# Backup automatique du global-metadata.dat (1ère fois)
python tools/02_apply_metadata.py

# Pour les noms d'enum (Sagesse, Dextérité, etc.)
python tools/03_strsec_repoint.py

# Pour les UI labels dans level files
python tools/04_ui_patch_assets.py
```

### 4. Test

Lance le jeu via Steam. Si crash → restaurer les backups :

```bash
cp backups/global-metadata.dat "C:\path\to\game\Esoteric Ebb_Data\il2cpp_data\Metadata\"
cp backups/level*.bak "C:\path\to\game\Esoteric Ebb_Data\"
```

### 5. Packaging

```bash
python tools/05_package_zip.py
# Génère : dist/EsotericEbb-FR-Patch-v1.0.zip
```

## Règles de sécurité

1. **Toujours backup avant patch** — les outils le font automatiquement la première fois
2. **Tester après chaque changement** — un patch peut casser une sauvegarde
3. **Patches risqués** : les noms d'un seul mot souvent utilisés comme clés de binding C# (Inventory, Spells, Cleric, Day…). Voir `KNOWN_LIMITATIONS.md`
4. **Quitter complètement Steam** entre tests — la metadata est chargée au démarrage du process
