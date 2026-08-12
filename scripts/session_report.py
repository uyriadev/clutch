"""Extract what actually happened in a Claude Code session - from the transcript.

Reads the real `.claude` session JSONL for this project and pulls out the facts a
report needs: the conversation id, the human requests, the chapter markers, every
file touched, git commits, tools used, and errors. No guessing - it's mined from the
transcript, so reports and history notes are grounded in what was actually done.

    python .clutch/scripts/session_report.py               # newest session -> reports/
    python .clutch/scripts/session_report.py --list        # list this project's sessions
    python .clutch/scripts/session_report.py --session 04ce6e3a   # a specific one (prefix ok)
    python .clutch/scripts/session_report.py --json --stdout       # machine-readable
    python .clutch/scripts/session_report.py --history     # fill today's history notes
    python .clutch/scripts/session_report.py --verbose     # include the full command list

Claude's session store is %USERPROFILE%\\.claude\\projects\\<encoded-cwd>\\<id>.jsonl
(override with --claude-dir or the CLAUDE_CONFIG_DIR env var). Stdlib only; 3.8+.
"""
import argparse
import datetime
import json
import os
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

from _common import AI_ROOT, REPO_ROOT, load_config, project_name

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
CMD_TOOLS = {"Bash", "PowerShell"}
CHAPTER_TOOL = "mcp__ccd_session__mark_chapter"


def claude_projects_dir(args):
    base = (args.claude_dir or os.environ.get("CLAUDE_CONFIG_DIR")
            or str(Path.home() / ".claude"))
    return Path(base) / "projects"


def encode_cwd(path: Path):
    """Claude encodes the project path by replacing : / \\ with '-'."""
    return re.sub(r"[:/\\]", "-", str(path))


def candidate_roots(args):
    """Claude keys the transcript dir by its working directory. The most reliable
    signal is the cwd the command is run from; fall back to the repo/AI roots."""
    roots = []
    if args.project_dir:
        roots.append(Path(args.project_dir).resolve())
    for r in (Path.cwd(), REPO_ROOT, AI_ROOT):
        roots.append(r.resolve())
    seen, out = set(), []
    for r in roots:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def session_files(args):
    base = claude_projects_dir(args)
    for root in candidate_roots(args):
        proj_dir = base / encode_cwd(root)
        if proj_dir.is_dir():
            fs = sorted(proj_dir.glob("*.jsonl"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
            if fs:
                return proj_dir, fs
    return base / encode_cwd(candidate_roots(args)[0]), []


def iter_events(path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _text_blocks(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content
                       if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _commit_subject(cmd):
    # handle combined short flags (-qm, -am) and an optional @ before the quote
    m = re.search(r"-\w*m\s+@?(['\"])(.+?)\1", cmd, re.DOTALL)
    if m:
        for line in m.group(2).splitlines():
            if line.strip():
                return line.strip()
    m = re.search(r"commit\b.*?<<[-']*\w+\s*\n\s*(.+)", cmd, re.DOTALL)  # heredoc
    if m:
        return m.group(1).splitlines()[0].strip()
    return "(git commit)"


def extract(path):
    d = {
        "conversation_id": path.stem,
        "title": None, "branch": None, "cwd": None, "version": None,
        "started": None, "ended": None, "events": 0,
        "requests": [], "chapters": [], "files": OrderedDict(),
        "commits": [], "commands": [], "tools": Counter(),
        "errors": 0, "error_samples": [], "artifacts": [], "todos": None,
    }
    for e in iter_events(path):
        d["events"] += 1
        t = e.get("type")
        ts = e.get("timestamp")
        if ts:
            d["started"] = min(d["started"], ts) if d["started"] else ts
            d["ended"] = max(d["ended"], ts) if d["ended"] else ts
        if e.get("gitBranch"):
            d["branch"] = e["gitBranch"]
        if e.get("cwd"):
            d["cwd"] = e["cwd"]
        if e.get("version"):
            d["version"] = e["version"]
        if t == "custom-title":
            d["title"] = e.get("customTitle") or d["title"]
            continue
        msg = e.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")

        if t == "user":
            origin = e.get("origin") or {}
            if (isinstance(content, str) and not e.get("isMeta")
                    and origin.get("kind") == "human"):
                d["requests"].append({"time": ts, "text": content.strip()})
            elif isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result" \
                            and b.get("is_error"):
                        d["errors"] += 1
                        if len(d["error_samples"]) < 5:
                            d["error_samples"].append(_text_blocks(
                                b.get("content"))[:200])
            continue

        if t == "assistant" and isinstance(content, list):
            for b in content:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name = b.get("name", "?")
                inp = b.get("input") or {}
                d["tools"][name] += 1
                if name in EDIT_TOOLS:
                    fp = inp.get("file_path")
                    if fp:
                        op = "write" if name == "Write" else "edit"
                        rec = d["files"].setdefault(fp, {"write": 0, "edit": 0})
                        rec[op] += 1
                elif name in CMD_TOOLS:
                    cmd = (inp.get("command") or "").strip()
                    d["commands"].append({"tool": name, "command": cmd,
                                          "desc": inp.get("description", "")})
                    if re.search(r"\bgit\s+commit\b", cmd):
                        d["commits"].append(_commit_subject(cmd))
                elif name == CHAPTER_TOOL:
                    d["chapters"].append({"title": inp.get("title", ""),
                                          "summary": inp.get("summary", "")})
                elif name == "SendUserFile":
                    for f in inp.get("files", []):
                        d["artifacts"].append(f)
                elif name == "TodoWrite":
                    d["todos"] = inp.get("todos")
    return d


def _fmt_duration(a, b):
    try:
        pa = datetime.datetime.fromisoformat(a.replace("Z", "+00:00"))
        pb = datetime.datetime.fromisoformat(b.replace("Z", "+00:00"))
        secs = int((pb - pa).total_seconds())
        h, m = divmod(secs // 60, 60)
        return f"{h}h {m}m" if h else f"{m}m"
    except Exception:
        return "?"


def _short_time(ts):
    try:
        return datetime.datetime.fromisoformat(
            ts.replace("Z", "+00:00")).strftime("%H:%M")
    except Exception:
        return "--:--"


def render_md(d, proj, verbose=False):
    L = [f"# Session report - {proj}", ""]
    span = ""
    if d["started"] and d["ended"]:
        span = f" - {d['started'][:16].replace('T', ' ')} -> {d['ended'][11:16]} " \
               f"({_fmt_duration(d['started'], d['ended'])})"
    L += [
        f"- **Conversation:** `{d['conversation_id']}`",
        f"- **Title:** {d['title'] or '(none)'}",
        f"- **Branch:** {d['branch'] or '(n/a)'} - {d['events']} events{span}",
    ]
    L.append("")

    L.append(f"## Requests ({len(d['requests'])})")
    for i, r in enumerate(d["requests"], 1):
        text = " ".join(r["text"].split())
        if len(text) > 160:
            text = text[:157] + "..."
        L.append(f"{i}. [{_short_time(r['time'])}] {text}")
    L.append("")

    if d["chapters"]:
        L.append(f"## Chapters ({len(d['chapters'])})")
        for c in d["chapters"]:
            s = f" - {c['summary']}" if c.get("summary") else ""
            L.append(f"- **{c['title']}**{s}")
        L.append("")

    L.append(f"## Files changed ({len(d['files'])})")
    for fp, r in d["files"].items():
        ops = ", ".join(f"{k} x{v}" for k, v in r.items() if v)
        L.append(f"- `{fp}` ({ops})")
    L.append("")

    L.append(f"## Commits ({len(d['commits'])})")
    for c in d["commits"]:
        L.append(f"- {c}")
    if not d["commits"]:
        L.append("- (none)")
    L.append("")

    n_cmd = len(d["commands"])
    by_tool = Counter(c["tool"] for c in d["commands"])
    L.append(f"## Commands ({n_cmd})")
    L.append("- " + (", ".join(f"{k} x{v}" for k, v in by_tool.items()) or "(none)"))
    if verbose:
        for c in d["commands"]:
            first = c["command"].splitlines()[0] if c["command"] else ""
            L.append(f"  - `{first}`" + (f"  - {c['desc']}" if c["desc"] else ""))
    L.append("")

    if d["tools"]:
        L.append("## Tools used")
        L.append(", ".join(f"{k} x{v}" for k, v in d["tools"].most_common()))
        L.append("")

    if d["artifacts"]:
        L.append("## Files sent to user")
        for a in d["artifacts"]:
            L.append(f"- `{a}`")
        L.append("")

    L.append("## Issues")
    L.append(f"- Tool calls returning an error/non-zero result: {d['errors']}")
    for s in d["error_samples"]:
        L.append(f"  - {' '.join(s.split())[:140]}")
    L.append("")

    L.append("<!-- Generated by session_report.py from the .claude transcript. "
             "Facts are extracted, not inferred. -->")
    return "\n".join(L) + "\n"


def history_block(d):
    files = ", ".join(f"`{Path(f).name}`" for f in list(d["files"])[:12])
    lines = ["**Session notes (extracted from transcript "
             f"`{d['conversation_id'][:8]}`):**", ""]
    if d["requests"]:
        lines.append("_Requests:_")
        for r in d["requests"]:
            text = " ".join(r["text"].split())
            lines.append(f"- {text[:140]}")
        lines.append("")
    if d["chapters"]:
        lines.append("_Chapters:_ " + " - ".join(c["title"] for c in d["chapters"]))
    lines.append(f"_Files changed ({len(d['files'])}):_ {files}"
                 + ("..." if len(d["files"]) > 12 else ""))
    if d["commits"]:
        lines.append(f"_Commits:_ {len(d['commits'])} - "
                     + "; ".join(d["commits"][:5]))
    return "\n".join(lines)


def fill_history(d):
    hist = AI_ROOT / "history"
    files = sorted(hist.glob("*.md")) if hist.is_dir() else []
    if not files:
        return "no history file to update (push first, or run history.py)"
    newest = files[-1]
    text = newest.read_text(encoding="utf-8")
    block = history_block(d)
    new = re.sub(r"<!--\s*notes:.*?-->", block, text, count=1, flags=re.DOTALL)
    if new == text:
        newest.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
        return f"appended transcript notes to {newest.name}"
    newest.write_text(new, encoding="utf-8")
    return f"filled notes placeholder in {newest.name}"


def main():
    ap = argparse.ArgumentParser(description="Report what a Claude session actually did.")
    ap.add_argument("--session", help="conversation id or prefix (default: newest)")
    ap.add_argument("--list", action="store_true", help="list this project's sessions")
    ap.add_argument("--json", action="store_true", help="output extracted data as JSON")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing a file")
    ap.add_argument("--history", action="store_true",
                    help="write the extracted summary into the newest history entry")
    ap.add_argument("--verbose", action="store_true", help="include the full command list")
    ap.add_argument("--claude-dir", help="override the .claude dir (default: ~/.claude)")
    ap.add_argument("--project-dir", help="project root whose transcript to read "
                    "(default: current directory)")
    args = ap.parse_args()

    try:  # reports contain ->, x, ... - never let a legacy stdout codepage crash us
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    cfg = load_config()
    proj = project_name(cfg)
    proj_dir, files = session_files(args)
    if not files:
        raise SystemExit(f"no sessions found in {proj_dir}\n"
                         "  (is this the project root? try --claude-dir)")

    if args.list:
        print(f"sessions for {proj} ({proj_dir}):")
        for p in files:
            title = ""
            for e in iter_events(p):
                if e.get("type") == "custom-title":
                    title = e.get("customTitle", "")
            when = datetime.datetime.fromtimestamp(
                p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  {p.stem}  {when}  {title}")
        return

    chosen = files[0]
    if args.session:
        match = [p for p in files if p.stem.startswith(args.session)]
        if not match:
            raise SystemExit(f"no session matching '{args.session}' (try --list)")
        chosen = match[0]

    d = extract(chosen)

    if args.history:
        print("session_report: " + fill_history(d))

    if args.json:
        payload = json.dumps(d, indent=2, ensure_ascii=False)
        if args.stdout:
            print(payload)
        else:
            out = AI_ROOT / "reports" / f"{d['conversation_id'][:8]}.json"
            out.parent.mkdir(exist_ok=True)
            out.write_text(payload, encoding="utf-8")
            print(f"wrote {out}")
        return

    md = render_md(d, proj, verbose=args.verbose)
    if args.stdout:
        print(md)
        return
    today = datetime.date.fromtimestamp(chosen.stat().st_mtime).isoformat()
    out = AI_ROOT / "reports" / f"{today}-{d['conversation_id'][:8]}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}  ({len(d['requests'])} requests, {len(d['files'])} files, "
          f"{len(d['commits'])} commits)")


if __name__ == "__main__":
    main()
