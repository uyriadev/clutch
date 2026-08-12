"""Propagate the latest toolkit + rebuild every registered project's bundle.

This closes the "nothing updates automatically" gap. It reads the registry
(%USERPROFILE%\\.clutch\\projects.json) and, in one shot:

  1. From the source repo: pushes library content to the global store (sync.py) and
     republishes the toolkit scripts (install_global.py).
  2. For every consumer project: refreshes its scripts from the toolkit and rebuilds
     its AI.md bundle (via install_project.py --defaults, which keeps existing config).

Run it after ANY change to the toolkit or the libraries. See guides/MAINTAINING.md.

    python .clutch/update_all.py            # propagate to all registered projects
    python .clutch/update_all.py --dry-run  # show what would happen
    python .clutch/update_all.py --no-republish   # skip step 1, just propagate toolkit

Also available as the `clutch update` console command. Stdlib only; Python 3.8+.
"""
import json
import subprocess
import sys
from pathlib import Path

GLOBAL = Path.home() / ".clutch"
TOOLKIT = GLOBAL / "toolkit"
DRY = "--dry-run" in sys.argv


def load_registry():
    f = GLOBAL / "projects.json"
    if not f.exists():
        sys.exit(f"no registry at {f}. Run setup.py / clutch init in a project first.")
    return json.loads(f.read_text(encoding="utf-8")).get("projects", {})


def role_of(clutch: Path):
    cfg = clutch / "config.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding="utf-8")).get("role", "consumer")
        except json.JSONDecodeError:
            pass
    return "consumer"


def run(argv, cwd):
    print(f"    $ {' '.join(str(a) for a in argv)}  (in {cwd})")
    if DRY:
        return 0
    return subprocess.run([str(a) for a in argv], cwd=str(cwd)).returncode


def main():
    projects = load_registry()
    source = None
    consumers = []
    for name, entry in sorted(projects.items()):
        clutch = Path(entry.get("clutch", ""))
        repo = Path(entry.get("path", ""))
        if not clutch.exists() and not repo.exists():
            print(f"  skip {name}: path gone ({repo})")
            continue
        if role_of(clutch) == "source":
            source = (name, repo, clutch)
        else:
            consumers.append((name, repo, clutch))

    print(f"registry: source={source[0] if source else '(none)'}, "
          f"{len(consumers)} consumer(s)")

    # 1. Republish from source: libraries -> global, scripts -> toolkit.
    if "--no-republish" not in sys.argv:
        if not source:
            print("warning: no source project registered; propagating current toolkit as-is.")
        else:
            _, repo, _ = source
            print(f"\n[republish from source: {source[0]}]")
            run([sys.executable, repo / "sync.py"], repo)
            run([sys.executable, repo / "install_global.py"], repo)

    installer = TOOLKIT / "install_project.py"
    if not DRY and not installer.exists():
        sys.exit(f"toolkit installer missing at {installer}; run install_global.py first.")

    # 2. Refresh + rebuild every consumer.
    print(f"\n[propagate to {len(consumers)} consumer(s)]")
    ok = 0
    for name, repo, _ in consumers:
        if not repo.exists():
            print(f"  {name}: repo path missing ({repo}); skipped")
            continue
        print(f"\n  == {name} ==")
        rc = run([sys.executable, installer, "--defaults"], repo)
        if rc == 0:
            ok += 1
        else:
            print(f"  {name}: installer exited {rc}")

    print(f"\ndone: {ok}/{len(consumers)} consumer(s) updated"
          + (" (dry run - nothing changed)" if DRY else ""))


if __name__ == "__main__":
    main()
