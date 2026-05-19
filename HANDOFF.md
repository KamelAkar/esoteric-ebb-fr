# HANDOFF — Passation à un nouveau Claude avec computer-use

**À toi qui lis ceci** : tu reprends un projet de traduction française pour le jeu Steam **Esoteric Ebb** (Unity 6 IL2CPP). Tu as accès au MCP computer-use, donc tu peux **lancer le jeu, naviguer, prendre des screenshots, et fermer le jeu toi-même**. L'utilisateur ne veut plus le faire manuellement.

## Lis d'abord (dans cet ordre)

1. **`CLAUDE.md`** — contexte général, règles critiques, approches échouées
2. **`README.md`** — vue d'ensemble
3. **`docs/PIPELINE.md`** — workflow technique
4. **`docs/KNOWN_LIMITATIONS.md`** — labels qui résistent et pourquoi

## Ton autonomie

Tu peux et tu DOIS :
- Lancer Steam et le jeu via computer-use (pas demander à l'humain)
- Prendre des screenshots et identifier visuellement ce qui est traduit / ne l'est pas
- Éditer les fichiers TSV de traduction
- Exécuter les scripts Python de la pipeline
- Fermer complètement le jeu entre tests (Steam → Quitter, PAS retour menu)
- Restaurer un backup si tu casses quelque chose (`backups/global-metadata.dat`)

Tu NE DOIS PAS :
- Demander à l'utilisateur de "relancer le jeu" — fais-le toi-même
- Modifier des fichiers que tu n'as pas backupés
- Réactiver BepInEx (déjà testé, instable sur Unity 6, abandonné)
- Patcher des chaînes mono-mot dans la metadata sans test isolé (casse les saves)

## Chemins critiques

```
Jeu Steam       : C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\
Metadata cible  : ...\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat
Repo projet     : C:\Users\Ravnow\Documents\esoteric-ebb-fr-clone\ (ou clone du repo)
Backup metadata : backups/global-metadata.dat (à créer si absent — voir étape ci-dessous)
```

## Lancer / fermer le jeu via computer-use

**Lancer** :
1. Ouvre Steam (Win+R → `steam://run/2647560` ou clic sur Steam puis Bibliothèque → Esoteric Ebb → Jouer)
2. Attends ~10-15 secondes le chargement (écran titre Esoteric Ebb visible)
3. Pour reprendre une partie : clic sur "Continuer" sur l'écran d'accueil

**Fermer COMPLÈTEMENT** (critique entre tests) :
1. Si en jeu : Échap → Quitter au menu principal
2. Sur l'écran principal : alt+F4 ou clic croix
3. **Vérifier** que le process Esoteric Ebb.exe n'existe plus avant relancer
   - Si nécessaire : `taskkill /F /IM "Esoteric Ebb.exe"` via Bash

La metadata IL2CPP est chargée **une seule fois au démarrage du process**. Sans full quit, tes patches n'ont aucun effet.

## Premier launch (vérification de l'état actuel)

Avant de modifier quoi que ce soit, lance le jeu et vérifie ce qui est déjà traduit. Référence-toi à `docs/KNOWN_LIMITATIONS.md` pour la liste détaillée.

### Checklist de vérification visuelle

Charge un autosave (clic Continuer) et navigue dans :

| Action                              | Attendu                                            | Si pas le cas                       |
|-------------------------------------|----------------------------------------------------|-------------------------------------|
| Menu principal — bouton Continuer   | "Continuer" + "Notes de Session" body en français | Patch metadata pas appliqué         |
| Char panel (touche I ou onglet)     | Force/Dextérité/Constitution/Intelligence/Sagesse/Charisme | STRSEC repoint pas appliqué |
| Faire un check de DC                | "Charisme DD 15 : Succès" (ou Échec)              | substring patches manquants         |
| Gagner XP (action quelconque)       | "XP gagnée : +5xp !"                              | idx 6136 / 1926 pas patchés         |
| Onglet inventaire — Don vide        | "[Don vide]" et pas "[Empty Feat Slot]"           | idx 13527 pas patché                |
| Quest Tracker (les barres à droite) | "Errant" / "Apolitique" / etc.                    | faction patches pas appliqués       |

### Labels qui DOIVENT rester en anglais (limitations connues)

Si tu vois ça en anglais, **NE PAS** essayer de patcher (déjà testé, casse le jeu) :
- `Inventory` (onglet) — STRSEC repoint freeze l'UI
- `Helms`, `Weapons`, `Food`, `Tools`, `Texts`, `Spells`, `Cantrips` (onglets inventaire) — source d'affichage non trouvée
- `Day 1` titre + HUD bas-droit — casse save preview
- `Lv 1 Cleric` chip + class names — casse save preview
- `Prepared Spells` / `Collected Spells` (tooltip body) — binding key

Pas de panique si tu les vois en anglais : c'est l'état actuel accepté.

## Si quelque chose est cassé après ton patch

Symptômes de patch qui casse :
- Jeu refuse de charger une save → metadata patché un truc utilisé comme clé de save
- UI inventaire/spellbook gelée → STRSEC repoint sur un nom de classe Unity
- "X" littéraux à la place de chiffres dans le spellbook → patch d'une clé de binding
- Menu principal affiche "Clerc de Niveau X / Jour XX:XX" placeholders → patch metadata trop large

**Restauration immédiate** :
```bash
cp backups/global-metadata.dat "C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\il2cpp_data\Metadata\global-metadata.dat"
```

Si tu as cassé un level file :
```bash
cp backups/level_X.bak "C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data\level_X"
```

## Tâches prioritaires (par ordre d'importance)

### 1. Verify current state

Lance le jeu, prends 5-10 screenshots du HUD, inventaire, journal, quest tracker, dialogue check de DC. Confirme que l'état décrit dans `KNOWN_LIMITATIONS.md` correspond à la réalité observée. Mets à jour le fichier si nécessaire.

### 2. Tenter de débloquer les UI tabs (Helms/Spells/Food/etc.) via `dotnet-deploy.exe`

Le tool C# `tools/dotnet-deploy/` utilise AssetsTools.NET qui **comprend les types Unity**. Contrairement aux scripts byte-level, il sait distinguer :
- `m_text` d'un `TextMeshProUGUI` (= un label affiché — safe à patcher)
- `m_Name` d'un `GameObject` (= identifiant — NE PAS patcher)

Workflow :
1. Build : `cd tools/dotnet-deploy && dotnet build -c Release`
2. Le mode `tmptext` patche m_text de TMP par valeur. Tester sur UNE chaîne d'abord :
   ```bash
   dotnet-deploy tmptext "$STEAM/Esoteric Ebb_Data/level1" "Helms" "Casques"
   ```
3. Lance le jeu, vérifie qu'aucun GameObject n'a été cassé (les scènes chargent normalement)
4. Si OK, étendre à : Weapons, Food, Tools, Texts, Spells, Cantrips, etc.

### 3. Packaging v1.0 Nexus

Une fois le maximum traduit, créer `tools/05_package_zip.py` qui :
1. Copie `Esoteric Ebb_Data/il2cpp_data/Metadata/global-metadata.dat` + tous les `.assets` patchés + `level*` patchés vers `dist/EsotericEbb-FR-Patch-v1.0/Esoteric Ebb_Data/`
2. Écrit un `LISEZ_MOI.txt` avec les 3 étapes d'install
3. Zippe → `dist/EsotericEbb-FR-Patch-v1.0.zip`

Pas besoin d'inclure BepInEx ou dotnet — drag-and-drop pur.

### 4. (Bonus) Fixer "one single time" dans Quest_34

Le Quest 34 (Conflit de Classe) a un template français qui dépend du runtime substituant `$WIZARD` par "one single time" (string anglaise hardcodée). Solution : réécrire les templates `source-data/ui-french/QuestPoints.csv` pour ne plus utiliser `$WIZARD/$CLERIC/etc.` au milieu de la phrase. Re-patcher `resources.assets` avec le mode `textasset` de `dotnet-deploy`.

## Communication avec l'utilisateur

L'utilisateur est **francophone** et préfère :
- Réponses courtes et factuelles
- Pas de jargon technique excessif
- Screenshots des résultats (pas juste "ça marche")

Quand tu lui rends compte d'un test :
- "✓ Charisme DD 15 : Succès affiché" + screenshot
- "✗ Helms toujours visible dans l'inventaire" + screenshot zoomé
- "→ Je tente le mode tmptext de dotnet-deploy ensuite"

## Git workflow

Le repo distant est sur https://github.com/KamelAkar/esoteric-ebb-fr.

- Branche main = état stable
- Commit après chaque correction validée par l'utilisateur (test visuel OK)
- Format de commit message :
  ```
  Concise summary
  
  Details if needed.
  
  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
  ```
- Push uniquement quand l'utilisateur le demande explicitement

## Si l'utilisateur dit "test toi-même"

C'est EXACTEMENT pour ça que tu as computer-use. Tu :
1. Sauvegardes ton travail (commit local si besoin)
2. Lances le jeu via Steam
3. Charge le dernier autosave
4. Navigues vers la zone à tester (inventaire / dialogue / etc.)
5. Prends des screenshots
6. Ferme le jeu COMPLÈTEMENT
7. Rapportes avec les screenshots

Ne JAMAIS dire "peux-tu relancer le jeu et vérifier" — c'est ton boulot maintenant.

---

Bonne continuation. Le projet est à ~99% traduit, les 1% restants sont du polish optionnel. Si l'utilisateur préfère packager v1.0 tel quel et publier sur Nexus, c'est aussi une réponse valide.
