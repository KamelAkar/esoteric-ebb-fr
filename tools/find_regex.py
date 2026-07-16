"""Find regex patterns in metadata."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

with open("metadata_strings/all_strings.tsv", encoding="utf-8", errors="replace") as f:
    next(f)
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        text = parts[4]
        if text.startswith("^") and len(text) < 100:
            if "(" in text or "\\" in text:
                print(f"L{parts[0]}: {text!r}")
