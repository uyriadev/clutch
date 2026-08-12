"""Is this project running the current clutch, or has it fallen behind?

Nothing here auto-installs. It reports, and the AI relays the report to the user,
because an update rewrites files in the project and that is the user's call.

    python .clutch/scripts/doctor.py          # human-readable verdict
    python .clutch/scripts/doctor.py --quiet  # exit code only

Exit codes: 0 current, 1 update available, 2 cannot tell (no global store).

Two things drift independently:

  toolkit  - the scripts in .clutch/scripts vs the published copy in the global
             store. Behind means you are running old code. Fix: `clutch init`.
  bundle   - AI.md vs the library files and config it was built from. Behind means
             the AI is reading stale rules. Fix: `python .clutch/export.py`.

Stdlib only; Python 3.8+.
"""
import hashlib
import sys
from pathlib import Path

from _common import AI_ROOT, global_dir, load_config

STAMP = "<!-- clutch-fingerprint: "


def digest(paths):
    """Order-independent content hash over a set of files."""
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: x.as_posix()):
        try:
            h.update(p.read_bytes())
        except OSError:
            continue
    return h.hexdigest()[:16]


def toolkit_state(cfg):
    """(local_hash, published_hash) for the toolkit scripts, or (None, None)."""
    local = AI_ROOT / "scripts"
    published = global_dir(cfg) / "toolkit" / "scripts"
    if not published.is_dir():
        return None, None
    names = {p.name for p in published.glob("*.py")}
    if not names:
        return None, None
    return (digest([local / n for n in names if (local / n).exists()]),
            digest([published / n for n in names]))


def library_fingerprint(cfg):
    """Hash of every library file + config that feeds the bundle."""
    files = []
    for root in ("prompts", "guides", "rules"):
        for base in (AI_ROOT / root, global_dir(cfg) / root):
            if base.is_dir():
                files.extend(base.rglob("*.md"))
                break  # local wins, same rule the readers use
    cfg_file = AI_ROOT / "config.json"
    if cfg_file.exists():
        files.append(cfg_file)
    return digest(files)


def stamped_fingerprint():
    """The fingerprint export.py recorded in AI.md, or None."""
    bundle = AI_ROOT / "AI.md"
    if not bundle.exists():
        return None
    for line in bundle.read_text(encoding="utf-8").splitlines()[:40]:
        if line.startswith(STAMP):
            return line[len(STAMP):].split(" ")[0].strip()
    return None


def check():
    """Returns (code, list of (severity, message, fix))."""
    cfg = load_config()
    findings = []

    if not global_dir(cfg).is_dir():
        return 2, [("unknown",
                    f"no global store at {global_dir(cfg)}",
                    "run `clutch init` in this project")]

    local_tk, pub_tk = toolkit_state(cfg)
    if local_tk is None:
        findings.append(("unknown", "no published toolkit to compare against",
                         "run `clutch update` from the clutch source repo"))
    elif local_tk != pub_tk:
        findings.append(("stale", "toolkit scripts differ from the published copy",
                         "clutch init"))

    live, stamped = library_fingerprint(cfg), stamped_fingerprint()
    if stamped is None:
        findings.append(("stale", "AI.md has no fingerprint (built by an older clutch)",
                         "python .clutch/export.py"))
    elif live != stamped:
        findings.append(("stale", "AI.md is out of date with the libraries or config",
                         "python .clutch/export.py"))

    if not findings:
        return 0, []
    return (1 if any(s == "stale" for s, *_ in findings) else 2), findings


def main():
    quiet = "--quiet" in sys.argv
    code, findings = check()
    if quiet:
        return code
    if code == 0:
        print("clutch doctor: current. Toolkit and bundle both match the global store.")
        return 0
    print("clutch doctor: UPDATE NEEDED\n")
    for sev, msg, fix in findings:
        print(f"  [{sev}] {msg}")
        print(f"          fix: {fix}\n")
    print("Tell the user this before doing further work - they decide whether to run it.")
    return code


if __name__ == "__main__":
    sys.exit(main())
