"""Register the `clutch init` console command. Run once from the clutch source.

It does three things:
  1. Publishes the toolkit (setup.py, sync.py, export.py, install_project.py, scripts/)
     into %USERPROFILE%\\.clutch\\toolkit\\ - the canonical copy clutch init reads.
  2. Writes launcher shims into %USERPROFILE%\\.clutch\\bin\\
     (clutch.cmd for cmd/PowerShell, clutch init for Git Bash).
  3. Adds that bin dir to your USER PATH (idempotent) so `clutch init` resolves in
     any new terminal.

Re-run after changing toolkit scripts to republish. Stdlib only; Python 3.8+.
"""
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
GLOBAL = Path.home() / ".clutch"
TOOLKIT = GLOBAL / "toolkit"
BIN = GLOBAL / "bin"
TOP = ("setup.py", "sync.py", "export.py", "install_project.py", "update_all.py",
       "clutch.py")


def publish_toolkit():
    (TOOLKIT / "scripts").mkdir(parents=True, exist_ok=True)
    for name in TOP:
        shutil.copy2(SRC / name, TOOLKIT / name)
    for f in (SRC / "scripts").glob("*.py"):
        if f.name != "__init__.py":
            shutil.copy2(f, TOOLKIT / "scripts" / f.name)
    if (SRC / ".gitignore").exists():
        shutil.copy2(SRC / ".gitignore", TOOLKIT / "gitignore")  # non-dot so it's visible
    print(f"published toolkit -> {TOOLKIT}")


def write_shims():
    """One shim per shell, both pointing at clutch.py, which dispatches subcommands."""
    BIN.mkdir(parents=True, exist_ok=True)
    # cmd/PowerShell launcher
    (BIN / "clutch.cmd").write_text(
        "@echo off\r\n"
        'python "%USERPROFILE%\\.clutch\\toolkit\\clutch.py" %*\r\n',
        encoding="utf-8",
    )
    # Git Bash / sh launcher (no extension)
    (BIN / "clutch").write_text(
        '#!/bin/sh\nexec python "$HOME/.clutch/toolkit/clutch.py" "$@"\n',
        encoding="utf-8", newline="\n",
    )
    # Retire the pre-rename commands so a stale shim can't shadow the new one.
    for old in ("installaihelper.cmd", "installaihelper",
                "aihelper-update.cmd", "aihelper-update",
                "clutch init", "clutch update"):
        stale = BIN / old
        if stale.exists():
            stale.unlink()
            print(f"  removed old shim: {old}")
    print(f"wrote shims     -> {BIN}\\clutch.cmd (+ bash shim)")


def ensure_path():
    bin_str = str(BIN)
    if sys.platform != "win32":
        print(f"note: add {bin_str} to your PATH to use `clutch init`.")
        return
    import ctypes
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                        winreg.KEY_READ | winreg.KEY_WRITE) as key:
        try:
            cur, kind = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            cur, kind = "", winreg.REG_EXPAND_SZ
        parts = [p for p in cur.split(";") if p]
        # Drop the pre-rename bin dir so a stale shim can't win the PATH lookup.
        stale = [p for p in parts if p.rstrip("\\/").lower().endswith(".ai-helper\\bin")]
        parts = [p for p in parts if p not in stale]
        for p in stale:
            print(f"  removed stale PATH entry: {p}")
        already = any(p.lower() == bin_str.lower() for p in parts)
        if already and not stale:
            print(f"PATH already contains {bin_str}")
            return
        if not already:
            parts.append(bin_str)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
    # Broadcast so new shells pick it up without a reboot.
    ctypes.windll.user32.SendMessageTimeoutW(
        0xFFFF, 0x1A, 0, "Environment", 0, 5000, ctypes.byref(ctypes.c_ulong()))
    print(f"added to USER PATH: {bin_str}")
    print("  open a NEW terminal for `clutch init` to resolve.")


def main():
    GLOBAL.mkdir(parents=True, exist_ok=True)
    publish_toolkit()
    write_shims()
    ensure_path()
    print("\nRegistered. In any project folder, run:  clutch init")


if __name__ == "__main__":
    main()
