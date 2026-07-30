"""Injecte toutes les traductions FR d'une zone (un sharedassets) via inkbulk.

Rassemble tous les morceaux (build_tmp/chunks/<name>__<k>.tsv + _fr.tsv) des
conteneurs de la zone, construit un TSV inkbulk unique (find<TAB>replace en
forme sous-chaîne échappée), et l'applique en une passe.

Usage: python tools/20_inject_zone.py <sa_index> <sharedassets.assets>
"""
import glob, json, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTNET = os.path.join(REPO, "tools", "dotnet-deploy", "bin", "Debug", "net8.0", "dotnet-deploy.exe")


def esc(s):
    return json.dumps("^" + s, ensure_ascii=False)[1:-1]


def read_en(path):
    # lecture manuelle (pas csv: il strippe les guillemets des champs commençant par ")
    out = {}
    with open(path, encoding="utf-8") as f:
        next(f, None)
        for line in f:
            line = line.rstrip("\n")
            p = line.split("\t")
            if len(p) < 3:
                continue
            out[p[0]] = (p[1], "\t".join(p[2:]))
    return out


def read_fr(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        next(f, None)
        for line in f:
            line = line.rstrip("\n")
            p = line.split("\t")
            if len(p) < 2:
                continue
            out[p[0]] = "\t".join(p[1:])
    return out


def main():
    sa = int(sys.argv[1])
    assets = sys.argv[2]
    conts = [c[1] for c in json.load(open("translations/_untranslated_containers.json")) if c[0] == sa]
    pairs = []
    missing = []
    for name in conts:
        en_chunks = sorted(glob.glob(f"build_tmp/chunks/{name}__*.tsv"))
        en_chunks = [c for c in en_chunks if not c.endswith("_fr.tsv")]
        for ec in en_chunks:
            fc = ec[:-4] + "_fr.tsv"
            if not os.path.exists(fc):
                missing.append(os.path.basename(ec))
                continue
            en = read_en(ec)
            fr = read_fr(fc)
            for idx, (pref, e) in en.items():
                if idx not in fr:
                    continue
                fe, ff = pref + e, pref + fr[idx]
                if fe != ff:
                    pairs.append((esc(fe), esc(ff)))
    if missing:
        print("MORCEAUX SANS TRADUCTION:", missing)
    # dédup + longest-first
    seen = set(); uniq = []
    for a, b in pairs:
        if a in seen:
            continue
        seen.add(a); uniq.append((a, b))
    uniq.sort(key=lambda p: -len(p[0]))
    tsv = "build_tmp/inkbulk_zone.tsv"
    with open(tsv, "w", encoding="utf-8", newline="") as f:
        for a, b in uniq:
            f.write(f"{a}\t{b}\n")
    print(f"{len(uniq)} paires -> {tsv}")
    r = subprocess.run([DOTNET, "inkbulk", assets, tsv], capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip())
    if r.returncode != 0:
        print("ERREUR:", r.stderr[:400])


if __name__ == "__main__":
    main()
