"""Rebuild sharedassets from VANILLA + only the FR Ink TextAssets.

Why: the previous translator's sharedassets were re-serialized with a broken
tool (the same one that corrupted level2 -> crash). Shipping them breaks the
GAMEPAD pause button (bisected 2026-07-21: vanilla sharedassets = pause works,
their sharedassets = pause broken), and likely carries other latent corruption.

Method: start from the vanilla file (all components intact) and inject ONLY the
FR text of each Ink TextAsset, using AssetsTools (dotnet-deploy), which rewrites
just those assets and leaves every other object untouched.

Usage: python tools/16_rebuild_sharedassets.py <vanilla_dir> <fr_dir> <out_dir>
"""
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTNET = os.path.join(REPO, "tools", "dotnet-deploy", "bin", "Debug", "net8.0", "dotnet-deploy.exe")


def list_text_assets(path):
    r = subprocess.run([DOTNET, "listta", path], capture_output=True, text=True, encoding="utf-8")
    names = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        size, name = parts
        try:
            int(size)
        except ValueError:
            continue
        names.append(name)
    return names


def dump(path, name, out_file):
    subprocess.run([DOTNET, "dumpta", path, name, out_file], capture_output=True)
    return os.path.exists(out_file)


def main():
    van_dir, fr_dir, out_dir = sys.argv[1:4]
    only = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    os.makedirs(out_dir, exist_ok=True)
    tmp_root = os.path.join("build_tmp", "fr_ink")
    total_files = total_assets = 0

    for i in range(30):
        if only is not None and i not in only:
            continue
        fn = f"sharedassets{i}.assets"
        vp = os.path.join(van_dir, fn)
        fp = os.path.join(fr_dir, fn)
        if not (os.path.exists(vp) and os.path.exists(fp)):
            continue

        names = list_text_assets(fp)
        if not names:
            shutil.copy(vp, os.path.join(out_dir, fn))
            print(f"{fn}: aucun TextAsset, copie vanilla")
            continue

        d = os.path.join(tmp_root, str(i))
        os.makedirs(d, exist_ok=True)
        got = []
        for nm in names:
            # skip names that would break the comma-separated arg
            if "," in nm:
                continue
            if dump(fp, nm, os.path.join(d, nm + ".json")):
                got.append(nm)

        out_file = os.path.join(out_dir, fn)
        shutil.copy(vp, out_file)
        if got:
            subprocess.run([DOTNET, out_file, d, ",".join(got), ".json"],
                           capture_output=True, text=True, encoding="utf-8")
        print(f"{fn}: {len(got)}/{len(names)} TextAssets FR injectés dans le vanilla")
        total_files += 1
        total_assets += len(got)
        shutil.rmtree(d, ignore_errors=True)

    print(f"\n{total_files} fichiers reconstruits, {total_assets} TextAssets FR injectés")


if __name__ == "__main__":
    main()
