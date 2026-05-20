"""Package the FR patch as a drag-and-drop ZIP for Nexus.

Copies all patched files from Steam dir to dist/EsotericEbb-FR-Patch-vX.X.X/,
writes LISEZ_MOI.txt, then zips.
"""
import shutil
import zipfile
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VERSION = "1.3.0"
REPO_ROOT = Path(__file__).resolve().parent.parent
STEAM_DATA = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Esoteric Ebb\Esoteric Ebb_Data")
DIST_DIR = REPO_ROOT / "dist"
PATCH_DIR = DIST_DIR / f"EsotericEbb-FR-Patch-v{VERSION}"
ZIP_FILE = DIST_DIR / f"EsotericEbb-FR-Patch-v{VERSION}.zip"

# Files to include in the patch (relative to Esoteric Ebb_Data/)
# Inclut TOUS les fichiers que v1.2.2 ou cette session ont pu modifier.
# Les sharedassets contiennent les TextAssets Ink (dialogues + intro) qui
# doivent être livrés en totalité — sinon installation sur vanilla = dialogues EN.
# resources.assets RÉ-INCLUS 2026-05-20 — initialement exclu car suspect de casser
# le parseur DC, mais la vraie cause était le patch metadata (4535, 'DC', 'DD').
# Avec ce patch désactivé + (9551, 'ROLL', 'JET') aussi désactivé, le resources.assets
# modifié (FR text dans col EN du Dialogs CSV par le précédent traducteur) fonctionne
# et apporte ~78k lignes FR pour les dialogues NPC (CB_, AR_, GW_, etc.).
INCLUDED_FILES = [
    "il2cpp_data/Metadata/global-metadata.dat",
    "resources.assets",
]
# All level files
for i in range(0, 25):
    INCLUDED_FILES.append(f"level{i}")
# ALL sharedassets — chacun contient des LL_*/CB_*/etc. TextAssets Ink traduits
for i in range(0, 25):
    INCLUDED_FILES.append(f"sharedassets{i}.assets")

LISEZ_MOI = """================================================================================
  ESOTERIC EBB - Patch de Traduction Française (v{VERSION})
================================================================================

  Patch drag-and-drop sans BepInEx ni autre framework. Modifie directement
  les fichiers de jeu (metadata IL2CPP + assets Unity).

================================================================================
  INSTALLATION
================================================================================

  1. Localisez le dossier du jeu sur Steam :
       Bibliothèque > Esoteric Ebb > Clic droit > Propriétés >
       Fichiers installés > Parcourir...

  2. Extrayez TOUT le contenu de ce patch directement dans le dossier
     du jeu, en remplaçant les fichiers existants. Seul le dossier
     "Esoteric Ebb_Data" est modifié.

  3. Lancez le jeu normalement via Steam.

================================================================================
  DÉSINSTALLATION
================================================================================

  Pour restaurer le jeu en anglais :

    Steam > Bibliothèque > Esoteric Ebb > Clic droit > Propriétés >
    Fichiers installés > Vérifier l'intégrité des fichiers du jeu

  Tous les fichiers modifiés seront restaurés.

================================================================================
  CONTENU DU PATCH v{VERSION}
================================================================================

  Nouveautés depuis v1.2.2 :
  - Onglets inventaire entièrement traduits (Tout / Bottes / Manteau /
    Casques / Armement / Livres / Clés / Cléricaux / Babioles / etc.)
  - Verbes d'interaction (Voir / Parler / Piquer / Examiner / Ouvrir /
    Lire / Toucher / Partir / etc.)
  - HUD : "Jour 1" au lieu de "Day 1"
  - Sections du journal traduites (Cite / Talent / Gens / Mystères /
    Régions / Annales / Langue / Pouvoir / Religion / Nature / Romans)
  - Items courants : Bottes, Manteau, Fiole, Dague, Sac sans Fond,
    Ceinture des Nains, Brassards de Voleur, Marteau Adamantin, etc.
  - Devise : Crowns -> Écus
  - Tooltips Grimoire (Sorts Préparés / Sorts Collectés / Difficulté
    de Sort) traduits
  - Popups Stockage Profond (bourse) traduits
  - Fix du bug "one single time" dans Quest_34
  - DC -> DD dans le glossaire
  - Et plus...

================================================================================
  LIMITATIONS CONNUES
================================================================================

  Quelques labels restent en anglais car ils sont utilisés comme clés de
  binding par le code C# du jeu :
  - "Inventory" (onglet supérieur)
  - Noms de sorts dans le Grimoire (Cure Wounds, Mage Hand, etc.)
  - Sections "DIALOGS / VISUALS / AUDIO" du menu Options
  - "Lower Lair" et autres noms de scènes

  Ces limitations seront contournées dans une future version si possible.

================================================================================
  Pour signaler un bug : https://github.com/KamelAkar/esoteric-ebb-fr/issues
================================================================================
""".format(VERSION=VERSION)


def main():
    # Clean dist
    if PATCH_DIR.exists():
        shutil.rmtree(PATCH_DIR)
    PATCH_DIR.mkdir(parents=True, exist_ok=True)

    # Copy files
    print(f"Packaging EsotericEbb-FR-Patch-v{VERSION}...")
    total_size = 0
    for rel in INCLUDED_FILES:
        src = STEAM_DATA / rel
        if not src.exists():
            print(f"  [SKIP] {rel} (missing)")
            continue
        dest = PATCH_DIR / "Esoteric Ebb_Data" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        size = src.stat().st_size
        total_size += size
        print(f"  + {rel} ({size:,} bytes)")

    # Write LISEZ_MOI
    (PATCH_DIR / "LISEZ_MOI.txt").write_text(LISEZ_MOI, encoding="utf-8")
    print(f"  + LISEZ_MOI.txt")

    print(f"\nTotal staged: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

    # Zip
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()
    print(f"\nZipping to {ZIP_FILE.name}...")
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in PATCH_DIR.rglob("*"):
            if f.is_file():
                arcname = f.relative_to(PATCH_DIR)
                zf.write(f, arcname)

    zip_size = ZIP_FILE.stat().st_size
    print(f"Done. {ZIP_FILE} ({zip_size:,} bytes, {zip_size/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
