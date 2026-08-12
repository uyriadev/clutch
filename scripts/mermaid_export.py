"""Render Mermaid diagrams to high-resolution images (SVG + PNG).

Wraps @mermaid-js/mermaid-cli (`mmdc`). If `mmdc` isn't on PATH it falls back to
`npx -y @mermaid-js/mermaid-cli`, so a Node install is enough - no global install
required (the first npx run downloads it).

    python .clutch/scripts/mermaid_export.py diagram.mmd
    python .clutch/scripts/mermaid_export.py diagram.mmd --scale 4 --background white
    python .clutch/scripts/mermaid_export.py notes.md            # every ```mermaid block
    python .clutch/scripts/mermaid_export.py diagram.mmd --format png --out-dir images/

Defaults: SVG (vector, resolution-independent) + PNG at scale 3, transparent
background, default theme. Higher --scale = higher-res PNG (deviceScaleFactor).

Stdlib only; Python 3.8+. Requires Node.js for the actual rendering.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)


BROWSER_MISSING = re.compile(r"Could not find (chrome|chromium)", re.IGNORECASE)

# Common system Chromium locations. Puppeteer's own bundled headless shell fails to
# launch on some Windows setups (0xC000007B), so prefer a real installed browser.
_BROWSER_CANDIDATES = {
    "win32": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ],
    "linux": [
        "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
    ],
}


def system_browser():
    """Path to an installed Chrome/Edge/Chromium, or None. Honors an env override."""
    import os
    env = os.environ.get("PUPPETEER_EXECUTABLE_PATH") or os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for cand in _BROWSER_CANDIDATES.get(sys.platform, []):
        if Path(cand).exists():
            return cand
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def renderer():
    """Return the argv prefix that runs mmdc, or None if Node isn't available."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        return [mmdc]
    npx = shutil.which("npx")
    if npx:
        return [npx, "-y", "@mermaid-js/mermaid-cli"]
    return None


def install_browser():
    """Download the headless Chromium that Puppeteer (mermaid-cli) needs.

    mermaid-cli ships puppeteer-core but not a browser; the first render on a fresh
    machine fails with 'Could not find chrome...'. This fetches it once (~150 MB).
    """
    npx = shutil.which("npx")
    if not npx:
        return False
    print("  headless browser missing - installing chrome-headless-shell "
          "(one-time, ~150 MB)...")
    proc = subprocess.run(
        [npx, "-y", "puppeteer", "browsers", "install", "chrome-headless-shell"],
        text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode == 0


def extract_sources(inp: Path, tmp: Path):
    """Yield (source_path, stem) for each diagram to render.

    A .mmd/.mermaid file is used directly. A markdown file has each ```mermaid block
    pulled into its own temp .mmd, suffixed -1, -2, ... when there is more than one.
    """
    if inp.suffix.lower() in (".mmd", ".mermaid"):
        yield inp, inp.stem
        return
    text = inp.read_text(encoding="utf-8")
    blocks = MERMAID_BLOCK.findall(text)
    if not blocks:
        sys.exit(f"error: no ```mermaid blocks found in {inp}")
    for i, body in enumerate(blocks, 1):
        stem = inp.stem if len(blocks) == 1 else f"{inp.stem}-{i}"
        f = tmp / f"{stem}.mmd"
        f.write_text(body.strip() + "\n", encoding="utf-8")
        yield f, stem


def main():
    ap = argparse.ArgumentParser(description="Render Mermaid to high-res SVG/PNG.")
    ap.add_argument("input", help="a .mmd/.mermaid file, or a .md file with mermaid blocks")
    ap.add_argument("-o", "--output", help="explicit output path (single-diagram input only)")
    ap.add_argument("--out-dir", help="directory for outputs (default: next to input)")
    ap.add_argument("--format", default="svg,png",
                    help="comma list of svg,png,pdf (default: svg,png)")
    ap.add_argument("--scale", type=float, default=3.0,
                    help="deviceScaleFactor for raster output; higher = higher-res (default: 3)")
    ap.add_argument("--width", type=int, help="canvas width in px (optional)")
    ap.add_argument("--height", type=int, help="canvas height in px (optional)")
    ap.add_argument("--theme", default="default",
                    choices=["default", "neutral", "dark", "forest", "base"])
    ap.add_argument("--background", default="transparent",
                    help="'transparent', 'white', or a hex color (default: transparent)")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        sys.exit(f"error: input not found: {inp}")

    run = renderer()
    if run is None:
        sys.exit(
            "error: no Mermaid renderer available.\n"
            "  Install Node.js, then either let this tool use npx (no action needed),\n"
            "  or install the CLI globally:  npm install -g @mermaid-js/mermaid-cli"
        )

    formats = [f.strip().lower() for f in args.format.split(",") if f.strip()]
    out_dir = Path(args.out_dir) if args.out_dir else inp.resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Puppeteer needs --no-sandbox in many environments (CI, containers, some Windows).
    # Prefer a system Chrome/Edge over the bundled headless shell (more reliable).
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        pconf = tmp / "puppeteer.json"
        pconf_data = {"args": ["--no-sandbox"]}
        browser = system_browser()
        if browser:
            pconf_data["executablePath"] = browser
            print(f"  using browser: {browser}")
        pconf.write_text(json.dumps(pconf_data), encoding="utf-8")

        def render(src, out):
            cmd = [
                *run, "-i", str(src), "-o", str(out),
                "-t", args.theme, "-b", args.background, "-s", str(args.scale),
                "-p", str(pconf),
            ]
            if args.width:
                cmd += ["-w", str(args.width)]
            if args.height:
                cmd += ["-H", str(args.height)]
            return subprocess.run(cmd, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace")

        made, failed = [], 0
        healed = False
        sources = list(extract_sources(inp, tmp))
        for src, stem in sources:
            for fmt in formats:
                if args.output and len(sources) == 1 and len(formats) == 1:
                    out = Path(args.output)
                    out.parent.mkdir(parents=True, exist_ok=True)
                else:
                    out = out_dir / f"{stem}.{fmt}"
                proc = render(src, out)
                # Auto-heal a missing Puppeteer browser once, then retry.
                if proc.returncode != 0 and not healed and \
                        BROWSER_MISSING.search((proc.stderr or "") + (proc.stdout or "")):
                    healed = True
                    if install_browser():
                        proc = render(src, out)
                if proc.returncode == 0 and out.exists():
                    kb = out.stat().st_size / 1024
                    print(f"  wrote {out}  ({kb:.0f} KB)")
                    made.append(out)
                else:
                    failed += 1
                    raw = (proc.stderr or proc.stdout or "unknown error").strip()
                    # Show the meaningful line(s), not just the last stack frame.
                    lines = [ln for ln in raw.splitlines()
                             if ln.strip() and not ln.strip().startswith("at ")]
                    msg = "\n    ".join(lines[-4:]) if lines else raw
                    print(f"  FAILED {out}\n    {msg}", file=sys.stderr)

    if not made:
        sys.exit("error: nothing rendered - check the diagram syntax and Node install.")
    print(f"done: {len(made)} file(s)" + (f", {failed} failed" if failed else ""))


if __name__ == "__main__":
    main()
