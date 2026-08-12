---
title: PowerShell Set-Content -Encoding utf8 writes a BOM that silently kills frontmatter parsing
tags: [powershell, windows, encoding, bom, utf8, frontmatter, yaml]
projects: [clutch]
date: 2026-08-12
---

## Problem

A markdown file edited through PowerShell stopped being picked up by a frontmatter
parser. No error, no warning: the file simply behaved as if it had no metadata at
all. In this case a library file dropped out of its `core` set and nothing reported
a failure - the count just went from 15 to 14.

The file looked completely normal in an editor and in `head`:

```
---
title: Continuity - one session, one continuous project
modes: [core]
---
```

## Root cause

`Set-Content -Encoding utf8` in Windows PowerShell 5.1 writes **UTF-8 with a BOM**
(bytes `EF BB BF`). The BOM lands before the opening `---`, so the first line is
`"﻿---"` rather than `"---"`.

The trap is that `str.strip()` in Python does **not** remove U+FEFF - it is not
whitespace. So the common guard

```python
if lines[0].strip() != "---":
    return {}, text          # "no frontmatter here"
```

takes the early-exit branch and reports the file as having no metadata, instead of
raising. Any parser written this way fails open and loses data silently.

Confirm with bytes, not characters:

```bash
head -c 3 file.md | xxd     # efbbbf means a BOM is present
```

## Solution

Strip the BOM before parsing. One line, at the top of the parser:

```python
text = text.lstrip("﻿")
```

Fixing the parser matters more than fixing the file, because the next tool that
touches the file through PowerShell will put the BOM straight back.

To clean existing files:

```python
raw = path.read_bytes()
if raw.startswith(b"\xef\xbb\xbf"):
    path.write_bytes(raw[3:])
```

To avoid writing one in the first place, prefer `-Encoding utf8NoBOM` (PowerShell
6+), or write the file from Python, or use `[IO.File]::WriteAllText($p, $s,
[Text.UTF8Encoding]::new($false))` on 5.1.

## Notes

- Windows PowerShell 5.1. PowerShell 6+ defaults `Set-Content` to UTF-8 without a
  BOM and adds the explicit `utf8NoBOM` value, so the same script behaves
  differently across the two.
- `Out-File` and `>` in this environment also produce UTF-8 with a BOM.
- Same class of bug as any `if first_line != EXPECTED: treat as absent` check. If a
  format has a required opening token, a missing token should be loud, not a
  silent "this file has no metadata".
- Related: the codebase-wide rule to run generated markdown through an ASCII
  normalizer catches non-keyboard characters but will not catch a BOM, since a BOM
  is invisible to a text-level pass that reads with `encoding="utf-8"` (Python
  decodes it into the string rather than dropping it).
