"""Replace common non-keyboard characters with ASCII (see prompts/human-output.md).

Mechanical cleanup: em/en dashes, smart quotes, ellipsis, arrows, bullets, and the
like become their standard-keyboard equivalents. Unmapped non-ASCII (e.g. the mouse
marker) is left alone and reported by --check so you can eyeball it.

    python .clutch/scripts/ascii_normalize.py prompts guides rules   # apply
    python .clutch/scripts/ascii_normalize.py --dry-run prompts       # preview
    python .clutch/scripts/ascii_normalize.py --check prompts guides  # report leftovers

Paths are files or dirs (dirs walked for the given extensions, default .md). Stdlib.
"""
import argparse
import sys
from pathlib import Path

REPLACEMENTS = {
    "—": "-",    # em dash
    "–": "-",    # en dash
    "‒": "-",    # figure dash
    "―": "-",    # horizontal bar
    "…": "...",  # ellipsis
    "“": '"', "”": '"', "„": '"',   # double quotes
    "‘": "'", "’": "'", "‚": "'",    # single quotes / apostrophe
    "→": "->", "←": "<-", "↔": "<->",  # arrows
    "⇒": "=>",
    "×": "x",    # multiplication sign
    "•": "-", "·": "-", "‧": "-",   # bullets / middot
    " ": " ", " ": " ", " ": " ", "​": "",  # spaces
    "✓": "[x]", "✔": "[x]", "✗": "[ ]", "✘": "[ ]",  # checks
    "✅": "[x]", "❌": "[ ]",   # emoji checks
    "≠": "!=", "≤": "<=", "≥": ">=",  # comparisons
    "‑": "-",    # non-breaking hyphen
    "²": "^2", "³": "^3", "±": "+/-",   # math notation
    "Σ": "sum", "≈": "~",  # summation, approx
    "🔴": "(red)", "🟡": "(yellow)", "🟢": "(green)",  # traffic-light status markers
}


def normalize(text):
    changes = 0
    for src, dst in REPLACEMENTS.items():
        if src in text:
            changes += text.count(src)
            text = text.replace(src, dst)
    return text, changes


def leftovers(text):
    seen = {}
    for ch in text:
        if ord(ch) > 127:
            seen[ch] = seen.get(ch, 0) + 1
    return seen


def gather(paths, exts):
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in sorted(path.rglob("*")):
                # never rewrite this file: its REPLACEMENTS map literally contains the
                # characters it replaces, so normalizing it would corrupt the map.
                if f.name == "ascii_normalize.py":
                    continue
                if f.is_file() and f.suffix.lower() in exts:
                    yield f
        elif path.is_file() and path.name != "ascii_normalize.py":
            yield path


def main():
    ap = argparse.ArgumentParser(description="Normalize non-ASCII punctuation to ASCII.")
    ap.add_argument("paths", nargs="+", help="files or directories")
    ap.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
    ap.add_argument("--check", action="store_true",
                    help="report remaining non-ASCII (after mapping), write nothing")
    ap.add_argument("--ext", default=".md",
                    help="comma list of extensions for dirs (default: .md)")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    exts = {e if e.startswith(".") else "." + e for e in args.ext.split(",")}
    total_files = total_changes = 0
    remaining = {}
    for f in gather(args.paths, exts):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new, changes = normalize(text)
        if args.check:
            rem = leftovers(new)
            if rem:
                remaining[str(f)] = rem
            continue
        if changes:
            total_files += 1
            total_changes += changes
            verb = "would fix" if args.dry_run else "fixed"
            print(f"  {verb} {changes:4d}  {f}")
            if not args.dry_run:
                f.write_text(new, encoding="utf-8")

    if args.check:
        if not remaining:
            print("clean: no non-ASCII characters remain.")
        else:
            for fn, chars in remaining.items():
                pretty = ", ".join(f"{repr(c)} x{n}" for c, n in chars.items())
                print(f"  {fn}: {pretty}")
        return
    tail = " (dry run)" if args.dry_run else ""
    print(f"{'would fix' if args.dry_run else 'fixed'} {total_changes} char(s) "
          f"in {total_files} file(s){tail}")


if __name__ == "__main__":
    main()
