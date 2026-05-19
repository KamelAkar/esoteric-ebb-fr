# Backups

Ce dossier reçoit les fichiers originaux du jeu **avant le premier patch**, pour permettre un rollback complet.

## Contenu attendu

Après la première exécution des outils :

- `global-metadata.dat.backup` — original IL2CPP metadata
- `level{0..N}.bak` — niveaux originaux
- `sharedassets{N}.assets.bak` — assets partagés originaux

Ces fichiers sont **gitignorés** car volumineux et soumis au copyright du jeu.

## Restauration

Pour revenir à la version vanilla anglaise :

```bash
# Restore metadata
cp backups/global-metadata.dat "C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat"

# Restore levels (one by one)
for i in {0..24}; do
    cp "backups/level$i.bak" "C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\level$i"
done
```

Ou plus simple : **Steam → clic droit Esoteric Ebb → Propriétés → Fichiers installés → Vérifier l'intégrité**.
