"""One-shot installer: register this .clutch with the global store and seed it.

    python .clutch/setup.py            # register + seed global store + first sync
    python .clutch/setup.py --no-hook  # skip installing the git pre-push hook

What it does:
  1. Creates the global store at %USERPROFILE%\\.clutch (guides/templates/rules/
     prompts/solutions/history) if missing.
  2. Runs sync.py, which copies this project's libraries up and pulls the shared set
     down (newer-wins) - this is the "creates copies" step.
  3. Records this project in the global registry projects.json (name -> path), so the
     store knows every project that shares it.
  4. Installs the pre-push history hook if this is a git repo (unless --no-hook).

Idempotent: safe to re-run. Stdlib only; Python 3.8+.
"""
import datetime
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from _common import (  # noqa: E402
    AI_ROOT, REPO_ROOT, global_dir, load_config, project_name, read_resource,
)

SUBDIRS = ("guides", "templates", "rules", "prompts", "solutions", "history")


def run(script, *args):
    """Run a sibling script with the same interpreter; stream its output."""
    path = AI_ROOT / script
    proc = subprocess.run([sys.executable, str(path), *args], cwd=str(REPO_ROOT))
    return proc.returncode


def register(cfg, gdir, proj):
    """Add/update this project in the global registry (the 'register' step)."""
    reg_file = gdir / "projects.json"
    reg = {"projects": {}}
    if reg_file.exists():
        try:
            reg = json.loads(reg_file.read_text(encoding="utf-8"))
            reg.setdefault("projects", {})
        except json.JSONDecodeError:
            print(f"warning: {reg_file} was unreadable; recreating it", file=sys.stderr)
    entry = reg["projects"].get(proj, {})
    entry.update({
        "path": str(REPO_ROOT),
        "clutch": str(AI_ROOT),
        "last_setup": datetime.date.today().isoformat(),
    })
    entry.setdefault("registered", datetime.date.today().isoformat())
    reg["projects"][proj] = entry
    reg_file.write_text(json.dumps(reg, indent=2), encoding="utf-8")
    return reg_file, len(reg["projects"])


def main():
    cfg = load_config()
    gdir = global_dir(cfg)
    proj = project_name(cfg)
    print(f"setting up '{proj}'")
    print(f"  project : {REPO_ROOT}")
    print(f"  global  : {gdir}")

    # 1. global store skeleton
    for sub in SUBDIRS:
        (gdir / sub).mkdir(parents=True, exist_ok=True)
    print(f"global store ready ({gdir})")

    # 2. seed + share via the normal sync path
    print("\n-- sync --")
    if run("sync.py") != 0:
        sys.exit("error: sync.py failed; setup aborted")

    # 3. register the project
    reg_file, count = register(cfg, gdir, proj)
    print(f"\nregistered '{proj}' in {reg_file} ({count} project(s) known)")

    # 4. git hook
    if "--no-hook" in sys.argv:
        print("skipped hook install (--no-hook)")
    elif (REPO_ROOT / ".git").is_dir():
        print("\n-- pre-push hook --")
        run("scripts/install_hooks.py")
    else:
        print("not a git repo - skipped hook (run install_hooks.py after 'git init')")

    # 4b. scaffold info.md at the project root if it's missing (fill in with real,
    # verified content later - do not fabricate; see prompts/human-output.md).
    info = REPO_ROOT / "info.md"
    if not info.exists():
        tmpl = read_resource("templates/info.md", cfg, required=False) \
            or "# {project} - info\n\n## Rundown\n\n<fill me in>\n"
        info.write_text(tmpl.replace("{project}", proj), encoding="utf-8")
        print(f"scaffolded {info} (fill it in with real content - see human-output.md)")

    # 5. build the single-file AI bundle (+ CLAUDE.md pointer)
    print("\n-- export bundle --")
    export_args = [a for a in ("--inline", "--no-claude-md") if a in sys.argv]
    if run("export.py", *export_args) != 0:
        print("warning: export.py failed; run it manually", file=sys.stderr)

    print("\nsetup complete. The assistant should read .clutch/AI.md (one file).")
    print("Next:")
    print('  - set "stack" in config.json, then re-run: python .clutch/export.py')
    print("  - start a task:  python .clutch/scripts/checkpoint.py new \"...\"")


if __name__ == "__main__":
    main()
