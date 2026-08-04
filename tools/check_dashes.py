"""Rejette les tirets cadratins et demi-cadratins dans les fichiers du projet.

Deux zones sont exclues, pour de bonnes raisons :

  translations/ et backups/   texte de dialogue du jeu. En francais, le tiret
                              cadratin est la ponctuation normale du dialogue.
  chaines Python de tools/    ce sont des textes de jeu traduits, injectes en
                              place dans les assets Unity : leur longueur en
                              octets est porteuse. Seuls les COMMENTAIRES sont
                              verifies.

Usage : python tools/check_dashes.py [--staged] [fichiers...]
"""
import io
import re
import subprocess
import sys
import tokenize

BANNED = re.compile('[' + chr(0x2013) + chr(0x2014) + ']')
SKIP_PREFIXES = ('translations/', 'backups/', 'test_game/', 'work/')


def list_files(args):
    explicit = [a for a in args if a != '--staged']
    if explicit:
        return explicit
    cmd = (['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR']
           if '--staged' in args else ['git', 'ls-files'])
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [f for f in out.stdout.split('\n') if f]


def check_python_comments(path, failures):
    try:
        with io.open(path, 'rb') as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.COMMENT and BANNED.search(tok.string):
                    failures.append(path + ':' + str(tok.start[0]))
    except (tokenize.TokenError, SyntaxError, UnicodeDecodeError, OSError):
        return


def main():
    args = sys.argv[1:]
    failures = []
    for path in list_files(args):
        if path.startswith(SKIP_PREFIXES):
            continue
        if path.endswith('.py'):
            check_python_comments(path, failures)
            continue
        try:
            with io.open(path, encoding='utf-8') as fh:
                content = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(content.split('\n'), 1):
            if BANNED.search(line):
                failures.append(path + ':' + str(i))
    if failures:
        print('Tiret interdit (U+2014 ou U+2013) trouve dans :', file=sys.stderr)
        for f in failures:
            print('  ' + f, file=sys.stderr)
        print('Remplacer par une virgule, un deux-points, des parentheses '
              'ou une phrase separee.', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
