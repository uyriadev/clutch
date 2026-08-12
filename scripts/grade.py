"""Generate a grading prompt from commits.

Usage:
    python .clutch/scripts/grade.py              # grade HEAD (last commit)
    python .clutch/scripts/grade.py HEAD~3..HEAD # grade a range
    python .clutch/scripts/grade.py abc1234     # grade a specific commit

Writes the prompt to .clutch/grading/<date>-<sha>.md and prints its path.
Paste the file's contents into your AI of choice; the rubric from
guides/GRADING.md is embedded.
"""
import datetime
import sys

from _common import AI_ROOT, git, load_config, project_name, read_resource, read_template


def main():
    refspec = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    cfg = load_config()

    if ".." in refspec:
        rng = refspec
    else:
        # single commit -> diff against its parent
        rng = f"{refspec}~1..{refspec}"

    commits = git("log", "--format=- %h %s (%an, %ad)", "--date=short", rng).strip()
    if not commits:
        sys.exit(f"error: no commits in range {rng}")
    diffstat = git("diff", "--stat", rng).strip()
    diff = git("diff", rng)

    max_chars = int(cfg.get("max_diff_chars", 60000))
    truncation_note = ""
    if len(diff) > max_chars:
        diff = diff[:max_chars]
        truncation_note = (
            f"\n> NOTE: diff truncated at {max_chars} characters. "
            "Grade what is shown and say the review is partial."
        )

    prompt = read_template("grading-prompt.md").format(
        project=project_name(cfg),
        refspec=refspec,
        rubric=read_resource("guides/GRADING.md", cfg),
        commits=commits,
        diffstat=diffstat,
        diff=diff,
        truncation_note=truncation_note,
    )

    short_sha = git("rev-parse", "--short", rng.split("..")[-1]).strip()
    out_dir = AI_ROOT / "grading"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{datetime.date.today().isoformat()}-{short_sha}.md"
    out.write_text(prompt, encoding="utf-8")
    print(f"grading prompt written: {out}")


if __name__ == "__main__":
    main()
