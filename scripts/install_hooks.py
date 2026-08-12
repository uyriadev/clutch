"""Install the pre-push git hook that runs history.py on every push.

Git has no client-side post-push hook, so pre-push is the standard place: it fires
once per push, after you ran `git push`, just before objects are sent. The hook
never blocks the push - history.py failures are warnings only.
"""
import stat
import sys

from _common import REPO_ROOT

HOOK = """#!/bin/sh
# installed by .clutch/scripts/install_hooks.py
python "$(git rev-parse --show-toplevel)/.clutch/scripts/history.py" || \
  echo "warning: .clutch history logging failed (push continues)" >&2
exit 0
"""


def main():
    hooks_dir = REPO_ROOT / ".git" / "hooks"
    if not hooks_dir.is_dir():
        sys.exit(f"error: {hooks_dir} not found - is this a git repository?")
    hook_path = hooks_dir / "pre-push"
    if hook_path.exists() and ".clutch" not in hook_path.read_text(encoding="utf-8"):
        sys.exit(
            f"error: {hook_path} already exists and is not ours.\n"
            "Add this line to it manually:\n"
            '  python "$(git rev-parse --show-toplevel)/.clutch/scripts/history.py"'
        )
    hook_path.write_text(HOOK, encoding="utf-8", newline="\n")
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"installed: {hook_path}")


if __name__ == "__main__":
    main()
