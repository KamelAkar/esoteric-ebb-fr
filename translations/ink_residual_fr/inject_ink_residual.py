# -*- coding: utf-8 -*-
"""Injecte les traductions des lignes Ink résiduelles (build_tmp/ink_fr.json) dans
tous les sharedassets via inkbulk (dotnet-deploy). Pour chaque texte traduit et chacun
de ses préfixes de condition, remplace esc(prefix+en) -> esc(prefix+fr).
Backup des sharedassets modifiés dans backups/sharedassets_pre_ink/. Déploie live+dist.
"""
import glob, json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTNET = os.path.join(REPO, "tools", "dotnet-deploy", "bin", "Debug", "net8.0", "dotnet-deploy.exe")
STEAM = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb/Esoteric Ebb_Data"
DIST = "dist/EsotericEbb-FR-Patch-v1.3.6/Esoteric Ebb_Data"
BACKUP = "backups/sharedassets_pre_ink"
os.makedirs(BACKUP, exist_ok=True)

def esc(s):
    return json.dumps("^" + s, ensure_ascii=False)[1:-1]

todo = json.load(open("build_tmp/ink_todo_map.json", encoding="utf-8"))
fr = json.load(open("build_tmp/ink_fr.json", encoding="utf-8"))

pairs = []
for text, prefixes in todo.items():
    if text not in fr:
        continue
    ftext = fr[text]
    if ftext == text:
        continue
    for p in prefixes:
        a, b = esc(p + text), esc(p + ftext)
        if a != b:
            pairs.append((a, b))
# dedup longest-first
seen = set(); uniq = []
for a, b in pairs:
    if a in seen:
        continue
    seen.add(a); uniq.append((a, b))
uniq.sort(key=lambda p: -len(p[0]))
tsv = "build_tmp/inkbulk_residual.tsv"
with open(tsv, "w", encoding="utf-8", newline="") as f:
    for a, b in uniq:
        f.write(f"{a}\t{b}\n")
print(f"{len(uniq)} paires -> {tsv}")

targets = sys.argv[1:] if len(sys.argv) > 1 else [str(i) for i in range(25)]
for i in targets:
    name = f"sharedassets{i}.assets"
    live = os.path.join(STEAM, name)
    if not os.path.exists(live):
        continue
    bak = os.path.join(BACKUP, name)
    if not os.path.exists(bak):
        import shutil; shutil.copy(live, bak)
    r = subprocess.run([DOTNET, "inkbulk", live, tsv], capture_output=True, text=True, encoding="utf-8")
    line = [l for l in r.stdout.splitlines() if "Modified" in l or "substitution" in l]
    print(f"{name}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''}", flush=True)
    if r.returncode != 0:
        print("  ERREUR:", r.stderr[:300]); continue
    import shutil; shutil.copy(live, os.path.join(DIST, name))
print("Injection Ink résiduelle terminée.")
