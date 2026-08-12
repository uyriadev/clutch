"""clutch - one command, a few subcommands. The entry point the shim calls.

    clutch init      install/refresh .clutch in the current project
    clutch update    propagate the latest toolkit + libraries to every project
    clutch doctor    check whether this project is behind the global store
    clutch search    find a prompt by keyword
    clutch modes     list the work phases and their read lines

Everything here is a thin dispatch to the script that already does the work, so
there is exactly one implementation of each job. Stdlib only; Python 3.8+.
"""
import subprocess
import sys
from pathlib import Path

TOOLKIT = Path(__file__).resolve().parent
LOCAL = Path.cwd() / ".clutch"

USAGE = """clutch - AI context toolkit

  clutch init [--defaults]   install or refresh .clutch/ in this project
  clutch update              rebuild every registered project (propagate)
  clutch doctor              is this project behind the global store?
  clutch search <keyword>    find a prompt by tag, title, or path
  clutch modes               list work phases and their read lines
  clutch tags                every tag and the file carrying it

Run `clutch <command> --help` where the underlying script supports it."""


def run(script, *args, cwd=None):
    """Run a toolkit or project script, passing through its exit code."""
    if not Path(script).exists():
        sys.exit(f"error: {script} not found. Re-run `clutch init` in this project.")
    return subprocess.run([sys.executable, str(script), *args],
                          cwd=str(cwd) if cwd else None).returncode


def project_script(name):
    """Prefer the project's own copy; fall back to the toolkit's."""
    local = LOCAL / name
    return local if local.exists() else TOOLKIT / name


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    cmd, rest = argv[0], argv[1:]

    if cmd == "init":
        return run(TOOLKIT / "install_project.py", *rest)
    if cmd == "update":
        return run(TOOLKIT / "update_all.py", *rest)
    if cmd == "doctor":
        return run(project_script("scripts/doctor.py"), *rest, cwd=Path.cwd())
    if cmd in ("search", "modes", "tags", "mode"):
        return run(project_script("scripts/library.py"), cmd, *rest, cwd=Path.cwd())

    print(f"unknown command: {cmd}\n", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
