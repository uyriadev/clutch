"""Append a session-history entry for everything since the last recorded push.

Runs automatically from the pre-push git hook (see install_hooks.py); can also be
run by hand. Tracks the last recorded commit in .clutch/state.json and logs
state..HEAD into .clutch/history/YYYY-MM-DD.md per guides/HISTORY.md.
"""
import datetime
import json

from _common import AI_ROOT, git, read_template

STATE = AI_ROOT / "state.json"


def main():
    head = git("rev-parse", "HEAD").strip()
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()

    last = None
    if STATE.exists():
        try:
            last = json.loads(STATE.read_text(encoding="utf-8")).get("last_recorded")
        except json.JSONDecodeError:
            last = None
    # Fall back to upstream, then to the last 10 commits, on first run.
    # --verify --quiet prints nothing on failure (plain rev-parse echoes the arg).
    if last is None:
        last = git("rev-parse", "--verify", "--quiet", "@{u}", check=False).strip() or None
    if last is None:
        last = git("rev-parse", "--verify", "--quiet", "HEAD~10", check=False).strip() or None

    rng = f"{last}..{head}" if last and last != head else None
    if rng is None and last == head:
        print("history: nothing new since last recorded push")
        return

    if rng:
        commits = git("log", "--format=- %h %s", rng).strip()
        diffstat = git("diff", "--stat", rng).strip()
    else:  # brand-new repo with < 10 commits and no upstream: log everything
        commits = git("log", "--format=- %h %s").strip()
        diffstat = git("show", "--stat", "--format=", head).strip()
        rng = f"(root)..{head[:7]}"

    if not commits:
        print("history: nothing new since last recorded push")
        return

    entry = read_template("history-entry.md").format(
        time=datetime.datetime.now().strftime("%H:%M"),
        branch=branch,
        range=f"{last[:7]}..{head[:7]}" if last and last in rng else rng,
        commits=commits,
        diffstat=diffstat,
    )

    hist_dir = AI_ROOT / "history"
    hist_dir.mkdir(exist_ok=True)
    day_file = hist_dir / f"{datetime.date.today().isoformat()}.md"
    if not day_file.exists():
        day_file.write_text(
            f"# Session history - {datetime.date.today().isoformat()}\n\n",
            encoding="utf-8",
        )
    with day_file.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")

    STATE.write_text(
        json.dumps({"last_recorded": head}, indent=2), encoding="utf-8"
    )
    print(f"history: logged {rng} -> {day_file}")
    print("history: fill in the Session notes placeholder (see guides/HISTORY.md)")


if __name__ == "__main__":
    main()
