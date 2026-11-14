"""Generate thumbnails for the Outreach page (outreach.yml).

For every entry whose `image` points into files/images/outreach/ and does not
exist yet, render the first page of the deck to a PNG:
  - PDF  -> pdftoppm (poppler)
  - HTML -> headless Google Chrome screenshot (macOS default path, or $CHROME)
The source is `thumbfrom` if set, otherwise `path`.
GitHub "blob" URLs are turned into raw URLs; site paths (/files/...) are read locally.

Usage:
    python scripts/outreach_thumbs.py            # only missing thumbnails
    python scripts/outreach_thumbs.py --force    # regenerate all
    python scripts/outreach_thumbs.py --only errori-test
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YML = ROOT / "outreach.yml"
THUMB_DIR = "files/images/outreach/"
WIDTH = 640
CHROME = os.environ.get(
    "CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)


def raw_url(url):
    """github.com/<u>/<r>/blob/<branch>/<path> -> raw.githubusercontent.com/<u>/<r>/<branch>/<path>"""
    if url.startswith("https://github.com/") and "/blob/" in url:
        return url.replace("https://github.com/", "https://raw.githubusercontent.com/", 1).replace("/blob/", "/", 1)
    return url


def fetch(src, tmp):
    """Return a local path (PDF) or URL (HTML) for `src`."""
    if src.startswith("/"):
        return str(ROOT / src.lstrip("/"))
    if src.lower().endswith(".pdf"):
        dest = Path(tmp) / "deck.pdf"
        req = urllib.request.Request(raw_url(src), headers={"User-Agent": "outreach-thumbs"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        return str(dest)
    return src


def pdf_thumb(pdf, out):
    stem = str(out.with_suffix(""))
    subprocess.run(
        ["pdftoppm", "-png", "-f", "1", "-l", "1", "-singlefile",
         "-scale-to-x", str(WIDTH), "-scale-to-y", "-1", pdf, stem],
        check=True,
    )


def html_thumb(src, out):
    url = src if "://" in src else Path(src).resolve().as_uri()
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={profile}", "--window-size=1280,720",
             "--virtual-time-budget=4000", f"--screenshot={out}", url],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    subprocess.run(["sips", "--resampleWidth", str(WIDTH), str(out)],
                   check=True, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()

    items = yaml.safe_load(YML.read_text(encoding="utf-8"))
    (ROOT / THUMB_DIR).mkdir(parents=True, exist_ok=True)
    failed = 0
    for it in items:
        img = str(it.get("image", "")).lstrip("/")
        if not img.startswith(THUMB_DIR):
            continue  # custom image, nothing to generate
        if args.only and it.get("id") != args.only:
            continue
        out = ROOT / img
        if out.exists() and not args.force:
            continue
        src = it.get("thumbfrom") or it.get("path")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                local = fetch(src, tmp)
                if local.lower().endswith(".pdf"):
                    pdf_thumb(local, out)
                else:
                    html_thumb(local, out)
            print(f"ok    {it['id']}")
        except Exception as e:  # keep going, report at the end
            failed += 1
            print(f"FAIL  {it.get('id')}: {e}", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
