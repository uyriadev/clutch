# Skills browser

A one-file local web app for reading the clutch skill libraries as a file tree and
copying paste-ready reference snippets. It walks `prompts/`, `guides/`, `rules/`, and
`templates/`, previews any file, and gives you one-click ways to point an AI at a skill
(bare path, `@mention`, a "Read X in full" front-load line, or the raw contents).

It reads your real files live on every request, so what you see is always what is on
disk - nothing to rebuild, nothing to keep in sync.

## Requirements

- Python 3.8 or newer. Stdlib only - no `pip install`, no virtualenv, no network.
- Any modern browser.

## Get it onto your machine

The script has to sit at the **root of the clutch repo** - it finds the libraries by
looking for `prompts/`, `guides/`, `rules/`, and `templates/` next to itself.

If you keep clutch in git:

```bash
git clone <your-clutch-remote> clutch
cd clutch
```

Then drop `skills_browser.py` in that root directory (it is already here if you cloned
this repo). That is the whole install - one file, no dependencies.

## Run it

```bash
python skills_browser.py
```

It scans the libraries, binds to a free port on `127.0.0.1`, prints the URL, and opens
your browser. Stop it with Ctrl-C.

Flags:

| Flag | What it does |
|------|--------------|
| `--port 8765` | Bind a fixed port instead of a random free one |
| `--no-open` | Do not auto-open the browser (just print the URL) |

## Use it

- **Filter** - just start typing anywhere; keystrokes jump to the filter box. It matches
  on title and path and auto-expands matching folders.
- **Move and open** - `up` / `down` walk the visible files, `enter` opens the preview.
  `esc` clears the filter.
- **Copy a reference** - with a file open, the copy bar gives four formats (keys `1`-`4`):
  1. bare path - `prompts/operating-mode.md`
  2. `@mention` - `@prompts/operating-mode.md`
  3. front-load line - `Read prompts/operating-mode.md in full, then `
  4. raw contents - the whole file in a fenced block
- **Basket** - tick the checkbox on any files, then copy them together as one combined
  front-load block or as all their contents concatenated. Good for handing an AI several
  skills at once. `space` toggles the highlighted file into the basket.

Paste whichever snippet into your AI chat to reference the skill.

## How it works (and how to adapt it)

One file, two halves:

- **Backend** - a stdlib `http.server` with three routes. `GET /` serves the page;
  `GET /api/tree` returns a flat JSON list of every skill file (`path`, `title`,
  `category`, `words`, `mtime`); `GET /api/file?path=...` returns one file's raw
  markdown. Every file read is jailed to the repo root and restricted to `.md` files
  under a known root, so a crafted `path` cannot escape the repo.
- **Frontend** - a single self-contained HTML page (all CSS and JS inline, no CDNs)
  embedded in the `FRONTEND_HTML` string near the bottom of the script. It builds the
  folder tree client-side by splitting each `path` on `/`.

Common changes:

- **Different libraries.** By default it scans `prompts`, `guides`, `rules`, `templates`.
  To change that without touching code, add a `"library_roots"` array to `config.json`:

  ```json
  { "library_roots": ["prompts", "guides", "rules", "templates", "solutions"] }
  ```

  The script picks it up on next start. Index files named `README.md` and `LIBRARY.md`
  are always skipped.

- **Swap the frontend.** The UI is just the `FRONTEND_HTML` string. Replace it with any
  self-contained HTML page that calls `/api/tree` and `/api/file?path=` per the shapes
  above and it will work unchanged.

- **Run it from another repo.** Point `REPO_ROOT` at wherever your markdown lives, or
  copy the script into that repo's root. As long as the roots exist next to the script,
  it serves them.

## Notes

- It binds to `127.0.0.1` only - it is a local tool, not something to expose on a network.
- Because it is a plain script (not part of the AI.md bundle), it does not need
  `export.py` or `clutch update` to propagate. Copy the file, run it.
