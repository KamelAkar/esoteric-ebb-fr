# Esoteric Ebb — Traduction Française

Patch de traduction française pour [Esoteric Ebb](https://store.steampowered.com/app/2647560/) (Unity 6 IL2CPP).

## Pour les joueurs

1. Télécharge la dernière release ZIP depuis Nexus Mods
2. Steam → clic droit Esoteric Ebb → Propriétés → Fichiers installés → Parcourir
3. Extrais le ZIP dans le dossier du jeu, écrase quand demandé
4. Lance le jeu

**Désinstallation** : Steam → Vérifier l'intégrité des fichiers du jeu.

## Pour les contributeurs / développeurs

Ce dépôt contient la pipeline complète pour générer le patch. Voir [`docs/PIPELINE.md`](docs/PIPELINE.md) pour le workflow.

### Architecture rapide

Le jeu est en **Unity 6 IL2CPP**, ce qui complique la traduction. Au lieu d'un runtime mod (BepInEx + XUnity.AutoTranslator), on patche directement :

- **`global-metadata.dat`** : chaînes hardcodées du code C# compilé (DC results, dates, format strings…). Voir [`docs/METADATA_PATCHING.md`](docs/METADATA_PATCHING.md).
- **`.assets` / `level*`** : contenu Ink, glossaire, UI prefabs. Voir [`docs/ASSETS_PATCHING.md`](docs/ASSETS_PATCHING.md).

Le patch final est **drag-and-drop pur** — pas de DLL injection, pas de plugin, pas d'overhead runtime.

### Structure

```
tools/             Scripts Python + outil C# (AssetsTools.NET)
translations/      Tables TSV éditables des chaînes traduites
source-data/       CSVs source EN/FR + textes de référence
backups/           Fichiers vanilla pour rollback
game-files/        Lien symbolique ou copie du dossier Steam (optionnel)
docs/              Documentation technique
```

### Limitations connues

Voir [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md). En résumé : ~99% du texte est en français. Quelques labels UI courts (1-2 mots) sont utilisés comme clés de binding interne et ne peuvent pas être patchés sans casser le jeu.

## Licence

Le code de la pipeline est sous MIT. Les textes traduits sont une œuvre dérivée d'Esoteric Ebb (© Lykkesalt Studios) et sont distribués à des fins non commerciales sous fair use.
