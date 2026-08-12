---
title: mermaid-cli / Puppeteer fails to launch on Windows - use system Chrome
tags: [mermaid, puppeteer, nodejs, windows, chrome]
projects: [clutch]
date: 2026-08-01
---

## Problem

Rendering a Mermaid diagram with `@mermaid-js/mermaid-cli` (`mmdc`) fails on Windows.
Two failure modes, in order:

1. First run: `Error: Could not find chrome-headless-shell (ver. ...)` - mermaid-cli
   ships `puppeteer-core` but no browser.
2. After `npx puppeteer browsers install chrome-headless-shell`, launching still fails:
   `Failed to launch the browser process: Code: 3221225595` (Windows `0xC000007B`,
   STATUS_INVALID_IMAGE_FORMAT - a missing/mismatched dependent DLL for the headless
   shell).

## Root cause

Puppeteer's downloaded `chrome-headless-shell` build doesn't reliably launch on some
Windows environments (missing runtime dependency -> `0xC000007B`). The bundled-browser
path is fragile there.

## Solution

Point Puppeteer at an **already-installed** Chrome or Edge via `executablePath` in the
puppeteer config, instead of the downloaded headless shell:

```json
{
  "executablePath": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "args": ["--no-sandbox"]
}
```

```bash
mmdc -i diagram.mmd -o diagram.png -s 4 -b white -p puppeteer.json
```

Common browsers to detect: `C:\Program Files\Google\Chrome\Application\chrome.exe`,
`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` (Edge ships with
Windows and is Chromium-based, so it always works as a fallback). Honor
`PUPPETEER_EXECUTABLE_PATH` if set.

`scripts/mermaid_export.py` does this automatically - it scans for a system browser
and writes `executablePath` into the config before rendering.

## Notes

- Write the puppeteer JSON with `json.dumps` / a real JSON writer, not shell `printf`
  - backslashes in the Windows path must be escaped (`\\`) or you get
  `SyntaxError: Bad escaped character in JSON`.
- `-s/--scale` is Puppeteer's `deviceScaleFactor`; scale 4 on a small diagram gave a
  ~2700px-wide PNG. SVG output is vector and resolution-independent regardless.
