"""Working-memory checkpoint for the current task (see guides/CONTEXT.md).

    python .clutch/scripts/checkpoint.py new "refactor the auth layer"
    python .clutch/scripts/checkpoint.py show      # print current.md
    python .clutch/scripts/checkpoint.py path      # print its path (for editing)
    python .clutch/scripts/checkpoint.py archive   # file it away, clear current

Keeps one live file, checkpoint/current.md, so context can be reset/compacted
without losing the load-bearing state of the task.
"""
import datetime
import sys

from _common import AI_ROOT, read_template

CP_DIR = AI_ROOT / "checkpoint"
CURRENT = CP_DIR / "current.md"
ARCHIVE = CP_DIR / "archive"


def _slug(text, n=48):
    keep = "".join(c if c.isalnum() or c in " -_" else "" for c in text.lower())
    return "-".join(keep.split())[:n] or "task"


def cmd_new(task):
    if not task:
        sys.exit('usage: checkpoint.py new "task description"')
    if CURRENT.exists():
        sys.exit(
            f"error: {CURRENT} already exists. Archive it first "
            "(checkpoint.py archive) or edit it directly."
        )
    CP_DIR.mkdir(exist_ok=True)
    body = read_template("checkpoint.md").format(
        task=task, date=datetime.date.today().isoformat()
    )
    CURRENT.write_text(body, encoding="utf-8")
    print(f"created: {CURRENT}")
    print("fill in Goal/Constraints as you work; see guides/CONTEXT.md")


def cmd_show():
    if not CURRENT.exists():
        sys.exit("no active checkpoint (run: checkpoint.py new \"...\")")
    print(CURRENT.read_text(encoding="utf-8"))


def cmd_path():
    print(CURRENT)


def cmd_archive():
    if not CURRENT.exists():
        sys.exit("no active checkpoint to archive")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    first = CURRENT.read_text(encoding="utf-8").splitlines()[0]
    task = first.replace("# Checkpoint", "").strip(" --") or "task"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    dest = ARCHIVE / f"{stamp}-{_slug(task)}.md"
    CURRENT.rename(dest)
    print(f"archived: {dest}")
    print("current checkpoint cleared - safe to reset context")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    arg = " ".join(sys.argv[2:]).strip()
    {
        "new": lambda: cmd_new(arg),
        "show": cmd_show,
        "path": cmd_path,
        "archive": cmd_archive,
    }.get(cmd, lambda: sys.exit(f"unknown command: {cmd}\n{__doc__}"))()


if __name__ == "__main__":
    main()
