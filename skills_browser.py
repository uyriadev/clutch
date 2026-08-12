"""Local browser for the clutch skill libraries.

Serves a small web UI that lets you walk prompts/, guides/, rules/, and templates/
as a file tree, preview any file, and copy paste-ready reference snippets (bare path,
@mention, a "Read X in full" front-load line, or the raw contents) to point an AI at
a skill. Reads your real files live on every request, so it never goes stale.

    python skills_browser.py            # scan, serve on a free localhost port, open browser
    python skills_browser.py --port 8765
    python skills_browser.py --no-open  # don't auto-open the browser

Stdlib only; Python 3.8+. The frontend is a single self-contained HTML page embedded
below - one file, nothing to install.
"""
import argparse
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from _common import parse_frontmatter  # noqa: E402

# The libraries this repo publishes. Kept in sync with config.json's roots if present,
# otherwise these four - the ai/ set etc. all live under rules/.
DEFAULT_ROOTS = ["prompts", "guides", "rules", "templates"]

# Index/meta files that aren't skills. Skipped only at a library root: prompts/README.md
# is a table of contents, but prompts/design/README.md is the design trigger table.
SKIP_NAMES = {"README.md", "LIBRARY.md", "INDEX.md"}


def load_roots():
    """Roots to scan - from config.json's "library_roots" if it's there, else the default."""
    cfg_path = REPO_ROOT / "config.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        roots = cfg.get("library_roots")
        if isinstance(roots, list) and roots:
            return roots
    except (OSError, ValueError):
        pass
    return DEFAULT_ROOTS


def first_h1(text):
    """Display title = the file's first markdown H1, or None if it has none."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def scan(roots):
    """Walk every root for *.md and return a flat list the frontend nests itself.

    Flat is deliberate - the client splits path on "/" to rebuild the tree, so the
    backend stays dumb and we never disagree about folder shape.
    """
    files = []
    for root in roots:
        base = REPO_ROOT / root
        if not base.is_dir():
            continue
        for md in sorted(base.rglob("*.md")):
            sub = md.relative_to(base)
            if len(sub.parts) == 1 and md.name in SKIP_NAMES:
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            meta, body = parse_frontmatter(text)
            rel = md.relative_to(REPO_ROOT).as_posix()
            files.append({
                "path": rel,
                "title": meta.get("title") or first_h1(body) or md.stem,
                "category": root,
                "tags": meta.get("tags", []),
                "modes": meta.get("modes", []),
                "order": int(meta.get("order") or 50),
                "words": len(body.split()),
                "mtime": int(md.stat().st_mtime),
            })
    return files


def safe_resolve(rel_path, roots):
    """Turn a client-supplied path into a real file, or None if it's out of bounds.

    Guards against traversal: the resolved path must sit inside the repo, live under
    one of the scanned roots, be a .md, and actually exist. Anything else -> None.
    """
    if not rel_path:
        return None
    candidate = (REPO_ROOT / rel_path).resolve()
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError:
        return None  # escaped the repo via .. or an absolute path
    if candidate.suffix != ".md" or not candidate.is_file():
        return None
    top = candidate.relative_to(REPO_ROOT).parts[0]
    if top not in roots:
        return None
    return candidate


class Handler(BaseHTTPRequestHandler):
    roots = DEFAULT_ROOTS  # overwritten in main() once config is read

    def _send(self, code, body, content_type):
        payload = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/":
            self._send(200, FRONTEND_HTML, "text/html; charset=utf-8")
            return

        if route == "/api/tree":
            self._json(200, {"files": scan(self.roots)})
            return

        if route == "/api/file":
            rel = (parse_qs(parsed.query).get("path") or [""])[0]
            target = safe_resolve(rel, self.roots)
            if target is None:
                self._json(404, {"error": "not found or out of bounds", "path": rel})
                return
            meta, body = parse_frontmatter(target.read_text(encoding="utf-8"))
            self._json(200, {"path": rel, "content": body, "meta": meta})
            return

        self._json(404, {"error": "unknown route", "path": route})

    def log_message(self, *_args):
        pass  # quiet - we don't need a request log spamming the console


# ---------------------------------------------------------------------------
# Frontend: filled in from the design pass. Single self-contained HTML page.
# ---------------------------------------------------------------------------
FRONTEND_HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>skills browser</title>
<style>
:root{
  --bg:#0d0d0c;
  --bg-2:#131312;
  --bg-3:#191918;
  --panel:#111110;
  --line:#252523;
  --line-2:#2f2f2c;
  --fg:#eeece6;
  --fg-2:#a3a099;
  --fg-3:#6d6a63;
  --accent:#d97f45;
  --accent-2:#f0a06a;
  --accent-dim:rgba(217,127,69,.14);
  --accent-dim-2:rgba(217,127,69,.28);
  --ok:#7fae6a;
  --bad:#c25b4e;
  --radius:6px;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --row:24px;
}
@media (prefers-color-scheme: light){
  :root{
    --bg:#faf9f6;
    --bg-2:#f2f1ec;
    --bg-3:#eae8e1;
    --panel:#fdfcfa;
    --line:#e2e0d8;
    --line-2:#d3d0c6;
    --fg:#26241f;
    --fg-2:#5d5a52;
    --fg-3:#8b877e;
    --accent:#bf6420;
    --accent-2:#a4541a;
    --accent-dim:rgba(191,100,32,.10);
    --accent-dim-2:rgba(191,100,32,.22);
    --ok:#4f7d3c;
    --bad:#a8402f;
  }
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;background:var(--bg);color:var(--fg);
  font:12px/1.5 var(--mono);
  -webkit-font-smoothing:antialiased;
  overflow:hidden;
}
button{font:inherit;color:inherit;background:none;border:none;cursor:pointer;padding:0}
svg{display:block}
::selection{background:var(--accent-dim-2)}

/* scrollbars */
*::-webkit-scrollbar{width:9px;height:9px}
*::-webkit-scrollbar-track{background:transparent}
*::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:99px;border:2px solid var(--bg)}
*::-webkit-scrollbar-thumb:hover{background:var(--fg-3)}

/* ---------- shell ---------- */
#app{display:flex;flex-direction:column;height:100%}

header{
  display:flex;align-items:center;gap:12px;
  height:38px;flex:0 0 38px;padding:0 12px;
  border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,var(--bg-2),var(--panel));
}
.brand{display:flex;align-items:center;gap:8px;letter-spacing:.02em}
.brand .mark{
  width:16px;height:16px;border-radius:4px;
  background:var(--accent);position:relative;flex:0 0 auto;
  box-shadow:0 0 0 3px var(--accent-dim);
}
.brand .mark::after{
  content:"";position:absolute;left:50%;top:50%;
  width:8px;height:4.5px;border-radius:1px;
  border-left:2px solid var(--bg);border-bottom:2px solid var(--bg);
  transform:translate(-50%,-62%) rotate(-45deg);
}
@media (prefers-color-scheme: light){.brand .mark::after{border-color:#fff}}
.brand b{font-weight:600}
.brand span{color:var(--fg-3);font-weight:600}
.hspace{flex:1}
.hint{color:var(--fg-3);display:flex;align-items:center;gap:6px}
kbd{
  border:1px solid var(--line-2);border-bottom-width:2px;border-radius:4px;
  padding:0 4px;font:inherit;font-size:10px;color:var(--fg-2);background:var(--bg-3);
}
.pill{
  display:flex;align-items:center;gap:6px;
  border:1px solid var(--line-2);border-radius:99px;
  padding:3px 9px 3px 7px;color:var(--fg-2);background:var(--bg-3);
  transition:border-color .2s,color .2s;
}
.pill:hover{border-color:var(--fg-3)}
.dot{width:6px;height:6px;border-radius:99px;background:var(--fg-3);position:relative;flex:0 0 auto}
.pill[data-s="up"]{color:var(--ok);border-color:rgba(127,174,106,.35)}
.pill[data-s="up"] .dot{background:var(--ok)}
.pill[data-s="up"] .dot::after{
  content:"";position:absolute;inset:0;border-radius:99px;background:var(--ok);
  animation:ping 2.4s ease-out infinite;
}
.pill[data-s="down"]{color:var(--bad);border-color:rgba(194,91,78,.35)}
.pill[data-s="down"] .dot{background:var(--bad)}
.pill[data-s="wait"] .dot{animation:blink .9s steps(2,end) infinite}
@keyframes ping{0%{opacity:.7;transform:scale(1)}70%,100%{opacity:0;transform:scale(3.4)}}
@keyframes blink{50%{opacity:.2}}

main{flex:1;display:flex;min-height:0}

/* ---------- left pane ---------- */
#left{
  width:330px;min-width:220px;max-width:620px;flex:0 0 auto;
  display:flex;flex-direction:column;min-height:0;
  border-right:1px solid var(--line);background:var(--panel);
}
#grip{
  flex:0 0 3px;cursor:col-resize;background:transparent;
  transition:background .15s;
}
#grip:hover,#grip.drag{background:var(--accent-dim-2)}

.filterwrap{padding:8px;border-bottom:1px solid var(--line);position:relative}
.fieldrow{
  display:flex;align-items:center;gap:7px;
  border:1px solid var(--line-2);border-radius:var(--radius);
  background:var(--bg-3);padding:0 8px;height:28px;
  transition:border-color .15s,box-shadow .15s,background .15s;
}
.fieldrow:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-dim)}
.fieldrow .caret{color:var(--accent);flex:0 0 auto}
#filter{
  flex:1;min-width:0;border:none;background:none;outline:none;
  font:inherit;color:var(--fg);height:100%;
}
#filter::placeholder{color:var(--fg-3)}
#clear{color:var(--fg-3);opacity:0;transition:opacity .15s,color .15s;padding:2px}
#clear:hover{color:var(--fg)}
.filterwrap.has #clear{opacity:1}
/* mode chips - click filters the tree, double-click stages the whole mode */
#moderow{display:flex;gap:4px;flex-wrap:wrap;margin-top:7px}
.mchip{
  border:1px solid var(--line-2);border-radius:99px;padding:1px 8px;
  color:var(--fg-3);background:var(--bg-3);font-size:10.5px;letter-spacing:.03em;
  transition:color .15s,border-color .15s,background .15s;
}
.mchip:hover{color:var(--fg);border-color:var(--fg-3)}
.mchip.on{background:var(--accent);border-color:var(--accent);color:var(--bg)}
@media (prefers-color-scheme: light){.mchip.on{color:#fff}}
.mchip .n{opacity:.6;margin-left:4px}

/* tag chips in the meta pane */
.tagrow{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.tag{
  border:1px solid var(--line);border-radius:3px;padding:0 5px;
  font-size:10px;color:var(--fg-3);background:var(--bg-3);
}
.tag:hover{color:var(--accent);border-color:var(--accent-dim-2)}

.count{
  padding:6px 10px 2px;color:var(--fg-3);font-size:11px;
  display:flex;justify-content:space-between;
}
.count em{font-style:normal;color:var(--fg-2)}

#tree{flex:1;overflow:auto;padding:2px 6px 14px;min-height:0;scroll-behavior:smooth}

.node{position:relative}
.row{
  display:flex;align-items:center;gap:6px;height:var(--row);
  padding:0 6px;border-radius:5px;cursor:pointer;
  position:relative;white-space:nowrap;
  transition:background .12s,color .12s;
}
.row::before{
  content:"";position:absolute;left:1px;top:4px;bottom:4px;width:2px;border-radius:2px;
  background:var(--accent);transform:scaleY(0);opacity:0;
  transition:transform .18s cubic-bezier(.2,.9,.3,1.2),opacity .18s;
}
.row:hover{background:var(--bg-3)}
.row.hl{background:var(--bg-3);color:var(--fg)}
.row.hl::before{transform:scaleY(1);opacity:.55}
.row.sel{background:var(--accent-dim);color:var(--fg)}
.row.sel::before{transform:scaleY(1);opacity:1}
.row .ic{color:var(--fg-3);flex:0 0 auto;transition:color .15s,transform .2s}
.row:hover .ic,.row.sel .ic{color:var(--accent)}
.row.dir .chev{transition:transform .2s cubic-bezier(.2,.8,.3,1)}
.node.open>.row .chev{transform:rotate(90deg)}
.label{overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
.row.dir .label{color:var(--fg-2);letter-spacing:.02em}
.node.open>.row.dir .label,.row.dir:hover .label{color:var(--fg)}
.badge{color:var(--fg-3);font-size:10px;flex:0 0 auto;font-variant-numeric:tabular-nums}
.row.sel .badge{color:var(--accent-2)}
.hit{background:var(--accent-dim-2);border-radius:2px;color:var(--fg)}

.cat>.row{margin-top:8px}
.cat:first-child>.row{margin-top:2px}
.cat>.row .label{text-transform:uppercase;font-size:10.5px;letter-spacing:.09em}

.kids{
  display:grid;grid-template-rows:0fr;
  transition:grid-template-rows .22s cubic-bezier(.3,.8,.3,1);
}
.node.open>.kids{grid-template-rows:1fr}
.kids>div{overflow:hidden;min-height:0}
.kids .node,.kids>div>.row{padding-left:11px}
.kids .node{border-left:1px solid var(--line);margin-left:8px}
.kids .node:hover{border-left-color:var(--line-2)}

.cb{
  width:12px;height:12px;flex:0 0 auto;border-radius:3px;
  border:1px solid var(--line-2);background:var(--bg-2);
  display:grid;place-items:center;color:transparent;
  transition:background .14s,border-color .14s,color .14s,transform .14s;
}
.cb:hover{border-color:var(--accent)}
.cb.on{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.cb.on svg{animation:pop .18s cubic-bezier(.2,.9,.3,1.4)}
@keyframes pop{from{transform:scale(.4);opacity:0}}
@media (prefers-color-scheme: light){.cb.on{color:#fff}}

/* basket */
#basket{
  flex:0 0 auto;border-top:1px solid var(--line);background:var(--bg-2);
}
#basket .bhead{
  display:flex;align-items:center;gap:8px;height:30px;padding:0 10px;cursor:pointer;
}
#basket .bhead .t{letter-spacing:.06em;text-transform:uppercase;font-size:10.5px;color:var(--fg-2)}
#bcount{
  min-width:18px;text-align:center;border-radius:99px;padding:1px 6px;font-size:10px;
  background:var(--bg-3);color:var(--fg-3);border:1px solid var(--line-2);
  transition:background .2s,color .2s,border-color .2s;
}
#basket.live #bcount{background:var(--accent);border-color:var(--accent);color:var(--bg)}
@media (prefers-color-scheme: light){#basket.live #bcount{color:#fff}}
#bcount.bump{animation:bump .3s cubic-bezier(.2,.9,.3,1.6)}
@keyframes bump{40%{transform:scale(1.45)}}
#bbody{display:grid;grid-template-rows:0fr;transition:grid-template-rows .24s cubic-bezier(.3,.8,.3,1)}
#basket.open #bbody{grid-template-rows:1fr}
#bbody>div{overflow:hidden;min-height:0}
#blist{max-height:132px;overflow:auto;padding:0 10px 6px}
.bitem{
  display:flex;align-items:center;gap:6px;height:20px;color:var(--fg-2);
  animation:slidein .2s ease both;
}
@keyframes slidein{from{opacity:0;transform:translateX(-6px)}}
.bitem span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;cursor:pointer}
.bitem span:hover{color:var(--fg)}
.bitem button{color:var(--fg-3);display:grid;place-items:center}
.bitem button:hover{color:var(--bad)}
.brow{display:flex;gap:6px;padding:0 10px 10px;flex-wrap:wrap}
.bempty{padding:0 10px 10px;color:var(--fg-3)}

/* ---------- buttons ---------- */
.btn{
  display:inline-flex;align-items:center;gap:6px;
  height:24px;padding:0 9px;border-radius:5px;
  border:1px solid var(--line-2);background:var(--bg-3);color:var(--fg-2);
  white-space:nowrap;position:relative;overflow:hidden;
  transition:color .15s,border-color .15s,background .15s,transform .08s;
}
.btn:hover{color:var(--fg);border-color:var(--fg-3);background:var(--bg-2)}
.btn:active{transform:translateY(1px)}
.btn[disabled]{opacity:.4;pointer-events:none}
.btn .k{color:var(--fg-3);font-size:10px}
.btn.done{color:var(--accent);border-color:var(--accent);background:var(--accent-dim)}
.btn.done::after{
  content:"";position:absolute;inset:0;background:var(--accent);opacity:.22;
  animation:flash .5s ease-out forwards;
}
@keyframes flash{to{opacity:0}}
.btn.pri{border-color:var(--accent-dim-2);color:var(--accent)}
.btn.pri:hover{background:var(--accent-dim);border-color:var(--accent)}

/* ---------- right pane ---------- */
#right{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;background:var(--bg)}
#meta{
  flex:0 0 auto;border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,var(--panel),var(--bg-2));
  padding:10px 16px 8px;
}
#meta .path{color:var(--fg-3);font-size:11px;display:flex;align-items:center;gap:5px;flex-wrap:wrap}
#meta .path b{color:var(--fg-2);font-weight:400}
#meta h1{
  margin:3px 0 0;font-size:15px;font-weight:600;letter-spacing:-.01em;
  display:flex;align-items:center;gap:9px;
}
#meta .tags{display:flex;gap:8px;color:var(--fg-3);font-size:11px;margin-top:3px}
#meta .tags i{font-style:normal;color:var(--line-2)}
#copybar{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
#doc{
  flex:1;overflow:auto;padding:22px 30px 70px;min-height:0;
  scroll-behavior:smooth;
}
#docinner{max-width:760px}
#docinner.in{animation:fadeup .26s cubic-bezier(.2,.8,.3,1) both}
@keyframes fadeup{from{opacity:0;transform:translateY(6px)}}

/* markdown */
.md{font-size:12.5px;line-height:1.72;color:var(--fg-2)}
.md h1,.md h2,.md h3,.md h4{color:var(--fg);line-height:1.3;font-weight:600;letter-spacing:-.01em}
.md h1{font-size:19px;margin:26px 0 10px;padding-bottom:7px;border-bottom:1px solid var(--line)}
.md h2{font-size:15.5px;margin:24px 0 8px}
.md h3{font-size:13.5px;margin:20px 0 6px}
.md h4{font-size:12.5px;margin:16px 0 5px;color:var(--fg-2)}
.md h1:first-child,.md h2:first-child,.md h3:first-child{margin-top:0}
.md h2::before,.md h3::before{content:"#";color:var(--accent);opacity:.5;margin-right:7px}
.md p{margin:0 0 11px}
.md ul,.md ol{margin:0 0 11px;padding-left:20px}
.md li{margin:2px 0}
.md li::marker{color:var(--accent);opacity:.75}
.md hr{border:none;border-top:1px solid var(--line);margin:20px 0}
.md strong{color:var(--fg);font-weight:600}
.md code{
  background:var(--bg-3);border:1px solid var(--line);border-radius:4px;
  padding:1px 4px;font-size:11.5px;color:var(--accent-2);
}
.md pre{
  background:var(--bg-2);border:1px solid var(--line);border-radius:var(--radius);
  padding:11px 13px;overflow:auto;margin:0 0 13px;position:relative;
}
.md pre code{background:none;border:none;padding:0;color:var(--fg);font-size:11.5px;line-height:1.65}
.md pre .lang{
  position:absolute;top:0;right:0;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--fg-3);background:var(--bg-3);border-left:1px solid var(--line);
  border-bottom:1px solid var(--line);border-radius:0 var(--radius) 0 var(--radius);padding:2px 7px;
}
.md a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--accent-dim-2)}
.md a:hover{border-bottom-color:var(--accent)}

/* states */
.state{
  height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:11px;color:var(--fg-3);text-align:center;padding:30px;
  animation:fadeup .3s ease both;
}
.state .big{color:var(--fg-2);font-size:13px}
.state .why{max-width:420px;line-height:1.7}
.state code{
  background:var(--bg-3);border:1px solid var(--line);border-radius:4px;padding:1px 5px;color:var(--accent-2);
}
.state.err .glyph{color:var(--bad)}
.glyph{opacity:.8}
.panelnote{padding:14px 12px;color:var(--fg-3);line-height:1.7}
.panelnote b{color:var(--accent);font-weight:400;display:block;margin-bottom:5px}

.sk{padding:6px}
.sk i{
  display:block;height:12px;margin:8px 4px;border-radius:3px;
  background:linear-gradient(90deg,var(--bg-2),var(--bg-3),var(--bg-2));
  background-size:200% 100%;animation:shim 1.3s linear infinite;
}
@keyframes shim{to{background-position:-200% 0}}

#toast{
  position:fixed;left:50%;bottom:22px;transform:translate(-50%,14px);
  background:var(--bg-3);border:1px solid var(--accent);color:var(--accent);
  border-radius:99px;padding:6px 14px;pointer-events:none;opacity:0;
  transition:opacity .18s,transform .18s cubic-bezier(.2,.9,.3,1.4);z-index:9;
  box-shadow:0 6px 20px rgba(0,0,0,.35);
}
#toast.on{opacity:1;transform:translate(-50%,0)}

@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}
}
</style>
</head>
<body>
<div id="app">
  <header>
    <div class="brand"><span class="mark"></span><b>skills</b><span>browser</span></div>
    <div class="hspace"></div>
    <div class="hint"><kbd>type</kbd> filter <kbd>up</kbd><kbd>down</kbd> move <kbd>enter</kbd> open</div>
    <button class="pill" id="status" data-s="wait" title="click to retry"><span class="dot"></span><span id="statustext">connecting</span></button>
  </header>
  <main>
    <section id="left">
      <div class="filterwrap" id="filterwrap">
        <div class="fieldrow">
          <span class="caret" aria-hidden="true">
            <svg width="9" height="9" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 1.5 6 5 2 8.5"/></svg>
          </span>
          <input id="filter" type="text" placeholder="filter by title or path" autocomplete="off" spellcheck="false">
          <button id="clear" title="clear (esc)">
            <svg width="10" height="10" viewBox="0 0 10 10" stroke="currentColor" stroke-width="1.5"><path d="M1.5 1.5 8.5 8.5M8.5 1.5 1.5 8.5"/></svg>
          </button>
        </div>
        <div id="moderow"></div>
      </div>
      <div class="count"><span id="cleft">loading</span><em id="cright"></em></div>
      <div id="tree"><div class="sk"><i style="width:70%"></i><i style="width:52%"></i><i style="width:61%"></i><i style="width:44%"></i><i style="width:66%"></i><i style="width:50%"></i></div></div>
      <div id="basket">
        <div class="bhead" id="bhead">
          <svg class="chev" width="9" height="9" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.6" style="color:var(--fg-3);transition:transform .2s"><path d="M2 1.5 6 5 2 8.5"/></svg>
          <span class="t">basket</span><span id="bcount">0</span><span class="hspace"></span>
        </div>
        <div id="bbody"><div>
          <div id="blist"></div>
          <div class="brow" id="brow">
            <button class="btn pri" id="b-front">front-load block</button>
            <button class="btn" id="b-mentions">@mentions</button>
            <button class="btn" id="b-raw">all contents</button>
            <button class="btn" id="b-clear">clear</button>
          </div>
        </div></div>
      </div>
    </section>
    <div id="grip"></div>
    <section id="right">
      <div id="meta"></div>
      <div id="doc"></div>
    </section>
  </main>
</div>
<div id="toast"></div>

<script>
(function(){
"use strict";

var API_TREE = "/api/tree";
var API_FILE = "/api/file?path=";

var state = {
  files: [],
  tree: null,
  byPath: {},
  cache: {},
  open: {},
  basket: [],
  mode: "",
  filter: "",
  visible: [],
  hl: -1,
  sel: null,
  online: false
};

var $ = function(id){ return document.getElementById(id); };
var treeEl = $("tree"), metaEl = $("meta"), docEl = $("doc");

/* ---------------- utils ---------------- */
function esc(s){
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function icon(name){
  var s = '<svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">';
  if(name === "chev")  return '<svg class="chev" width="9" height="9" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2 1.5 6 5 2 8.5"/></svg>';
  if(name === "folder")return s + '<path d="M1 3.2A1 1 0 0 1 2 2.2h2.2l1 1.3H10a1 1 0 0 1 1 1v4.3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1z"/></svg>';
  if(name === "file")  return s + '<path d="M3 1.2h3.6L9.4 4v6.8H3z"/><path d="M6.5 1.4V4H9"/></svg>';
  if(name === "check") return '<svg width="8" height="8" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.6 5.2 4 7.6 8.4 2.6"/></svg>';
  if(name === "copy")  return s + '<rect x="4" y="4" width="6.6" height="6.8" rx="1"/><path d="M8 2H2.4a1 1 0 0 0-1 1v5.4"/></svg>';
  if(name === "x")     return '<svg width="9" height="9" viewBox="0 0 10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2 2 8 8M8 2 2 8"/></svg>';
  if(name === "plug")  return '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0z"/><path d="M12 16v5"/></svg>';
  if(name === "doc")   return '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2.5h7l5 5V21.5H6z"/><path d="M13 2.8V7.5h4.7M9 12h6M9 15.5h6M9 19h4"/></svg>';
  return "";
}
function fmtWords(n){
  if(n == null) return "";
  return n >= 1000 ? (n/1000).toFixed(1).replace(/\.0$/,"") + "k" : String(n);
}
function fmtDate(ts){
  if(!ts) return "";
  var d = new Date(ts * 1000);
  if(isNaN(d.getTime())) return "";
  var m = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return m[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
}
function toast(msg){
  var t = $("toast");
  t.textContent = msg;
  t.classList.add("on");
  clearTimeout(toast._t);
  toast._t = setTimeout(function(){ t.classList.remove("on"); }, 1400);
}
function copy(text, btn, label){
  var done = function(){
    if(btn){
      var old = btn.getAttribute("data-label") || btn.textContent;
      btn.setAttribute("data-label", old);
      btn.classList.add("done");
      btn.textContent = "copied";
      clearTimeout(btn._t);
      btn._t = setTimeout(function(){
        btn.classList.remove("done");
        btn.textContent = old;
      }, 1000);
    }
    toast("copied " + (label || "") );
  };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done, function(){ fallback(text); done(); });
  } else { fallback(text); done(); }
}
function fallback(text){
  var ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select();
  try{ document.execCommand("copy"); }catch(e){}
  document.body.removeChild(ta);
}

/* ---------------- markdown ---------------- */
function md(src){
  var text = String(src == null ? "" : src).replace(/\r\n?/g, "\n");
  var blocks = [];
  // pull fenced code out first, on the raw text
  text = text.replace(/```([^\n`]*)\n([\s\S]*?)```/g, function(m, lang, body){
    blocks.push({ lang: lang.trim(), body: body.replace(/\n$/, "") });
    return "\u0000BLOCK" + (blocks.length - 1) + "\u0000";
  });

  var lines = esc(text).split("\n");
  var out = [], i = 0;

  function inline(s){
    return s
      .replace(/`([^`]+)`/g, function(m, c){ return "<code>" + c + "</code>"; })
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/__([^_]+)__/g, "<strong>$1</strong>")
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }

  while(i < lines.length){
    var ln = lines[i];

    var bm = ln.match(/^\u0000BLOCK(\d+)\u0000\s*$/);
    if(bm){
      var b = blocks[+bm[1]];
      out.push('<pre>' + (b.lang ? '<span class="lang">' + esc(b.lang) + '</span>' : "") +
               "<code>" + esc(b.body) + "</code></pre>");
      i++; continue;
    }
    if(/^\s*$/.test(ln)){ i++; continue; }
    if(/^(---+|\*\*\*+|___+)\s*$/.test(ln)){ out.push("<hr>"); i++; continue; }

    var h = ln.match(/^(#{1,6})\s+(.*)$/);
    if(h){
      var lvl = Math.min(h[1].length, 4);
      out.push("<h" + lvl + ">" + inline(h[2].trim()) + "</h" + lvl + ">");
      i++; continue;
    }
    if(/^\s*([-*+])\s+/.test(ln)){
      var ul = [];
      while(i < lines.length && /^\s*([-*+])\s+/.test(lines[i])){
        ul.push("<li>" + inline(lines[i].replace(/^\s*[-*+]\s+/, "")) + "</li>");
        i++;
      }
      out.push("<ul>" + ul.join("") + "</ul>"); continue;
    }
    if(/^\s*\d+[.)]\s+/.test(ln)){
      var ol = [];
      while(i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])){
        ol.push("<li>" + inline(lines[i].replace(/^\s*\d+[.)]\s+/, "")) + "</li>");
        i++;
      }
      out.push("<ol>" + ol.join("") + "</ol>"); continue;
    }
    if(/^&gt;\s?/.test(ln)){
      var q = [];
      while(i < lines.length && /^&gt;\s?/.test(lines[i])){
        q.push(inline(lines[i].replace(/^&gt;\s?/, ""))); i++;
      }
      out.push('<p style="border-left:2px solid var(--accent);padding-left:10px;color:var(--fg-3)">' + q.join("<br>") + "</p>");
      continue;
    }
    var para = [];
    while(i < lines.length && !/^\s*$/.test(lines[i]) &&
          !/^\u0000BLOCK\d+\u0000\s*$/.test(lines[i]) &&
          !/^#{1,6}\s/.test(lines[i]) &&
          !/^\s*([-*+])\s+/.test(lines[i]) &&
          !/^\s*\d+[.)]\s+/.test(lines[i]) &&
          !/^(---+|\*\*\*+|___+)\s*$/.test(lines[i])){
      para.push(lines[i]); i++;
    }
    out.push("<p>" + inline(para.join(" ")) + "</p>");
  }
  return out.join("\n");
}

/* ---------------- tree build ---------------- */
function buildTree(files){
  var root = { name: "", dir: true, kids: [], map: {}, path: "" };
  files.forEach(function(f){
    var cat = f.category || (f.path.split("/")[0] || "misc");
    var parts = f.path.split("/");
    // ensure the category node is the top level even when path does not start with it
    var node = root;
    if(parts[0] !== cat){ parts.unshift(cat); }
    for(var i = 0; i < parts.length - 1; i++){
      var seg = parts[i];
      if(!node.map[seg]){
        var acc = node.path ? node.path + "/" + seg : seg;
        var d = { name: seg, dir: true, kids: [], map: {}, path: acc, depth: i, cat: i === 0 };
        node.map[seg] = d; node.kids.push(d);
      }
      node = node.map[seg];
    }
    node.kids.push({ name: parts[parts.length - 1], dir: false, file: f, path: f.path });
  });
  (function sort(n){
    n.kids.sort(function(a, b){
      if(a.dir !== b.dir) return a.dir ? -1 : 1;
      return (a.dir ? a.name : (a.file.title || a.name)).localeCompare(a.dir ? b.name : (b.file.title || b.name));
    });
    n.kids.forEach(function(k){ if(k.dir) sort(k); });
  })(root);
  return root;
}

function matches(f, q){
  if(state.mode && (f.modes || []).indexOf(state.mode) === -1) return false;
  if(!q) return true;
  return (f.path.toLowerCase().indexOf(q) !== -1) ||
         ((f.title || "").toLowerCase().indexOf(q) !== -1) ||
         ((f.tags || []).join(" ").toLowerCase().indexOf(q) !== -1);
}

/* the paste-able front-load instruction - mirrors scripts/library.py read_line() */
function readLine(paths){
  if(!paths || !paths.length) return "";
  var joined;
  if(paths.length === 1) joined = paths[0];
  else if(paths.length === 2) joined = paths[0] + " and " + paths[1];
  else joined = paths.slice(0, -1).join(", ") + ", and " + paths[paths.length - 1];
  return "Read " + joined + " in full for context.";
}

/* every mode declared anywhere in the library, core first then the phases */
function allModes(){
  var order = ["core","plan","code","debug","review","wrap"], seen = {}, out = [];
  state.files.forEach(function(f){ (f.modes || []).forEach(function(m){ seen[m] = 1; }); });
  order.forEach(function(m){ if(seen[m]){ out.push(m); delete seen[m]; } });
  Object.keys(seen).sort().forEach(function(m){ out.push(m); });
  return out;
}

/* stage exactly the files a mode loads, in declared order */
function pickMode(m){
  var hits = state.files.filter(function(f){ return (f.modes || []).indexOf(m) !== -1; });
  if(m !== "core") hits = hits.filter(function(f){ return (f.modes || []).indexOf("core") === -1; });
  hits.sort(function(a, b){ return (a.order - b.order) || a.path.localeCompare(b.path); });
  state.basket = hits.map(function(f){ return f.path; });
  renderBasket(true);
  render();
  toast(m + ": " + state.basket.length + " file" + (state.basket.length === 1 ? "" : "s") + " staged");
}
function mark(s, q){
  var e = esc(s);
  if(!q) return e;
  var idx = e.toLowerCase().indexOf(q);
  if(idx === -1) return e;
  return e.slice(0, idx) + '<span class="hit">' + e.slice(idx, idx + q.length) + "</span>" + e.slice(idx + q.length);
}

/* ---------------- render tree ---------------- */
function render(){
  var q = state.filter.trim().toLowerCase();
  state.visible = [];
  if(!state.tree){ return; }

  var shown = 0, total = state.files.length;

  function walk(node, depth){
    var frag = document.createDocumentFragment();
    node.kids.forEach(function(k){
      if(k.dir){
        var sub = walk(k, depth + 1);
        if(!sub.count) return;
        shown += 0;
        var wrap = document.createElement("div");
        wrap.className = "node" + (k.cat ? " cat" : "");
        var openState = q ? true : (state.open[k.path] !== false);
        if(openState) wrap.classList.add("open");
        var row = document.createElement("div");
        row.className = "row dir";
        row.innerHTML = icon("chev") + '<span class="ic">' + icon("folder") + "</span>" +
                        '<span class="label">' + mark(k.name, q) + "</span>" +
                        '<span class="badge">' + sub.count + "</span>";
        row.addEventListener("click", function(){
          var isOpen = wrap.classList.toggle("open");
          state.open[k.path] = isOpen;
        });
        var kids = document.createElement("div");
        kids.className = "kids";
        var inner = document.createElement("div");
        inner.appendChild(sub.frag);
        kids.appendChild(inner);
        wrap.appendChild(row); wrap.appendChild(kids);
        frag.appendChild(wrap);
        var c = sub.count;
        return c;
      } else {
        if(!matches(k.file, q)) return;
        var f = k.file;
        var r = document.createElement("div");
        r.className = "row file";
        r.dataset.path = f.path;
        var on = state.basket.indexOf(f.path) !== -1;
        r.innerHTML = '<span class="cb' + (on ? " on" : "") + '">' + icon("check") + "</span>" +
                      '<span class="ic">' + icon("file") + "</span>" +
                      '<span class="label">' + mark(f.title || k.name, q) + "</span>" +
                      '<span class="badge">' + fmtWords(f.words) + "</span>";
        if(state.sel === f.path) r.classList.add("sel");
        r.querySelector(".cb").addEventListener("click", function(ev){
          ev.stopPropagation();
          toggleBasket(f.path);
        });
        r.addEventListener("click", function(){ open(f.path); });
        frag.appendChild(r);
        state.visible.push(f.path);
      }
    });
    var count = 0;
    // count files under this node that pass the filter
    (function cnt(n){
      n.kids.forEach(function(k){ if(k.dir) cnt(k); else if(matches(k.file, q)) count++; });
    })(node);
    return { frag: frag, count: count };
  }

  var res = walk(state.tree, 0);
  treeEl.innerHTML = "";
  if(res.count === 0){
    var e = document.createElement("div");
    e.className = "panelnote";
    e.innerHTML = "no files match <code>" + esc(state.filter) + "</code>";
    treeEl.appendChild(e);
  } else {
    treeEl.appendChild(res.frag);
  }
  shown = res.count;
  $("cleft").textContent = shown === total ? total + " files" : shown + " of " + total + " files";
  $("cright").textContent = state.basket.length ? state.basket.length + " in basket" : "";
  applyHl();
}

function applyHl(){
  var rows = treeEl.querySelectorAll(".row.file");
  for(var i = 0; i < rows.length; i++) rows[i].classList.remove("hl");
  if(state.hl < 0 || state.hl >= state.visible.length) return;
  var p = state.visible[state.hl];
  var row = treeEl.querySelector('.row.file[data-path="' + cssEsc(p) + '"]');
  if(!row) return;
  row.classList.add("hl");
  var rt = row.offsetTop, rb = rt + row.offsetHeight;
  if(rt < treeEl.scrollTop + 4) treeEl.scrollTop = rt - 4;
  else if(rb > treeEl.scrollTop + treeEl.clientHeight - 4) treeEl.scrollTop = rb - treeEl.clientHeight + 4;
}
function cssEsc(s){ return s.replace(/["\\]/g, "\\$&"); }

/* ---------------- mode chips ---------------- */
function renderModes(){
  var row = $("moderow"), modes = allModes();
  row.innerHTML = "";
  if(!modes.length) return;
  modes.forEach(function(m){
    var n = state.files.filter(function(f){ return (f.modes || []).indexOf(m) !== -1; }).length;
    var b = document.createElement("button");
    b.className = "mchip" + (state.mode === m ? " on" : "");
    b.innerHTML = esc(m) + '<span class="n">' + n + "</span>";
    b.title = "click: filter the tree to " + m + "\ndouble-click: stage " + m + "'s read line";
    b.addEventListener("click", function(){
      state.mode = (state.mode === m) ? "" : m;
      renderModes(); render();
    });
    b.addEventListener("dblclick", function(){ pickMode(m); });
    row.appendChild(b);
  });
}

/* ---------------- basket ---------------- */
function toggleBasket(path){
  var i = state.basket.indexOf(path);
  if(i === -1) state.basket.push(path); else state.basket.splice(i, 1);
  renderBasket(true);
  var row = treeEl.querySelector('.row.file[data-path="' + cssEsc(path) + '"]');
  if(row) row.querySelector(".cb").classList.toggle("on", state.basket.indexOf(path) !== -1);
  $("cright").textContent = state.basket.length ? state.basket.length + " in basket" : "";
}
function renderBasket(bump){
  var b = $("basket"), list = $("blist"), n = state.basket.length;
  $("bcount").textContent = n;
  b.classList.toggle("live", n > 0);
  if(n > 0) b.classList.add("open");
  if(bump){
    var c = $("bcount");
    c.classList.remove("bump"); void c.offsetWidth; c.classList.add("bump");
  }
  $("b-front").disabled = !n; $("b-mentions").disabled = !n; $("b-raw").disabled = !n; $("b-clear").disabled = !n;
  if(!n){
    list.innerHTML = '<div class="bempty">check files in the tree to stage them here</div>';
    return;
  }
  list.innerHTML = "";
  state.basket.forEach(function(p){
    var d = document.createElement("div");
    d.className = "bitem";
    d.innerHTML = '<span title="' + esc(p) + '">' + esc(p) + "</span><button title=\"remove\">" + icon("x") + "</button>";
    d.querySelector("span").addEventListener("click", function(){ open(p); });
    d.querySelector("button").addEventListener("click", function(){ toggleBasket(p); render(); });
    list.appendChild(d);
  });
}

/* ---------------- api ---------------- */
function setStatus(s, text){
  var p = $("status");
  p.dataset.s = s;
  $("statustext").textContent = text;
  state.online = (s === "up");
}
function loadTree(){
  setStatus("wait", "connecting");
  treeEl.innerHTML = '<div class="sk"><i style="width:70%"></i><i style="width:52%"></i><i style="width:61%"></i><i style="width:44%"></i><i style="width:66%"></i></div>';
  fetch(API_TREE, { cache: "no-store" })
    .then(function(r){ if(!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function(data){
      var files = (data && data.files) || [];
      state.files = files;
      state.byPath = {};
      files.forEach(function(f){ state.byPath[f.path] = f; });
      state.tree = buildTree(files);
      setStatus("up", "backend up");
      renderModes();
      render();
      if(!state.sel) emptyDoc();
    })
    .catch(function(err){
      setStatus("down", "backend down");
      state.files = []; state.tree = null;
      $("cleft").textContent = "no data";
      treeEl.innerHTML = '<div class="panelnote"><b>backend not running</b>' +
        "could not reach <code>" + esc(API_TREE) + "</code> (" + esc(err.message) + ").<br>" +
        "start the local server, then retry.</div>";
      var btn = document.createElement("div");
      btn.style.padding = "0 12px";
      btn.innerHTML = '<button class="btn pri">retry</button>';
      btn.querySelector("button").addEventListener("click", loadTree);
      treeEl.appendChild(btn);
      offlineDoc();
    });
}
function getFile(path){
  if(state.cache[path]) return Promise.resolve(state.cache[path]);
  return fetch(API_FILE + encodeURIComponent(path), { cache: "no-store" })
    .then(function(r){ if(!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function(d){
      var c = (d && d.content) || "";
      state.cache[path] = c;
      if(!state.online) setStatus("up", "backend up");
      return c;
    });
}

/* ---------------- right pane ---------------- */
function emptyDoc(){
  metaEl.innerHTML = "";
  metaEl.style.display = "none";
  docEl.innerHTML = '<div class="state"><span class="glyph">' + icon("doc") + "</span>" +
    '<div class="big">no file selected</div>' +
    '<div class="why">pick a skill from the tree, or just start typing to filter. ' +
    'up / down moves, enter opens.</div></div>';
}
function offlineDoc(){
  metaEl.style.display = "none";
  metaEl.innerHTML = "";
  docEl.innerHTML = '<div class="state err"><span class="glyph">' + icon("plug") + "</span>" +
    '<div class="big">backend not running</div>' +
    '<div class="why">this page is frontend only. it expects <code>GET /api/tree</code> and ' +
    '<code>GET /api/file?path=</code> on the same origin. start the local python server and hit retry ' +
    'in the header.</div></div>';
}

function copyButtons(f, content){
  var bar = document.createElement("div");
  bar.id = "copybar";
  var defs = [
    { label: "path",      key: "1", get: function(){ return f.path; } },
    { label: "@mention",  key: "2", get: function(){ return "@" + f.path; } },
    { label: "front-load",key: "3", get: function(){ return readLine([f.path]); } },
    { label: "contents",  key: "4", get: function(){ return content ? fence(f.path, content) : null; } }
  ];
  defs.forEach(function(d){
    var b = document.createElement("button");
    b.className = "btn" + (d.label === "front-load" ? " pri" : "");
    b.innerHTML = '<span class="ic">' + icon("copy") + '</span>' + d.label + '<span class="k">' + d.key + "</span>";
    b.setAttribute("data-label", d.label);
    b.addEventListener("click", function(){
      var v = d.get();
      if(v == null){
        getFile(f.path).then(function(c){ copyBtn(b, fence(f.path, c), d.label); })
          .catch(function(){ toast("could not fetch contents"); });
        return;
      }
      copyBtn(b, v, d.label);
    });
    bar.appendChild(b);
  });
  return bar;
}
function copyBtn(btn, text, label){
  var inner = btn.innerHTML;
  btn.classList.add("done");
  btn.textContent = "copied " + label;
  clearTimeout(btn._t);
  btn._t = setTimeout(function(){ btn.classList.remove("done"); btn.innerHTML = inner; }, 1000);
  if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).catch(function(){ fallback(text); });
  else fallback(text);
  toast("copied " + label);
}
function fence(path, content){
  return "```markdown\n" + content.replace(/\s+$/, "") + "\n```";
}

function open(path){
  var f = state.byPath[path];
  if(!f) return;
  state.sel = path;
  var idx = state.visible.indexOf(path);
  if(idx !== -1) state.hl = idx;
  var rows = treeEl.querySelectorAll(".row.file");
  for(var i = 0; i < rows.length; i++) rows[i].classList.toggle("sel", rows[i].dataset.path === path);
  applyHl();

  metaEl.style.display = "";
  metaEl.innerHTML = "";
  var crumbs = f.path.split("/");
  var head = document.createElement("div");
  head.innerHTML =
    '<div class="path">' + crumbs.map(function(c, i){
      return (i === crumbs.length - 1 ? "<b>" + esc(c) + "</b>" : esc(c));
    }).join(' <span style="color:var(--line-2)">/</span> ') + "</div>" +
    "<h1>" + esc(f.title || crumbs[crumbs.length - 1]) + "</h1>" +
    '<div class="tags"><span>' + esc(f.category || "") + "</span><i>|</i><span>" +
      fmtWords(f.words) + " words</span>" +
      (f.mtime ? '<i>|</i><span>' + esc(fmtDate(f.mtime)) + "</span>" : "") +
      ((f.modes || []).length ? '<i>|</i><span>modes: ' + esc(f.modes.join(", ")) + "</span>" : "") +
    "</div>";
  metaEl.appendChild(head);
  if((f.tags || []).length){
    var tr = document.createElement("div");
    tr.className = "tagrow";
    f.tags.forEach(function(t){
      var b = document.createElement("button");
      b.className = "tag"; b.textContent = t;
      b.title = "filter by " + t;
      b.addEventListener("click", function(){
        state.filter = t; $("filter").value = t;
        $("filterwrap").classList.add("has"); render();
      });
      tr.appendChild(b);
    });
    head.appendChild(tr);
  }
  metaEl.appendChild(copyButtons(f, state.cache[f.path]));

  docEl.innerHTML = '<div class="sk" style="max-width:700px"><i style="width:40%;height:18px"></i><i style="width:92%"></i><i style="width:88%"></i><i style="width:70%"></i><i style="width:80%"></i></div>';
  getFile(f.path).then(function(c){
    if(state.sel !== path) return;
    var wrap = document.createElement("div");
    wrap.id = "docinner"; wrap.className = "md in";
    wrap.innerHTML = md(c);
    docEl.innerHTML = "";
    docEl.appendChild(wrap);
    docEl.scrollTop = 0;
    metaEl.replaceChild(copyButtons(f, c), $("copybar"));
  }).catch(function(err){
    if(state.sel !== path) return;
    docEl.innerHTML = '<div class="state err"><span class="glyph">' + icon("plug") + "</span>" +
      '<div class="big">could not load this file</div>' +
      '<div class="why"><code>' + esc(API_FILE + encodeURIComponent(f.path)) + "</code> failed (" +
      esc(err.message) + "). the backend may not be running.</div></div>";
    setStatus("down", "backend down");
  });
}

/* ---------------- basket copy ---------------- */
function basketFront(){
  return readLine(state.basket);
}
function basketMentions(){
  // just the paths as @mentions, one per line - a lightweight reference list
  return state.basket.map(function(p){ return "@" + p; }).join("\n");
}
function basketRaw(){
  return Promise.all(state.basket.map(function(p){
    return getFile(p).then(function(c){ return "# " + p + "\n\n```markdown\n" + c.replace(/\s+$/, "") + "\n```"; });
  })).then(function(parts){ return parts.join("\n\n"); });
}

/* ---------------- events ---------------- */
$("filter").addEventListener("input", function(e){
  state.filter = e.target.value;
  $("filterwrap").classList.toggle("has", !!state.filter);
  state.hl = state.filter ? 0 : -1;
  render();
});
$("clear").addEventListener("click", function(){
  state.filter = ""; $("filter").value = "";
  $("filterwrap").classList.remove("has");
  render(); $("filter").focus();
});
$("status").addEventListener("click", loadTree);
$("bhead").addEventListener("click", function(){ $("basket").classList.toggle("open"); });
$("b-front").addEventListener("click", function(){
  copyBtn(this, basketFront(), state.basket.length + " front-load lines");
});
$("b-mentions").addEventListener("click", function(){
  copyBtn(this, basketMentions(), state.basket.length + " mentions");
});
$("b-raw").addEventListener("click", function(){
  var btn = this;
  basketRaw().then(function(t){ copyBtn(btn, t, state.basket.length + " files"); })
    .catch(function(){ toast("could not fetch all contents"); });
});
$("b-clear").addEventListener("click", function(){
  state.basket = []; renderBasket(true); render();
});

document.addEventListener("keydown", function(e){
  var inField = /^(INPUT|TEXTAREA)$/.test(e.target.tagName);
  if(e.key === "Escape"){
    if(state.filter){ state.filter = ""; $("filter").value = ""; $("filterwrap").classList.remove("has"); render(); }
    else $("filter").blur();
    return;
  }
  if(e.key === "ArrowDown" || e.key === "ArrowUp"){
    if(!state.visible.length) return;
    e.preventDefault();
    var d = e.key === "ArrowDown" ? 1 : -1;
    state.hl = state.hl < 0 ? (d > 0 ? 0 : state.visible.length - 1)
                            : (state.hl + d + state.visible.length) % state.visible.length;
    applyHl();
    return;
  }
  if(e.key === "Enter"){
    if(state.hl >= 0 && state.visible[state.hl]){ e.preventDefault(); open(state.visible[state.hl]); }
    return;
  }
  if(inField) return;
  if(e.key === " " && state.hl >= 0){ e.preventDefault(); toggleBasket(state.visible[state.hl]); return; }
  if(!e.metaKey && !e.ctrlKey && !e.altKey && /^[0-9]$/.test(e.key) && state.sel){
    var b = metaEl.querySelectorAll("#copybar .btn")[+e.key - 1];
    if(b){ e.preventDefault(); b.click(); return; }
  }
  if(!e.metaKey && !e.ctrlKey && !e.altKey && e.key.length === 1){
    $("filter").focus();
  }
});

/* resizer */
(function(){
  var g = $("grip"), left = $("left"), dragging = false;
  g.addEventListener("mousedown", function(e){
    dragging = true; g.classList.add("drag");
    document.body.style.cursor = "col-resize"; e.preventDefault();
  });
  window.addEventListener("mousemove", function(e){
    if(!dragging) return;
    var w = Math.min(620, Math.max(220, e.clientX));
    left.style.width = w + "px";
  });
  window.addEventListener("mouseup", function(){
    if(!dragging) return;
    dragging = false; g.classList.remove("drag"); document.body.style.cursor = "";
  });
})();

renderBasket(false);
emptyDoc();
loadTree();
})();
</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser(description="Browse the clutch skill libraries.")
    ap.add_argument("--port", type=int, default=0, help="port to bind (default: a free one)")
    ap.add_argument("--no-open", action="store_true", help="don't auto-open the browser")
    args = ap.parse_args()

    Handler.roots = load_roots()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = "http://127.0.0.1:{}/".format(server.server_address[1])
    print("skills-browser serving {} libraries at {}".format(len(Handler.roots), url))
    print("roots: {}".format(", ".join(Handler.roots)))
    print("Ctrl-C to stop.")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
