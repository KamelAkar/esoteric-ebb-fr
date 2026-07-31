# État de la traduction des LEVEL FILES (texte hors-dialogue)

Distinct des dialogues Ink (100% faits). Percée validée en jeu 2026-07-31.

## Fichiers de travail (build_tmp = gitignoré, donc archivé aussi dans translations/level_fr/)
- `build_tmp/level_strings_all.json` — extraction brute [level, path_id, field, value] (210447 rec). Régénérable via `build_tmp/extract_level_strings.py` (~30 min, background).
- `build_tmp/level_todo_map.json` — {english: [[level,pid,field],...]} des 741 chaînes EN affichables sur champs SÛRS. Archivé: translations/level_fr/_todo_map.json
- `build_tmp/level_translations.json` — {english: french} accumulé. Archivé: translations/level_fr/_master_translations.json
- Champs SÛRS traités: .Description .description .quickResponse .descText .infoText .varMods[].ModDescription .textNoteOnReveal .SelectInfoDesc .InfoBoxText .DisplayName .subAreaName .SubDisplayName .AreaSubName .IdeaDesc
- Champs RISQUÉS exclus (noms=clés, cf mémoire localization-data-traps): .itemName .Nickname .GlossaryTerms[].Term  → NE PAS traduire sans test isolé.

## Avancement
- Lot 1 (105) = champs système (sorts/stats/infos/mods/notes/zones). FAIT + commité f3960d5.
- RESTANT ≈ 636 : surtout .Description (442 : nav, journal de quête, indices), .description (141 : objets), .quickResponse (53 : barks PNJ).

## Continuer une traduction (chaque tir de cron)
1. `python build_tmp/level_show_remaining.py .Description 60`  (ou .description / .quickResponse / all)
   → liste `@@KEY@@[field] valeur` (KEY = index dans list(level_todo_map.items())).
2. Traduire, puis écrire un script qui construit {KEY:french} et met à jour level_translations.json :
   items=list(json.load(open('build_tmp/level_todo_map.json')).items()); pour chaque KEY: english=items[KEY][0]; trans[english]=french.
   Respecter CONVENTIONS.md + glossaire (lichhouse gardé « la lichhouse », les Fils, Reflux, Cité d'En Bas, Errant, couronnes, Dés de Vie, DD, termes D&D 5e VF ; pieds conservés). Tags <i>/<b>/<shake>/<size> et \n intacts.
3. cp build_tmp/level_translations.json translations/level_fr/_master_translations.json ; commit+push (translations/ seulement, dist/backups gitignorés).

## Injecter (quand TOUT traduit, ou par level au fur et à mesure)
`python build_tmp/inject_all_levels.py [indices]`  (défaut: tous les levels concernés)
- Charge le level LIVE, remplace récursivement toute string == english (dans level_translations.json) par le french, RESTREINT aux path_id du todo map. Backup dans backups/levels_pretexte/. Déploie live + dist.
- Lent (~2 min chargement gen + par level). Une seule injection lourde à la fois.
- Vérifier après: 0 anglais résiduel sur les valeurs traduites + type counts.

## Fin
Re-scan, rebuild ZIP v1.3.6 (tools/05_package_zip.py), commit, CronDelete du job de trad level, PushNotification.
