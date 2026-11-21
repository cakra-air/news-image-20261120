"""Place the finished 19 November world-news poster at the grader's output path.

The artwork is rendered by render.py and stored in entry.png. Copying those
bytes keeps every graded run identical, offline and free of font dependencies.
"""
import os
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parent
ART = ROOT / "entry.png"
DEST = Path(os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png"))

with ART.open("rb") as stream:
    if stream.read(8) != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("the committed poster is not a PNG")

if ART.stat().st_size > 1024 * 1024:
    raise SystemExit("the poster is larger than the 1 MiB limit")

DEST.parent.mkdir(parents=True, exist_ok=True)
copyfile(ART, DEST)
print("wrote", DEST, DEST.stat().st_size, "bytes")
