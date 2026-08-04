# Contribuer

Ce dépôt contient l'outillage de traduction, pas les fichiers du jeu. Rien de ce
qui vient de l'installation d'Esoteric Ebb ne doit y être commité.

## Avant de proposer un changement

- La chaîne doit rester rejouable de bout en bout, dans l'ordre des scripts
  numérotés de `tools/`. Voir `docs/PIPELINE.md`.
- Un patch en place (`in-place`) dépend de la **longueur en octets** de la chaîne
  française. Ne jamais modifier une chaîne traduite sans revérifier son slot.
- Toute limite connue va dans `docs/KNOWN_LIMITATIONS.md`, avec la raison
  technique. Les contournements non documentés se reperdent.
- Les changements visibles par le joueur passent par `docs/CHANGELOG.md`.

## Conventions

Les commits sont signés par le seul propriétaire du dépôt. Ne pas ajouter de
ligne de co-auteur automatique ni de signature d'outil aux messages de commit,
aux pull requests ou aux notes de version.

Typographie : le tiret cadratin (U+2014) et le tiret demi-cadratin (U+2013) ne
sont pas utilisés dans la documentation, les commentaires ni les messages du
projet. Utiliser une virgule, un deux-points, des parenthèses ou une phrase
séparée. Pour une plage de valeurs, un trait d'union ou le mot « à ».

Deux zones échappent volontairement à cette règle, et le script de vérification
les ignore :

- `translations/` et `backups/` : c'est du dialogue de jeu. En français, le
  tiret cadratin y est la ponctuation normale de la réplique.
- les chaînes de caractères de `tools/` : ce sont des textes traduits injectés
  dans les assets Unity, dont la longueur en octets est porteuse. Seuls les
  commentaires y sont vérifiés.

`python tools/check_dashes.py` applique exactement cette règle, en local via le
hook de pre-commit et dans la CI.
