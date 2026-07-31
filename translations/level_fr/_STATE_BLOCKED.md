# État — traduction des chaînes BLOQUÉES des level files (feats, journal de quête, bios PNJ)

Débloqué via ÉDITION BRUTE (pas de typetree) — VALIDÉ EN JEU 2026-07-31 (scènes chargent, pas de crash).
Voir mémoire [[reference-level-typetree-failure]]. Les 741 champs lisibles sont déjà faits (voir [[reference-level-monobehaviour-fields]]).

## Fichiers
- `translations/level_fr/_BLOCKED_typetree_517.json` — les 517 chaînes EN à traduire (source, triée = ordre des KEY).
- `build_tmp/blocked_fr.json` — {english: french} accumulé. Archive: `translations/level_fr/_blocked_fr.json`.
- Injection: `build_tmp/inject_blocked_raw.py` — remplace les chaînes Unity alignées dans le blob brut de chaque objet MonoBehaviour, `set_raw_data` + `env.save` (recalcule offsets → FR plus long OK, PAS de typetree). Backup: `backups/levels_BLOCKED_pre/`. Déploie live+dist.

## Méthode par tir de cron
1. `python build_tmp/blocked_show_remaining.py 40 all` (ou feat/quest/bio) → liste `@@KEY@@ <json EN>` (KEY = index dans sorted(_BLOCKED_...517)).
2. Traduire un lot (~30-60) en respectant CONVENTIONS.md + glossaire (Fils, Rappel à la Vie, Communication avec les Morts, Errant, Coinlord, Cité d'En Bas, lichhouse gardé, Guenaude, couronnes, Reflux, DON=feat, classes D&D 5e VF : CLERC/ROUBLARD/MAGICIEN/BARBARE/BARDE/DRUIDE/GUERRIER/OCCULTISTE/ENSORCELEUR/RÔDEUR/PALADIN/MOINE, stats FOR/DEX/CON/INT/SAG/CHA, Contemplation=Behold). Tags <i>/<b> et \n intacts, noms propres gardés, vulgarités préservées, tutoiement (journal/feats = voix joueur).
   Écrire un script qui, via `b=sorted(json.load(_BLOCKED_...517))`, mappe {b[KEY]: french} dans build_tmp/blocked_fr.json.
3. cp build_tmp/blocked_fr.json translations/level_fr/_blocked_fr.json ; commit+push.
4. Quand blocked_show_remaining.py all = 0 → `python build_tmp/inject_blocked_raw.py` (rapide, ~5-8 min, pas de gen typetree ; garde mtime/process). Vérifier 0 EN résiduel. Rebuild ZIP v1.3.6. Commit. Stop cron. PushNotification.

## NE PAS toucher
Libellés mono-mots de la fiche perso (Strength/Dexterity/Cleric/Stats) = metadata/STRSEC + clés de lookup → dangereux (casse scripts/saves). Hors scope de ce lot.
