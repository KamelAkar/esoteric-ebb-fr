# -*- coding: utf-8 -*-
"""Corrige les préfixes de jet DUPLIQUÉS (ex 'ROLL33 wis-ROLL33 wis-' -> 'ROLL33 wis-')
qui fuient à l'écran. Remplacement de sous-chaîne brute via inkbulk sur tous les sharedassets.
Backup dans backups/sharedassets_pre_dupfix/. Déploie live+dist.
"""
import re, glob, os, subprocess, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTNET = os.path.join(REPO, "tools", "dotnet-deploy", "bin", "Debug", "net8.0", "dotnet-deploy.exe")
STEAM = r"C:/Program Files (x86)/Steam/steamapps/common/Esoteric Ebb/Esoteric Ebb_Data"
DIST = "dist/EsotericEbb-FR-Patch-v1.3.6/Esoteric Ebb_Data"
BACKUP = "backups/sharedassets_pre_dupfix"
os.makedirs(BACKUP, exist_ok=True)

pat = re.compile(rb'([A-Z][A-Za-z]*[0-9]+ [a-z]+-)\1')
# collecte des préfixes dupliqués sur tout le corpus
prefixes = set()
for f in glob.glob(STEAM + '/sharedassets*.assets'):
    d = open(f, 'rb').read()
    for m in pat.finditer(d):
        prefixes.add(m.group(1).decode())
print("préfixes dupliqués:", sorted(prefixes))

tsv = "build_tmp/dupfix.tsv"
with open(tsv, "w", encoding="utf-8", newline="") as fp:
    for p in sorted(prefixes):
        fp.write(f"{p}{p}\t{p}\n")   # sous-chaîne brute (ASCII, pas d'échappement)

for f in sorted(glob.glob(STEAM + '/sharedassets*.assets')):
    name = os.path.basename(f)
    d = open(f, 'rb').read()
    if not pat.search(d):
        continue
    bak = os.path.join(BACKUP, name)
    if not os.path.exists(bak):
        shutil.copy(f, bak)
    r = subprocess.run([DOTNET, "inkbulk", f, tsv], capture_output=True, text=True, encoding="utf-8")
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    print(f"{name}: {last}", flush=True)
    if r.returncode == 0:
        shutil.copy(f, os.path.join(DIST, name))
    else:
        print("  ERREUR:", r.stderr[:200])
print("Fix terminé.")
