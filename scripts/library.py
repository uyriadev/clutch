"""Library metadata: what each prompt/guide is about, and when to load it.

Every file in prompts/ and guides/ carries frontmatter:

    ---
    title: Communication - findings first, filler never
    tags: [response-style, filler, brevity]
    modes: [core]
    order: 20
    ---

This module reads that metadata and answers the three questions the rest of the
toolkit asks:

  - what is always on?          modes containing "core"
  - what does a phase need?     mode_files(cfg, "debug")
  - where is the file about X?  search(cfg, "encoding")

export.py builds the AI.md mode table from it, skills_browser.py searches it, and
you can drive it by hand:

    python .clutch/scripts/library.py modes            # the mode table
    python .clutch/scripts/library.py mode debug       # one mode's read line
    python .clutch/scripts/library.py search timeout   # keyword -> files
    python .clutch/scripts/library.py --list           # everything with metadata

Stdlib only; Python 3.8+.
"""
import sys

from _common import AI_ROOT, global_dir, load_config, parse_frontmatter

# The phases. "core" is not a phase - it is the always-on set that never unloads.
# Order here is the order they appear in the AI.md table.
MODES = {
    "core": "Always loaded. The response contract and failure-mode discipline.",
    "plan": "Before writing code: scope, approach, and the risky assumption.",
    "code": "Implementing a change that is already decided.",
    "debug": "Something is broken and the cause is not yet known.",
    "review": "Auditing code (yours or someone else's) for defects.",
    "wrap": "Closing a session: the three memory stores, commit, propagate.",
}

# What the user might say to force a phase. Shown in the AI.md router so the switch
# is recognised from plain speech, not just from the mode's own name.
TRIGGERS = {
    "plan": '"plan", "plan mode", "how would you", "what\'s the approach"',
    "code": '"fix", "add X", "continue", "clean", "redo", "implement"',
    "debug": '"debug", "why is this failing", or a pasted error / stack trace',
    "review": '"review", "audit", "check this", "optimize"',
    "wrap": ('"wrap up", "we\'re done", "save state", "save the session", '
             '"index this", "commit this", "before I go"'),
}

# Libraries that carry mode/tag metadata. rules/ is selected by config "stack"
# instead, so it deliberately stays out.
ROOTS = ("prompts", "guides")

# Index files, skipped only at a library root - prompts/README.md is a table of
# contents, but prompts/design/README.md is the design trigger table, real content.
SKIP_NAMES = {"README.md", "LIBRARY.md", "INDEX.md"}


def is_index(rel_parts):
    return len(rel_parts) == 1 and rel_parts[0] in SKIP_NAMES


def library_dirs(cfg, root):
    """Local first, then the global store - a source repo overrides the published copy."""
    dirs = []
    local = AI_ROOT / root
    if local.is_dir():
        dirs.append(local)
    g = global_dir(cfg) / root
    if g.is_dir() and g != local:
        dirs.append(g)
    return dirs


def scan(cfg=None, roots=ROOTS):
    """Every library file with its metadata, deduped by relative path (local wins)."""
    cfg = cfg or load_config()
    seen, entries = set(), []
    for root in roots:
        for base in library_dirs(cfg, root):
            for path in sorted(base.rglob("*.md")):
                sub = path.relative_to(base)
                if is_index(sub.parts):
                    continue
                rel = f"{root}/{sub.as_posix()}"
                if rel in seen:
                    continue
                seen.add(rel)
                try:
                    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
                except OSError:
                    continue
                entries.append({
                    "path": rel,
                    "root": root,
                    "title": meta.get("title") or first_h1(body) or path.stem,
                    "tags": meta.get("tags", []),
                    "modes": meta.get("modes", []),
                    "order": int(meta.get("order", 50) or 50),
                    "words": len(body.split()),
                })
    return entries


def first_h1(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def mode_files(cfg=None, mode="core", entries=None):
    """Paths a mode loads, in declared order. 'core' files are excluded from the
    phase modes - they are already resident, so a phase only names what is new."""
    entries = entries if entries is not None else scan(cfg)
    hits = [e for e in entries if mode in e["modes"]]
    if mode != "core":
        hits = [e for e in hits if "core" not in e["modes"]]
    hits.sort(key=lambda e: (e["order"], e["path"]))
    return [e["path"] for e in hits]


def read_line(paths, suffix="in full for context."):
    """The paste-able front-load instruction. Matches the skills-browser button."""
    if not paths:
        return ""
    if len(paths) == 1:
        joined = paths[0]
    elif len(paths) == 2:
        joined = f"{paths[0]} and {paths[1]}"
    else:
        joined = ", ".join(paths[:-1]) + f", and {paths[-1]}"
    return f"Read {joined} {suffix}".rstrip()


def search(cfg=None, *terms, entries=None):
    """Rank files by keyword hit. Tag match outranks title, which outranks path."""
    entries = entries if entries is not None else scan(cfg)
    needles = [t.lower() for t in terms if t.strip()]
    if not needles:
        return []
    scored = []
    for e in entries:
        score = 0
        tags = " ".join(e["tags"]).lower()
        for n in needles:
            if n in tags:
                score += 5
            if n in e["title"].lower():
                score += 3
            if n in e["path"].lower():
                score += 2
        if score:
            scored.append((score, e))
    scored.sort(key=lambda se: (-se[0], se[1]["path"]))
    return [e for _, e in scored]


def tag_index(cfg=None, entries=None):
    """tag -> the paths carrying it. The reverse lookup search would do for you."""
    entries = entries if entries is not None else scan(cfg)
    idx = {}
    for e in entries:
        for t in e["tags"]:
            idx.setdefault(t, set()).add(e["path"])
    return {t: sorted(paths) for t, paths in sorted(idx.items())}


def vocabulary(cfg=None, entries=None):
    """Every tag in use, alphabetical. The 'what can I even ask for' list."""
    return sorted(tag_index(cfg, entries))


def mode_table(cfg=None, entries=None):
    """Rows of (mode, description, read_line) for the AI.md routing table."""
    entries = entries if entries is not None else scan(cfg)
    rows = []
    for mode, desc in MODES.items():
        paths = mode_files(cfg, mode, entries)
        rows.append((mode, desc, read_line(paths) if paths else ""))
    return rows


def main():
    cfg = load_config()
    entries = scan(cfg)
    args = sys.argv[1:]
    cmd = args[0] if args else "modes"

    if not entries:
        sys.exit("error: no library files with metadata found. Run sync.py first.")

    if cmd in ("--list", "list"):
        for e in sorted(entries, key=lambda e: e["path"]):
            modes = ",".join(e["modes"]) or "-"
            tags = ", ".join(e["tags"]) or "-"
            print(f"  {e['path']:<44} [{modes}]  {tags}")
        print(f"\n{len(entries)} files with metadata")
        return

    if cmd == "modes":
        for mode, desc, line in mode_table(cfg, entries):
            n = len(mode_files(cfg, mode, entries))
            print(f"\n  {mode}  ({n} file{'s' if n != 1 else ''}) - {desc}")
            if line:
                print(f"    {line}")
        return

    if cmd == "mode":
        if len(args) < 2:
            sys.exit(f"usage: library.py mode <{'|'.join(MODES)}>")
        name = args[1]
        if name not in MODES:
            sys.exit(f"error: unknown mode '{name}'. Known: {', '.join(MODES)}")
        line = read_line(mode_files(cfg, name, entries))
        print(line or f"(mode '{name}' has no files tagged yet)")
        return

    if cmd == "tags":
        idx = tag_index(cfg, entries)
        for tag, paths in idx.items():
            print(f"  {tag:<22} {', '.join(paths)}")
        print(f"\n{len(idx)} tags across {len(entries)} files")
        return

    if cmd == "search":
        if len(args) < 2:
            sys.exit("usage: library.py search <keyword> [keyword...]")
        hits = search(cfg, *args[1:], entries=entries)
        if not hits:
            print(f"no match for {' '.join(args[1:])}")
            return
        for e in hits:
            print(f"  {e['path']:<44} {e['title']}")
            if e["tags"]:
                print(f"    tags: {', '.join(e['tags'])}")
        print(f"\n{read_line([e['path'] for e in hits[:4]])}")
        return

    sys.exit(f"unknown command '{cmd}'. Try: modes | mode <name> | search <kw> | --list")


if __name__ == "__main__":
    main()
