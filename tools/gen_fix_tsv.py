"""Generate fix TSV adding trailing space after each FR choice."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

# (asset, current_text, fr_text_to_have)  -- the replace will be fr_text + " "
entries = [
    ("LL_Intro", "DC10 wis-...Le salon de thé ?"),
    ("LL_Intro", "DC10 wis-...Un salon de thé a explosé ?"),
    ("LL_Intro", "DC11 int-« <i>Je</i> devrais être aux commandes, en tant que dieu-roi mage-seigneur. »"),
    ("LL_Intro", "DC12 dex-« Je suis un petit roublard fourbe. »"),
    ("LL_Intro", "DC12 str-<i>Le</i> Clerc ? J'aime ça."),
    ("LL_Intro", "DC12 wis-« Clerc. »"),
    ("LL_Intro", "DC13 con-Je ne veux pas être mort."),
    ("LL_Intro", "DC13 con-Rédemption ? Attendez, qu'ai-je fait ?"),
    ("LL_Intro", "DC13 dex-« Pour sortir des ténèbres. »"),
    ("LL_Intro", "DC13 wis-« Je suis bel et bien un clerc. »"),
    ("LL_Intro", "DC14 int-« Je suis un foutu magicien. »"),
    ("LL_Intro", "DC14 int-« Ragn Hemlin. »"),
    ("LL_Intro", "DC14 str-Un héros ? Moi ?"),
    ("LL_Intro", "DC14 str-« Pour sauver le monde. »"),
    ("LL_Intro", "DC14 wis-Pas de retour possible ? Ça n'augure rien de bon."),
    ("LL_Intro", "DC15 dex-...« Dick-Ass » ?"),
    ("LL_Intro", "DC15 dex-« Dick-Ass Roublard. »"),
    ("LL_Intro", "DC15 int-Contrôle ?"),
    ("LL_Intro", "DC15 int-« Pour régner sur le monde. »"),
    ("LL_Intro", "DC15 str-Je vous en prie, non, je ne veux pas être un Envoyeur..."),
    ("LL_Intro", "DC15 str-« <b>Le Clerc.</b> »"),
    ("LL_Intro", "DC15 str-« Je suis le Gardien de la justice et de la paix. Un véritable héros <i>humain</i>. »"),
    ("LL_Intro", "DC17 cha-« <i>M'aimer</i> ? »"),
    ("LL_Intro", "DC17 con-« La <i>chair</i> ? »"),
    ("LL_Intro", "DC17 con-« Les Agrariens. S'ils étaient encore là... »"),
    ("LL_Intro", "DC17 dex-« <i>La propagande</i> ? »"),
    ("LL_Intro", "DC17 int-« <i>Prendre le pouvoir</i> ? »"),
    ("LL_Intro", "DC17 str-« Mes <i>os</i> ? »"),
    ("LL_Intro", "DC17 wis-« ...<i>Tout</i> le reste ? »"),
    ("LL_Intro", "DC9 dex-« Je <shake><b>NE SUIS PAS MORT</b></shake>. »"),
    ("LL_Intro", "DC9 str-Sauver la cité ?"),
    ("LL_Intro", "FC10 wis-D'accord. Mais c'est quoi la quête déjà ?"),
    ("LL_Intro", "FC8 int-<i>Ragn ?</i>"),
    ("LL_Intro", "FC8 wis-C. L. Eric ? Ça sonne comme <i>Cleric</i>."),
    ("LL_Intro", "FC8 wis-« C.L. Eric. »"),
    ("LL_CorpseOne", "DC11 int-« Je voterai pour moi. Je serai votre dirigeant Arcaniste. Un mage-roi. Ça sonne bien, hein ? »"),
    ("LL_CorpseOne", "DC17 con-(Avoir honte.) « Je suis Agrarien. Juste un gars de la ferme. Cherchant à revenir à l'essentiel, vous voyez ? »"),
]

# Wrap each in a quote terminator: search for `text"` and replace with `text "`
# That way we add a trailing space before the closing JSON quote
out = []
for asset, text in entries:
    # Find: text + '"' (closing JSON quote)
    # Replace: text + ' "' (text + space + closing quote)
    find = text + '"'
    repl = text + ' "'
    out.append(f"{asset}\t{find}\t{repl}")

with open("translations/ll_intro_choices_fix2.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {len(out)} fix entries")
