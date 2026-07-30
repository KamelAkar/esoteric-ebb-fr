"""Extrait les lignes de PROSE traduisibles d'un conteneur Ink (dumpé en JSON).

JSON-aware : parse le Ink JSON et collecte les valeurs string commençant par '^'
(le texte affiché). Gère correctement les guillemets internes.

Usage: python tools/18_extract_dialogue.py <dump.json> <out.tsv>
Sort: idx <TAB> prefix <TAB> english   (prefix = préfixe de jet à préserver)
"""
import re, sys, json

sys.stdout.reconfigure(encoding="utf-8")

PREFIX_RE = re.compile(r'^(ROLL\d+ \w+-|IROLL-|DC\d+ \w+-|DC\d+-|FC\d* \w+-|FC\d*-|SPELL [^-]+-|[A-Za-z][A-Za-z0-9]*-)')
CONTROL_RE = re.compile(r'^(\.|LOC_|music_|sfx_|amb_|vo_|anim_|cam_|img_|bg_)')
IDENT_RE = re.compile(r'^[A-Za-z][A-Za-z0-9]*(_[A-Za-z0-9]+)+\s*$')
DICE_ONLY = re.compile(r'^(DC|FC|ROLL|IROLL|SPELL)\b[^a-z]*$')


def walk(node, out):
    if isinstance(node, str):
        if node.startswith('^'):
            out.append(node[1:])
    elif isinstance(node, list):
        for x in node:
            walk(x, out)
    elif isinstance(node, dict):
        for v in node.values():
            walk(v, out)


def is_prose(t):
    s = t.strip()
    if len(s) < 3:
        return False
    if CONTROL_RE.match(s) or IDENT_RE.match(s) or DICE_ONLY.match(s):
        return False
    if '==' in s or re.search(r'[A-Za-z0-9]==?', s) and re.search(r'\b\w+\s*=\s*\d', s):
        return False
    if not re.search(r'[A-Za-z]{2,}', s):
        return False
    if ' ' not in s and not re.search(r'[.!?,;:]', s):
        return False
    return True


def split_prefix(t):
    m = PREFIX_RE.match(t)
    if m:
        pref = m.group(1)
        # ne pas confondre un vrai préfixe de jet avec un mot suivi d'un tiret dans la prose
        if re.match(r'^(ROLL|IROLL|DC|FC|SPELL)', pref):
            return pref, t[m.end():]
    return "", t


def main():
    dump, out = sys.argv[1], sys.argv[2]
    raw = open(dump, encoding="utf-8-sig").read()
    obj = json.loads(raw)
    strings = []
    walk(obj, strings)
    rows = []
    seen = set()
    for t in strings:
        pref, body = split_prefix(t)
        if not is_prose(body):
            continue
        if '\n' in t or '\r' in t:      # lignes multi-lignes: à traiter à part
            continue
        if t in seen:
            continue
        seen.add(t)
        rows.append((pref, body))
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write("idx\tprefix\tenglish\n")
        for i, (pref, body) in enumerate(rows):
            f.write(f"{i}\t{pref}\t{body}\n")
    print(f"{len(rows)} lignes de prose extraites -> {out}")


if __name__ == "__main__":
    main()
