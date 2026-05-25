# Esoteric Ebb — Traduction Française

Contenu prêt à copier-coller dans la page Nexus.

## Titre court (≤ 60 chars)

```
Esoteric Ebb - Traduction Française (FR)
```

## Description courte (≤ 200 chars, Summary Nexus)

```
Patch drag-and-drop qui traduit Esoteric Ebb en français. ~99% du texte
narratif, dialogues, items, sorts, UI. Aucun framework requis (pas de
BepInEx).
```

## Description longue (DESCRIPTION Nexus)

```
[size=5][b]Esoteric Ebb en Français[/b][/size]

Patch de traduction française pour [url=https://store.steampowered.com/app/2647560/]Esoteric Ebb[/url], le RPG narratif inspiré par Donjons & Dragons 5e.

[size=4][b]Caractéristiques[/b][/size]

[list]
[*][b]~99% du jeu traduit[/b] — narratif, dialogues, items, sorts, glossaire, journal, quêtes
[*][b]Drag-and-drop pur[/b] — aucun framework (BepInEx, XUnity, etc.) requis
[*][b]Respect terminologie D&D 5e VF[/b] — Clerc, Sagesse, Dés de Vie, DD au lieu de DC, etc.
[*][b]Vouvoiement par défaut[/b] / tutoiement intime pour les voix intérieures et Snell
[*][b]Style soutenu légèrement littéraire[/b] avec archaïsmes occasionnels
[*][b]Préservation du registre original[/b] — humour mordant et vulgarités conservés
[/list]

[size=4][b]Installation[/b][/size]

[list=1]
[*]Steam > Bibliothèque > Esoteric Ebb > Clic droit > Propriétés > Fichiers installés > Parcourir...
[*]Extraire tout le contenu du ZIP dans le dossier, en remplaçant les fichiers
[*]Lancer le jeu via Steam
[/list]

[b]Désinstallation[/b] : Steam > Vérifier l'intégrité des fichiers (restaure l'anglais).

[size=4][b]Nouveautés v1.3.2[/b][/size]

[list]
[*][b]Hotfix critique[/b] : l'initiative de combat ne se déclenchait pas (zombie de l'intro + autres combats), le dialogue bouclait à l'infini. Mon regex de restauration des préfixes en v1.3.1 manquait le format `IROLL-` (initiative). 14 préfixes IROLL-/SPELL restaurés. Merci à AvatarTix8 pour le report.
[/list]

[size=4][b]Nouveautés v1.3.1[/b][/size]

[list]
[*][b]Fix critique[/b] : préfixe "DC" visible sur les choix de jet (intro et tout le jeu) — parseur du jeu cassé par une regression metadata. Résolu.
[*][b]Fix critique[/b] : préfixe "ROLL" visible (ROLL16 wis-, etc.) sur les choix de jet — même cause. Résolu.
[*][b]Fix critique[/b] : choix manuels "S" / "F" qui apparaissaient après un jet (ex. Tenter une Prière de Guérison) — 219 préfixes ROLL/DC/FC restaurés à travers tout le jeu.
[*][b]Fix critique[/b] : dialogues mixtes FR/EN (ex. "I have some other questions. Je crois.") — synchronisation massive de ~15 400 traductions depuis le Dialogs CSV vers l'Ink JSON utilisé par le moteur.
[*]Intro Lower Lair intégralement traduite : intro de personnage, Zombie, Tas de pommes, Cadavre Sven, Sable Moustique, Manteau Garde-d'Urth, vérification zombie (~800 strings)
[*]395 lignes restantes du Dialogs CSV traduites (laissées en EN ou mix par les versions précédentes)
[*]Notes de session (résumé "Notes de Session" sur l'écran de chargement) intégralement traduites
[*]Tiers de difficulté des jets : Challenging → Difficile, Daunting → Pénible, Effortless → Trivial, Medium → Moyen
[*]"Journal Updated" → "Journal mis à jour"
[*]Choix DC/FC de l'intro non couverts (35 strings : Dick-Ass Roublard, Contrôle, Pour sauver le monde, etc.)
[/list]

[size=4][b]Nouveautés v1.3.0[/b][/size]

[list]
[*]Onglets inventaire (Tout / Casques / Armement / Livres / Clés / Cléricaux / Babioles / Consommables / etc.)
[*]Verbes d'interaction (Voir / Parler / Piquer / Examiner / Ouvrir / Lire / Toucher / Partir)
[*]HUD bas-droit : "Jour 1" au lieu de "Day 1"
[*]Sections du journal traduites (Cite / Talent / Gens / Mystères / Régions / Annales / Langue / Pouvoir / Religion / Nature / Romans)
[*]Items courants : Bottes, Manteau, Fiole, Dague, Sac sans Fond, Ceinture des Nains, Marteau Adamantin, Manteau du Croisé, etc.
[*]Devise : Crowns → Écus
[*]Tooltips Grimoire (Sorts Préparés / Sorts Collectés / Difficulté de Sort)
[*]Popups Stockage Profond (bourse) traduits
[*]Fix du bug "one single time" dans Quest_34
[*]DC → DD partout (terminologie D&D 5e VF officielle)
[*]Factions : Errant, Apolitique, Agrarien, Arcaniste, Azgaliste
[*]Verbes UI : Retour, Annuler, Lancer, Cacher, Suivant, Non, Pousser
[*]Time-of-day : Matin / Tantôt / Soir / Nuit
[*]Et beaucoup plus...
[/list]

[size=4][b]Limitations connues[/b][/size]

Quelques labels restent en anglais car ils servent de clés internes au code C# :

[list]
[*]"Inventory" (onglet supérieur) — patcher fait disparaître les slots
[*]Noms de sorts dans le Grimoire (Cure Wounds, Mage Hand, etc.) — patcher casse le compteur
[*]Sections "DIALOGS / VISUALS / AUDIO" du menu Options — pas dans les fichiers patchables
[*]"Lower Lair" et autres noms de scènes — utilisés par le code pour charger les scènes
[*]Format date du journal ("1st Day, 8h 3m") — concaténation runtime non patchable
[/list]

[size=4][b]Crédits[/b][/size]

Traduction par Ravnow. N'hésitez pas à signaler tout texte non traduit, faute de frappe ou tournure maladroite — traduction faite par un Français pour les Français.

Esoteric Ebb © Lykkesalt Studios. Traduction distribuée à but non lucratif sous fair use.
```

## Catégories Nexus

- **Primary** : Translations / Languages
- **Secondary** : User Interface

## Tags

```
translation, french, francais, fr, traduction, ui, dialogue, no-bepinex
```

## Description du fichier (champ "File description" lors de l'upload)

Texte court, plat. À coller dans le champ "Description" du formulaire d'upload du ZIP.

```
Patch FR complet (drag-and-drop, sans BepInEx). Glissez le contenu du ZIP dans le dossier Steam d'Esoteric Ebb. Pour désinstaller : Steam > Vérifier l'intégrité des fichiers.
```

## Changelogs (onglet LOGS sur Nexus)

RÈGLES STRICTES Nexus changelog :
- Chaque ligne devient un bullet automatiquement (pas besoin de mettre `-` ou `*`)
- Aucun balisage interprété (ni markdown ni BBCode)
- Pas de saut de ligne au milieu d'une idée — sinon ça forme une grosse ligne
- Une idée courte par ligne

À CHAQUE nouvelle version, ajouter une nouvelle entrée changelog avec le bloc texte correspondant. Coller TEL QUEL (sans les triples backticks).

### v1.3.2

```
Hotfix critique : l'initiative de combat ne se déclenchait pas (zombie de l'intro et autres combats), dialogue en boucle infinie.
Cause : mon regex de restauration des préfixes en v1.3.1 manquait le format IROLL- (initiative, sans nombre contrairement à ROLL16 wis-).
14 préfixes IROLL- et SPELL restaurés dans tout le jeu.
Merci à AvatarTix8 pour le report et la suggestion de fix précise.
```

### v1.3.1

```
Mise à jour majeure : couverture FR poussée à 99,99% et plusieurs bugs critiques corrigés.
Fix critique : préfixe DC visible sur les choix de jet (parseur Ink cassé). Résolu.
Fix critique : préfixe ROLL visible sur les choix de jet (ex. ROLL16 wis-...). Même cause. Résolu.
Fix critique : choix manuels S/F après un jet (ex. Tenter une Prière de Guérison). 219 préfixes ROLL/DC/FC restaurés.
Fix critique : dialogues mixtes FR/EN dans tout le jeu (ex. "I have some other questions. Je crois."). 15 400 traductions Ink synchronisées depuis le Dialogs CSV.
Intro Lower Lair intégralement traduite (Zombie, Tas de pommes, Cadavre Sven, Sable Moustique, Manteau Garde-d'Urth, vérification zombie). Environ 800 strings.
395 lignes restantes du Dialogs CSV traduites (EN/mix du précédent traducteur).
Notes de session (résumé sur l'écran de chargement) intégralement traduites.
Tiers de difficulté : Challenging devient Difficile, Daunting devient Pénible, Effortless devient Trivial, Medium devient Moyen.
"Journal Updated" devient "Journal mis à jour".
35 choix DC/FC de l'intro non couverts (Dick-Ass Roublard, Contrôle, Pour sauver le monde, etc.).
Connu : badge DC sur les jets reste en DC (le littéral est en double-usage avec le parseur de choix, le changer casserait les jets).
```

### v1.3.0

```
Onglets inventaire entièrement traduits (Tout, Casques, Armement, Livres, Clés, Cléricaux, Babioles, Consommables).
Verbes d'interaction (Voir, Parler, Piquer, Examiner, Ouvrir, Lire, Toucher, Partir).
HUD : Jour 1 au lieu de Day 1.
Sections du journal (Cite, Talent, Gens, Mystères, Régions, Annales, Langue, Pouvoir, Religion, Nature, Romans).
Items : Bottes, Manteau, Fiole, Dague, Sac sans Fond, Ceinture des Nains, Marteau Adamantin, Manteau du Croisé.
Devise : Crowns devient Écus.
Tooltips Grimoire (Sorts Préparés, Sorts Collectés, Difficulté de Sort).
Popups Stockage Profond (bourse) traduits.
Fix du bug "one single time" dans Quest_34.
DC devient DD partout (terminologie D&D 5e VF officielle).
Factions : Errant, Apolitique, Agrarien, Arcaniste, Azgaliste.
Verbes UI : Retour, Annuler, Lancer, Cacher, Suivant, Non, Pousser.
Time-of-day : Matin, Tantôt, Soir, Nuit.
Pomme Jardin pour l'objet item.
```

### v1.2.2 (état précédent, déjà publié)

```
Drag-and-drop pur, BepInEx désactivé.
Stats FR, dialogues Ink traduits, glossaire complet.
DD : Succès / Échec, XP gagnée, dates mars/avril/etc.
```
```

## Screenshots à fournir (TODO)

1. Menu principal avec "Nouvelle Partie / Charger / Options / Crédits / Quitter"
2. Save preview avec "Jour 01 - 08:10"
3. Inventaire (TOUT / CASQUES / ARMEMENT / LIVRES / CLÉS) — page char avec stats FR
4. Grimoire avec tooltip Sorts Préparés en FR
5. Journal section "CITE" avec entrée Urth + tag "Religion, City" (ou la version FR)
6. Dialogue avec zombie : "« Salutations, citoyenne. »" + check DD 11 : Succès
7. Pickup popup "POMME JARDIN" ou "ÉCUS"
8. Quête "SEMAINE ÉLECTORALE" avec "une unique fois"
