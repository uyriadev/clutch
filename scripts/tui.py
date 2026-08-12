"""Minimal stdlib interactive multi-select (checkbox) menu - Windows + POSIX.

No dependencies. Arrow keys (or j/k) move, space toggles, a/n select all/none,
enter saves, q/esc cancels. Falls back gracefully: if there's no TTY, multiselect()
returns None so the caller can keep defaults instead of hanging.
"""
import os
import shutil
import sys
import textwrap

ESC = "\x1b"


def _enable_vt():
    """Turn on ANSI escape handling on Windows 10+ consoles."""
    if os.name != "nt":
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(mode)):
            k.SetConsoleMode(h, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


def _read_key():
    """Block for one keypress; return a normalized token."""
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            code = msvcrt.getwch()
            return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(code, "")
        if ch == "\r":
            return "enter"
        if ch == "\x03":
            return "cancel"
        if ch == ESC:
            return "cancel"
        return ch
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == ESC:
            if sys.stdin.read(1) == "[":
                return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(
                    sys.stdin.read(1), "")
            return "cancel"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == "\x03":
            return "cancel"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _draw(title, items, selected, idx):
    width = max(40, min(shutil.get_terminal_size((80, 24)).columns, 100))
    out = [f"{ESC}[2J{ESC}[H"]  # clear + home
    out.append(f"\033[1m{title}\033[0m")
    out.append("\033[2mUp/Down move  -  space toggle  -  a all  -  n none  -  "
               "enter save  -  q cancel\033[0m")
    out.append("")
    for i, (key, label, _desc) in enumerate(items):
        cursor = "\033[36m>\033[0m" if i == idx else " "
        box = "\033[32m[x]\033[0m" if key in selected else "[ ]"
        text = f"\033[1m{label}\033[0m" if i == idx else label
        out.append(f" {cursor} {box} {text}")
    out.append("")
    desc = items[idx][2] if items else ""
    for line in textwrap.wrap(desc, width - 4) or [""]:
        out.append(f"   \033[2m{line}\033[0m")
    n_sel = len([1 for k, _, _ in items if k in selected])
    out.append("")
    out.append(f"\033[2m{n_sel} of {len(items)} selected\033[0m")
    sys.stdout.write("\n".join(out) + "\n")
    sys.stdout.flush()


def multiselect(title, items, preselected=None, keys=None):
    """Show a checkbox menu. items = [(key, label, description), ...].

    Returns the set of selected keys, or None if cancelled / no TTY.
    `keys` (an iterable of tokens) drives it non-interactively for tests.
    """
    interactive = keys is None
    if interactive and not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    selected = set(preselected or [])
    idx = 0
    if interactive:
        _enable_vt()
        try:  # a live terminal handles UTF-8; guard against legacy codepages
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    kb = None if interactive else iter(keys)
    try:
        while True:
            if interactive:
                _draw(title, items, selected, idx)
                key = _read_key()
            else:
                try:
                    key = next(kb)
                except StopIteration:
                    return None
            if key in ("up", "k"):
                idx = (idx - 1) % len(items)
            elif key in ("down", "j"):
                idx = (idx + 1) % len(items)
            elif key == " ":
                selected ^= {items[idx][0]}
            elif key in ("a", "A"):
                selected = {k for k, _, _ in items}
            elif key in ("n", "N"):
                selected = set()
            elif key == "enter":
                return selected
            elif key in ("cancel", "q", "Q"):
                return None
    finally:
        if interactive:
            sys.stdout.write(f"{ESC}[2J{ESC}[H")
            sys.stdout.flush()
