"""Shared helpers for .clutch scripts. Stdlib only; Python 3.8+."""
import json
import subprocess
import sys
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parent.parent   # the .clutch folder
REPO_ROOT = AI_ROOT.parent


def load_config():
    cfg = {"project": None, "global_dir": None, "max_diff_chars": 60000}
    cfg_file = AI_ROOT / "config.json"
    if cfg_file.exists():
        try:
            cfg.update(json.loads(cfg_file.read_text(encoding="utf-8")))
        except json.JSONDecodeError as e:
            sys.exit(f"error: {cfg_file} is not valid JSON: {e}")
    return cfg


def git(*args, check=True):
    """Run git in the repo root and return stdout as text."""
    proc = subprocess.run(
        ["git", *args], cwd=str(REPO_ROOT),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if check and proc.returncode != 0:
        sys.exit(f"error: git {' '.join(args)} failed:\n{proc.stderr.strip()}")
    return proc.stdout


def project_name(cfg=None):
    cfg = cfg or load_config()
    if cfg.get("project"):
        return cfg["project"]
    remote = git("remote", "get-url", "origin", check=False).strip()
    if remote:
        return remote.rstrip("/").split("/")[-1].removesuffix(".git")
    return REPO_ROOT.name


def global_dir(cfg=None):
    cfg = cfg or load_config()
    if cfg.get("global_dir"):
        return Path(cfg["global_dir"]).expanduser()
    return Path.home() / ".clutch"


def parse_frontmatter(text):
    """Split leading `---` frontmatter off a library file. Returns (meta, body).

    Not a YAML parser - just the flat `key: value` subset the libraries actually
    use, plus `[a, b]` lists (tags, modes, projects). An unterminated or absent
    block means "no metadata": the whole text comes back as body, so a file that
    merely starts with a horizontal rule is never mangled.
    """
    meta = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return meta, text
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [t.strip() for t in val[1:-1].split(",") if t.strip()]
        else:
            meta[key] = val
    if end is None:
        return {}, text
    return meta, "\n".join(lines[end + 1:]).lstrip("\n")


def strip_frontmatter(text):
    return parse_frontmatter(text)[1]


def find_resource(relpath, cfg=None):
    """Locate a library file (guide/template/prompt) local-first, then global.

    Consumer projects don't carry the libraries locally - they live in the global
    store - so every read of a shared resource goes through here.
    """
    cfg = cfg or load_config()
    for base in (AI_ROOT, global_dir(cfg)):
        p = base / relpath
        if p.exists():
            return p
    return None


def read_resource(relpath, cfg=None, required=True, strip_meta=False):
    """Read a library file. strip_meta drops the frontmatter block.

    Defaults to False on purpose: templates/solution.md *is* a frontmatter
    example, and read_template goes through here - stripping by default would
    gut it.
    """
    path = find_resource(relpath, cfg)
    if path is None:
        if required:
            sys.exit(
                f"error: resource not found: {relpath}\n"
                f"  looked in {AI_ROOT} and {global_dir(cfg)}\n"
                "  run setup.py / sync.py to populate the global store."
            )
        return None
    text = path.read_text(encoding="utf-8")
    return strip_frontmatter(text) if strip_meta else text


def read_template(name):
    text = read_resource(f"templates/{name}", required=False)
    if text is None:
        sys.exit(f"error: template missing: templates/{name} (run sync.py to restore it)")
    return text
