"""Construit un TSV inkbulk (find<TAB>replace) depuis les TSV EN+FR extraits,
puis l'applique au fichier sharedassets via dotnet-deploy inkbulk.

find/replace = forme "sous-chaîne échappée" (json.dumps sans les guillemets
externes) du token Ink '^...' — ça matche le contenu brut du m_Script.

Usage: python tools/19_inject_dialogue.py <en.tsv> <fr.tsv> <sharedassets.assets>
"""
import csv, json, os, sys, subprocess

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTNET = os.path.join(REPO, "tools", "dotnet-deploy", "bin", "Debug", "net8.0", "dotnet-deploy.exe")


def esc(s):
    # forme échappée interne (comme dans le JSON brut), sans guillemets externes
    return json.dumps("^" + s, ensure_ascii=False)[1:-1]


def main():
    en_path, fr_path, assets = sys.argv[1:4]
    en = {}
    with open(en_path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            en[r["idx"]] = (r["prefix"], r["english"])
    fr = {}
    with open(fr_path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            fr[r["idx"]] = r["french"]

    pairs = []
    for idx, (pref, eng) in en.items():
        if idx not in fr:
            continue
        f_en = pref + eng
        f_fr = pref + fr[idx]
        if f_en == f_fr:
            continue
        pairs.append((esc(f_en), esc(f_fr)))

    # trie longest-first pour éviter les remplacements partiels
    pairs.sort(key=lambda p: -len(p[0]))
    tsv = os.path.join("build_tmp", "inkbulk_current.tsv")
    with open(tsv, "w", encoding="utf-8", newline="") as f:
        for a, b in pairs:
            f.write(f"{a}\t{b}\n")
    print(f"{len(pairs)} paires écrites -> {tsv}")

    r = subprocess.run([DOTNET, "inkbulk", assets, tsv], capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip())
    if r.returncode != 0:
        print("ERREUR:", r.stderr[:500])


if __name__ == "__main__":
    main()
