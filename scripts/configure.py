"""Choose which bundle components go into AI.md - interactive menu + config writer.

The registry below is the single source of truth for what the bundle can contain;
export.py reads it too, so the menu and the build never drift. Run it standalone to
reconfigure an existing project:

    python .clutch/scripts/configure.py     # pick components, then rebuild AI.md

install_project.py calls run() during install so the installer asks up front.
Selections persist in config.json as `bundle_include` (+ the `operating_mode` flag).
"""
import json
import subprocess
import sys
from pathlib import Path

from _common import AI_ROOT, load_config

# key, category, path (relative to a library root), label, description, default-on.
# `operating-mode` is special: it maps to the config `operating_mode` flag.
COMPONENTS = [
    ("operating-mode", "Persona", "prompts/operating-mode.md",
     "Operating mode - clutch engaged",
     "The persona: voice (address you as 'Chief', punchy, no filler) plus the reliability "
     "marker and pre-flight discipline. Off = a plain, neutral assistant with no marker."),
    ("AI-PITFALLS", "Guide", "guides/AI-PITFALLS.md",
     "AI failure-mode checklist",
     "The pre-flight for anchoring, sycophancy, confabulation, premature closure, and when "
     "to spawn a clean-context subagent. Highest-leverage guide - keep it on."),
    ("CONTEXT", "Guide", "guides/CONTEXT.md",
     "Context & working memory",
     "How to reset or compact context without losing accuracy, using the checkpoint "
     "working-memory file. On for long, multi-step work."),
    ("MEMORY", "Guide", "guides/MEMORY.md",
     "Memory API",
     "How to save and read the three memory stores - solutions (cross-project), history "
     "(per-session), and the checkpoint (current task)."),
    ("SOLUTIONS", "Guide", "guides/SOLUTIONS.md",
     "Solutions library (cross-project fixes)",
     "What qualifies as a reusable solution, how to write one, and the standing rule to "
     "grep solutions/ before any environmental debugging. Recommended on."),
    ("HISTORY", "Guide", "guides/HISTORY.md",
     "Session history (episodic memory)",
     "How per-session notes get written to history/ on push, and what belongs in one. "
     "Include if you want the AI maintaining session notes."),
    ("COMMIT", "Guide", "guides/COMMIT.md",
     "Commit-in-transcript-order workflow",
     "How to use transcript_commit.py: group the session's changes by the request that "
     "produced them and commit in the order the work was done. Include if you commit "
     "from sessions."),
    ("MAINTAINING", "Guide", "guides/MAINTAINING.md",
     "Propagation rule (clutch update)",
     "The standing rule that a toolkit or library change is not finished until "
     "clutch update rebuilds every project. Mainly for the source repo, cheap "
     "everywhere else."),
    ("code-craft", "Prompt", "prompts/code-craft.md",
     "Code craft",
     "Make generated code read as human-written: name libraries/errors/versions exactly, "
     "complete code with no stubs, right-sized abstraction."),
    ("communication", "Prompt", "prompts/communication.md",
     "Communication discipline",
     "Findings-first, filler-free responses; length calibrated to the task; result verbs "
     "over hedges."),
    ("command-vocabulary", "Prompt", "prompts/command-vocabulary.md",
     "Command vocabulary",
     "A shared glossary so terse commands (fix / continue / optimize / review) mean one "
     "consistent thing. Useful for fast iterative work."),
    ("continuity", "Prompt", "prompts/continuity.md",
     "Session continuity",
     "Treat a session as one project: reference prior artifacts by name, keep naming "
     "stable, build additively."),
    ("human-output", "Prompt", "prompts/human-output.md",
     "Human output (no AI tells)",
     "No co-author trailers, standard-keyboard characters only (no em dashes), casual "
     "explanatory comments, defer creative calls to the user, verify sources, keep "
     "info.md current. Recommended on."),
    ("flowcharts", "Prompt", "prompts/flowcharts.md",
     "Flowcharts (Mermaid state diagrams)",
     "Author flowcharts as Mermaid stateDiagram-v2 and export high-res images with "
     "mermaid_export.py. Include if you make diagrams."),
    ("design-playbooks", "Prompt", "prompts/design/README.md",
     "Design playbooks (trigger table)",
     "Decision playbooks for structural choices (data structures, function design). "
     "Only the trigger table rides in the bundle; the full playbook is read from "
     "prompts/design/ when a trigger fires. Recommended on."),
    ("modes", "Router", "prompts/modes/",
     "Mode router (plan / code / debug / review / wrap)",
     "A small routing table naming each work phase, when to enter it, and the exact "
     "read line that loads it. The phase playbooks themselves stay on disk until "
     "needed. Generated from library frontmatter. Recommended on."),
]


def default_selection():
    # everything on by default
    return {key for key, *_ in COMPONENTS}


def current_selection(cfg=None):
    cfg = cfg or load_config()
    inc = cfg.get("bundle_include")
    sel = set(inc) if inc is not None else {k for k, cat, *_ in COMPONENTS if cat != "Persona"}
    if inc is None:  # first run: default everything on
        sel = default_selection()
    if cfg.get("operating_mode", True):
        sel.add("operating-mode")
    else:
        sel.discard("operating-mode")
    return sel


def included(cfg, key):
    """Does this component go into the bundle, per config?"""
    if key == "operating-mode":
        return cfg.get("operating_mode", True)
    inc = cfg.get("bundle_include")
    return inc is None or key in inc


def apply_selection(sel):
    cfg_file = AI_ROOT / "config.json"
    cfg = {}
    if cfg_file.exists():
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    cfg["operating_mode"] = "operating-mode" in sel
    cfg["bundle_include"] = [k for k, *_ in COMPONENTS
                             if k != "operating-mode" and k in sel]
    cfg_file.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return cfg


def run(interactive=True):
    """Show the picker (if a TTY) and persist the selection. Returns True if it ran."""
    items = [(key, f"[{cat}] {label}", desc) for key, cat, path, label, desc in COMPONENTS]
    sel = None
    if interactive:
        try:
            from tui import multiselect
            sel = multiselect(
                "AI.md - choose what to include  (space = on/off)",
                items, preselected=current_selection())
        except Exception as e:  # never let the menu block an install
            print(f"  (menu unavailable: {e}; keeping current selection)", file=sys.stderr)
            return False
    if sel is None:
        print("  configure: kept current selection")
        return False
    apply_selection(sel)
    on = ", ".join(sorted(sel)) or "(none)"
    print(f"  configure: included -> {on}")
    return True


if __name__ == "__main__":
    changed = run(interactive="--defaults" not in sys.argv)
    # standalone: rebuild the bundle so the choice takes effect immediately
    export = AI_ROOT / "export.py"
    if export.exists():
        subprocess.run([sys.executable, str(export)], cwd=str(AI_ROOT.parent))
