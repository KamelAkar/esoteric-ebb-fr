# Changelog — Patch FR Esoteric Ebb

## v1.3.5 — 2026-07-22

**Mise à jour majeure** : zones inaccessibles ("scene not found"), crash au chargement, bug de monnaie et bouton pause manette — corrigés ; traduction fortement étendue (menus, création de personnage, carte, glossaire, fiches PNJ, ambiance).

### Correction critique

- Zones « scene not found » corrigées : Jardin des Gobelins, pont et la plupart des portes/transitions sont de nouveau accessibles.
- Crash au chargement de partie corrigé.
- Map qui se coupait au début du jeu corrigée.
- **Bouton pause à la manette réparé** : les fichiers de dialogue étaient reconstruits par un outil défectueux qui abîmait des composants du jeu au passage. Ils repartent désormais des fichiers d'origine, avec seulement les textes français réinjectés. Cela supprime aussi d'éventuels problèmes latents du même type.

### Traduction étendue

- Fichiers de niveau re-traduits proprement (re-sérialisation avec le bon typetree IL2CPP via UnityPy, sans corrompre la structure) : menu principal et menu pause entièrement en français, création de personnage (textes de présentation, classes, stats), noms de zones traduits sur la carte du monde (Antre de Visken, Jardin Gobelin, Croisée du Pilier, etc.).
- Les noms de chargement de scène restent en anglais en interne (champ séparé de l'affichage) → l'affichage est en français ET les scènes chargent.
- Onglet d'inventaire « Consomm. » remis en entier (« Consommables ») ; mois « décembr »/« juil » corrigés en « décembre »/« juillet » ; libellés de repos dé-abrégés.
- 2 dialogues au texte corrompu réparés (Q_Sea, CB_CraniumAnt).
- Bug de monnaie corrigé : les écus/couronnes disparaissaient et n'étaient pas dépensables (texte d'achat barré). Les noms d'objets et de la monnaie servaient de clés internes ; ils restent en anglais pour ne pas casser l'économie et les icônes.
- 433 dialogues cassés réparés (guillemets mal encodés sur les textes à virgule), qui provoquaient l'erreur "error occurred in: Snell" et rendaient des choix non cliquables.
- 573 lignes de dialogue restées en anglais traduites (phrases d'intro, choix, interjections) et synchronisées dans l'Ink que le jeu affiche.
- 643 entrées de glossaire traduites (l'encyclopédie cliquable : sorts, lieux, factions, peuples, concepts du monde), appliquées aussi aux révélations de jets passifs affichées en jeu.
- 194 fiches d'examen de PNJ traduites (les observations révélées quand on examine un personnage).
- 174 observations d'environnement traduites (les textes qui apparaissent en explorant les décors).
- 18 historiques de création de personnage traduits (nom + description).
- Noms de stats traduits sur les badges de jets de dés (Force, Dextérité, Sagesse, Charisme…).
- Réactions du personnage traduites (« Besoin de me reposer avant de faire ça », « Pas les moyens », etc.).

### Autres corrections

- Préfixes de jets de dés qui s'affichaient en clair dans les choix (ex. « ROLL33 wis- ») : 226 doublons supprimés.
- Marqueur technique « <> » qui apparaissait dans certains dialogues : nettoyé.
- Libellés « Retour » et « Annuler » laissés en anglais volontairement : ces mots servent de noms d'actions au système de contrôle, les traduire cassait le bouton pause à la manette.

### Limite connue

- Les catégories du journal (Politics, Geography, etc.) restent en anglais : elles sont codées en dur dans le binaire du jeu et les traduire casse les scripts.
- Les noms d'objets et de la monnaie dans l'inventaire restent en anglais : ils servent de clés internes (comptage de l'argent, icônes, sauvegardes).

## v1.3.3 — 2026-05-26

**Hotfix majeur** : zones inaccessibles ("scene not found"), map coupée, sort Bless cassé.

### Correction critique

- Les patches sur la section `strings` de la metadata (catégories du journal : City/Skills/Geography/History/Language/Politics/Religion/Nature/Literature, le sort Bless, et les repoints Wisdom/Dexterity/Behold/Trifle) renommaient en réalité des noms de **types/classes/méthodes de réflexion .NET**. "History" (42 occurrences) et "Language" (26) à eux seuls corrompaient des dizaines de noms internes, cassant la résolution de scripts et de scènes → "scene not found", map coupée, script Bless manquant.
- Toute la section `strings` revient à l'état vanilla. L'affichage FR des stats reste assuré par les patches stringLiteral (sûrs).
- Effet de bord assumé : les libellés des catégories du journal et quelques noms internes réaffichés en anglais.

## v1.3.2 — 2026-05-24

**Hotfix critique** suite à un report joueur Nexus (AvatarTix8).

### Correction critique

- **L'initiative de combat ne se déclenchait pas** (zombie de l'intro et autres combats) : dialogue qui boucle infiniment au lieu de lancer le combat. Cause identifiée : mon regex de restauration des préfixes de v1.3.1 manquait le préfixe **`IROLL-`** (format différent — pas de nombre après, contrairement à `ROLL16 wis-`). 14 préfixes `IROLL-` et `SPELL <nom>-` restaurés à travers tout le jeu.

Merci à AvatarTix8 pour le report et la suggestion de fix précise.

## v1.3.1 — 2026-05-21

**Mise à jour majeure** : couverture FR poussée à ~99.99% et correction de plusieurs bugs gameplay critiques introduits par les versions précédentes.

### Corrections critiques

- **Préfixe `DC` visible** sur les choix d'intro et tout le jeu : le parseur Ink ne reconnaissait plus les jets de dé. Cause identifiée : un patch metadata sur le littéral "DC". Résolu.
- **Préfixe `ROLL` visible** sur les choix de jet (ex. `ROLL16 wis-...`) : même cause que le bug DC. Résolu.
- **Choix `S` / `F` apparaissant manuellement** après un jet (ex. "Tenter une Prière de Guérison" → 1.S / 2.F) : la synchronisation Ink/Dialogs avait stripé les préfixes de jet de **219 choix** à travers tout le jeu, empêchant le moteur de lancer les dés automatiquement. Restauration complète.
- **Dialogues mixtes FR/EN** (ex. "I have some other questions. Je crois.") : le jeu lit l'Ink JSON en priorité, pas le Dialogs CSV. Sync massive de **~15 400 traductions** depuis le Dialogs vers l'Ink à travers les 12 fichiers `sharedassets*.assets`.

### Traductions nouvelles

- **Intro Lower Lair (LL_*)** intégralement traduite : intro de personnage, dialogue Zombie, tas de pommes, cadavre Sven, sable moustique, manteau Garde-d'Urth, vérification zombie (~800 strings).
- **395 lignes restantes du Dialogs CSV** traduites (le précédent traducteur en avait laissé en anglais ou en mix FR/EN).
- **Notes de session** (résumé "Notes de Session" sur l'écran de chargement) : tous les paragraphes par Chris le développeur, incluant les fins par classe (Azgal/Errant/Party/God-Wizard-King/Appleboy/apolitique).
- **Tiers de difficulté des jets** (badge sur les jets de dé) :
  - Challenging → **Difficile**
  - Daunting → **Pénible**
  - Effortless → **Trivial**
  - Medium → **Moyen**
- **"Journal Updated"** → "Journal mis à jour" (notification HUD).
- **Choix DC/FC de l'intro** non couverts (35 strings : Dick-Ass Roublard, Contrôle, Pour sauver le monde, etc.).
- **2 derniers choix EN de l'intro** ("Class? What class am I?", "I have a very important job to do.").

### Conventions de traduction

- Respect des termes D&D 5e VF officiels : Clerc, Roublard, Magicien, Barde, etc.
- Sorts FR officiels : Communication avec les Morts, Rappel à la Vie, Lumières Dansantes, Compréhension des Langues, etc.
- Tutoiement intime pour voix intérieures et Snell (compagnon gobelin), vouvoiement par défaut pour les autres PNJ.
- Préservation des vulgarités du texte original ("Dick-Ass", "putain", etc.) — pas d'aseptisation.
- Noms propres conservés : Norvik, Tolstad, Snell, Sven, Visken, Viira, Ettir, Pinja, Modissa, etc.

### Connu / non corrigé

- **Badge "DC" sur les jets** : le littéral est utilisé en double-usage (rendu badge + parseur de choix Ink). Le patcher en "DD" casserait le mécanisme de jet. À traiter dans une future MAJ via patches coordonnés metadata + 1000+ choix Ink.

### Installation

Glisser le contenu du ZIP dans le dossier Steam d'Esoteric Ebb, écraser les fichiers existants. Pour désinstaller : Steam > clic droit sur le jeu > Propriétés > Fichiers installés > Vérifier l'intégrité.

---

## v1.2.2 — État précédent

Travail du précédent traducteur basé sur BepInEx + XUnity AutoTranslator (~78 000 lignes du Dialogs CSV traduites). Patch statique drag-and-drop sans framework runtime.
