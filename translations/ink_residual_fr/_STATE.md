# Lignes Ink RÉSIDUELLES anglaises (options conditionnelles + narration) - dans les sharedassets

PATTERN : options de dialogue conditionnelles (.Snell==1-, .BARB/BARD/DRUID/Ettir/Meek==1-, quêtes .Q_*) + narration, laissées EN dans des conteneurs Ink majoritairement FR. 1003 textes distincts / ~7800 mots.

## Fichiers (build_tmp = gitignoré, archivé ici)
- build_tmp/ink_todo_map.json : {texte_affiché_EN: [préfixes de condition]}. Régénérable via build_ink_todo.py.
- build_tmp/ink_fr.json : {texte_affiché_EN: français} accumulé. Archive: translations/ink_residual_fr/ink_fr.json
- Injection : build_tmp/inject_ink_residual.py -> inkbulk (dotnet) sur les 25 sharedassets, esc(prefix+en)->esc(prefix+fr). Backup dans backups/sharedassets_pre_ink/. Déploie live+dist.

## Boucle par tir
1. `python build_tmp/ink_show_remaining.py 50 all` (ou .Snell / .Ettir / .BARB ...) -> @@KEY@@ <json texte> (KEY = index dans sorted(ink_todo_map keys)).
2. Traduire ~40-60 (CONVENTIONS.md + glossaire ; tutoiement pour options adressées à Snell/compagnons/voix intérieure, vouvoiement pour NPC formels ; garder tags <i>/<b>, guillemets « », parenthèses d'action, ESPACE finale si présente). Écrire un script : keys=sorted(json.load(ink_todo_map)); {keys[KEY]: fr} -> merge dans build_tmp/ink_fr.json.
3. cp build_tmp/ink_fr.json translations/ink_residual_fr/ink_fr.json ; commit+push.
4. Quand ink_show_remaining all = 0 -> `python build_tmp/inject_ink_residual.py` (inkbulk, ~1-2 min ; PAS de typetree). Vérifier EN parti. Rebuild ZIP v1.3.6. Commit. Stop cron. PushNotification.

NB : l'injection est idempotente (ré-exécutable). On peut injecter à tout moment pour tester.
