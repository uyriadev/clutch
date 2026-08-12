"""Install a consumer .clutch into the CURRENT directory.

This is what the `clutch init` console command runs. It copies the toolkit
scripts from the global store into ./.clutch/, writes a consumer config.json if
one doesn't exist, then runs setup.py (seed global store, install the pre-push hook,
build the AI.md bundle).

Re-running it in an existing project refreshes the toolkit scripts to the latest
published version without touching config, solutions, history, or the checkpoint.

Register the command once with `install_global.py` from the clutch source repo.
Stdlib only; Python 3.8+.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

TOOLKIT = Path.home() / ".clutch" / "toolkit"
TOP_SCRIPTS = ("setup.py", "sync.py", "export.py")


def main():
    if not TOOLKIT.is_dir():
        sys.exit(
            f"error: toolkit not found at {TOOLKIT}\n"
            "  Register it once: run `python install_global.py` in the clutch source repo."
        )

    cwd = Path.cwd()
    dest = cwd / ".clutch"
    if dest.resolve() == TOOLKIT.parent.resolve():
        sys.exit("error: refusing to install into the global store itself.")
    (dest / "scripts").mkdir(parents=True, exist_ok=True)

    # Copy the toolkit (always refresh scripts; never touch data).
    for name in TOP_SCRIPTS:
        shutil.copy2(TOOLKIT / name, dest / name)
    shutil.copy2(TOOLKIT / "install_project.py", dest / "install_project.py")
    for f in (TOOLKIT / "scripts").glob("*.py"):
        shutil.copy2(f, dest / "scripts" / f.name)
    gi = TOOLKIT / "gitignore"
    if gi.exists() and not (dest / ".gitignore").exists():
        shutil.copy2(gi, dest / ".gitignore")

    # Write a consumer config only if there isn't one already.
    cfg = dest / "config.json"
    created_cfg = not cfg.exists()
    if created_cfg:
        cfg.write_text(json.dumps({
            "project": cwd.name,
            "role": "consumer",
            "global_dir": None,
            "max_diff_chars": 60000,
            "operating_mode": True,
            "stack": [],
        }, indent=2) + "\n", encoding="utf-8")

    print(f"clutch init: toolkit copied into {dest}")

    # Ask which components to bundle (interactive menu; skipped if no TTY or --defaults).
    if "--defaults" not in sys.argv and "--yes" not in sys.argv:
        print("-- choose bundle components --")
        sys.path.insert(0, str(dest / "scripts"))
        try:
            import configure
            configure.run(interactive=True)
        except Exception as e:
            print(f"  (skipped menu: {e})")

    print("-- running setup --")
    rc = subprocess.run([sys.executable, str(dest / "setup.py"), *sys.argv[1:]],
                        cwd=str(cwd)).returncode
    if rc != 0:
        sys.exit(f"setup.py exited {rc}")

    print("\nclutch init: done - read .clutch/AI.md.")
    if created_cfg:
        print('Set your stack: edit .clutch/config.json "stack" '
              '(e.g. ["python","fastapi"]), then: python .clutch/export.py')


if __name__ == "__main__":
    main()
