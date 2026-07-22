# Changelogs Nexus (onglet LOGS)

Fichier de référence pour la zone **LOGS** de la page Nexus.

## Règles strictes du format Nexus LOGS

- Chaque ligne devient automatiquement un bullet — **ne pas** mettre `-` ni `*` en début de ligne
- **Aucun balisage interprété** : ni markdown, ni BBCode (le `[b]` et le `**` s'affichent en brut)
- **Une idée courte par ligne** — pas de saut de ligne au milieu d'une phrase, sinon Nexus fusionne tout
- Coller le bloc **tel quel**, sans les triples backticks

À chaque nouvelle version : ajouter une entrée en haut de ce fichier, puis créer le changelog correspondant sur Nexus.

---

## v1.3.5

```
Zones "scene not found" corrigées : Jardin des Gobelins, pont et la plupart des portes de nouveau accessibles.
Crash au chargement de partie corrigé.
Map coupée au début du jeu corrigée.
Bouton pause à la manette réparé.
Bug de monnaie corrigé : les écus ne disparaissent plus et sont de nouveau dépensables chez les marchands.
433 dialogues cassés réparés, dont l'erreur "error occurred in: Snell" qui empêchait Snell de rejoindre le groupe.
Menu principal et menu pause entièrement traduits.
Création de personnage traduite : présentation, classes, statistiques, 18 historiques.
Noms de zones traduits sur la carte du monde.
643 entrées de glossaire traduites : encyclopédie cliquable et révélations de jets passifs.
194 fiches d'examen de PNJ traduites.
174 observations d'environnement traduites.
573 lignes de dialogue restées en anglais traduites : intro, choix, interjections.
Noms de statistiques traduits sur les badges de jets de dés.
Préfixes de jets qui s'affichaient en clair supprimés, par exemple ROLL33 wis-.
Marqueur technique "<>" nettoyé dans les dialogues.
Onglet d'inventaire "Consommables" et libellés divers remis en mots complets.
Limite connue : les catégories du journal restent en anglais, elles sont codées en dur dans le jeu.
Limite connue : les noms d'objets et de la monnaie dans l'inventaire restent en anglais, ils servent de clés internes.
Limite connue : les libellés Back et Cancel restent en anglais, les traduire casse le bouton pause à la manette.
```

> Note : la v1.3.4 n'a jamais été publiée sur Nexus — son contenu est fusionné dans la v1.3.5 ci-dessus.

---

## v1.3.3

```
Fix majeur : certaines zones étaient inaccessibles (scene not found), la map était coupée, et le sort Bless était cassé.
Cause : des patches sur les noms de types internes du jeu (catégories du journal, Bless) corrompaient la résolution des scripts et des scènes.
Ces noms reviennent à l'état d'origine. L'affichage des stats reste en français.
Effet de bord : quelques libellés de catégories du journal et certains noms internes réaffichés en anglais (compromis nécessaire pour ne plus casser les scènes).
```

---

## v1.3.2

```
Fix : initiative de combat qui ne se déclenchait pas (zombie de l'intro et autres combats), dialogue en boucle infinie.
14 préfixes IROLL- et SPELL restaurés dans tout le jeu.
```

---

## v1.3.1

```
Fix : préfixe DC visible sur les choix de jet (parseur Ink cassé).
Fix : préfixe ROLL visible sur les choix de jet (ex. ROLL16 wis-...).
Fix : choix manuels S/F après un jet. 219 préfixes ROLL/DC/FC restaurés.
Fix : dialogues mixtes FR/EN dans tout le jeu. 15 400 traductions Ink synchronisées.
Intro Lower Lair intégralement traduite (Zombie, Tas de pommes, Cadavre Sven, Sable Moustique, Manteau Garde-d'Urth, vérification zombie). 800 strings.
395 lignes restantes du Dialogs CSV traduites.
Notes de session (résumé écran de chargement) intégralement traduites.
Tiers de difficulté : Challenging devient Difficile, Daunting devient Pénible, Effortless devient Trivial, Medium devient Moyen.
Journal Updated devient Journal mis à jour.
35 choix DC/FC de l'intro traduits (Dick-Ass Roublard, Contrôle, Pour sauver le monde, etc.).
```

---

## v1.3.0

```
Onglets inventaire entièrement traduits (Tout, Casques, Armement, Livres, Clés, Cléricaux, Babioles, Consommables).
Verbes d'interaction (Voir, Parler, Piquer, Examiner, Ouvrir, Lire, Toucher, Partir).
HUD : Jour 1 au lieu de Day 1.
Sections du journal (Cite, Talent, Gens, Mystères, Régions, Annales, Langue, Pouvoir, Religion, Nature, Romans).
Items : Bottes, Manteau, Fiole, Dague, Sac sans Fond, Ceinture des Nains, Marteau Adamantin, Manteau du Croisé.
Devise : Crowns devient Écus.
Tooltips Grimoire (Sorts Préparés, Sorts Collectés, Difficulté de Sort).
Popups Stockage Profond (bourse) traduits.
Fix du bug one single time dans Quest_34.
DC devient DD partout.
Factions : Errant, Apolitique, Agrarien, Arcaniste, Azgaliste.
Verbes UI : Retour, Annuler, Lancer, Cacher, Suivant, Non, Pousser.
Time-of-day : Matin, Tantôt, Soir, Nuit.
Pomme Jardin pour l'objet item.
```

---

## v1.2.2 (état précédent, déjà publié)

```
Drag-and-drop pur, BepInEx désactivé.
Stats FR, dialogues Ink traduits, glossaire complet.
DD : Succès / Échec, XP gagnée, dates mars/avril/etc.
```
