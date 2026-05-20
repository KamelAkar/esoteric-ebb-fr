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

Traduction par la communauté FR. Source : [url=https://github.com/KamelAkar/esoteric-ebb-fr]GitHub esoteric-ebb-fr[/url]

Esoteric Ebb © Lykkesalt Studios. Traduction distribuée à but non lucratif sous fair use.
```

## Catégories Nexus

- **Primary** : Translations / Languages
- **Secondary** : User Interface

## Tags

```
translation, french, francais, fr, traduction, ui, dialogue, no-bepinex
```

## Changelog v1.3.0

```
v1.3.0 (2026-05-20)
- Onglets inventaire entièrement traduits (Tout/Casques/Armement/Livres/Clés/etc.)
- Verbes d'interaction (Voir/Parler/Piquer/Examiner/Ouvrir/Lire/Toucher/Partir)
- HUD : Jour 1 au lieu de Day 1
- Sections du journal (Cite/Talent/Gens/Mystères/Régions/Annales/Langue/Pouvoir/Religion/Nature/Romans)
- Items : Bottes, Manteau, Fiole, Dague, Sac sans Fond, Ceinture des Nains, etc.
- Devise : Crowns → Écus
- Tooltips Grimoire (3 hovers) traduits
- Popups Stockage Profond (bourse)
- Fix bug "one single time" dans Quest_34
- DC → DD partout
- Factions Agrarien/Arcaniste/Azgaliste
- Verbes UI (Retour/Annuler/Cacher/Suivant/etc.)
- Time-of-day (Matin/Tantôt/Soir/Nuit)
- Pomme Jardin pour l'objet item

v1.2.2 (état précédent — déjà publié)
- Drag-and-drop pur, BepInEx désactivé
- Stats FR, dialogues Ink traduits, glossaire complet
- DD : Succès / Échec, XP gagnée, dates mars/avril/etc.
- etc.
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
