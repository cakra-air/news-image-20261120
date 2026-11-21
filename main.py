"""Put the finished 20 November news poster where the grader looks.

The picture was drawn by render.py and committed as entry.png. Copying the
committed bytes makes every run identical, offline, and independent of the
fonts installed in the sandbox.
"""
import os
import struct
from pathlib import Path
from shutil import copyfile

HERE = Path(__file__).resolve().parent
POSTER = HERE / "entry.png"
TARGET = Path(os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png"))

with POSTER.open("rb") as source:
    signature = source.read(24)

if signature[:8] != b"\x89PNG\r\n\x1a\n":
    raise SystemExit("committed artwork is not a PNG")
if struct.unpack(">II", signature[16:24]) != (1024, 1024):
    raise SystemExit("committed artwork is not 1024 by 1024")
if POSTER.stat().st_size > 1024 * 1024:
    raise SystemExit("committed artwork exceeds 1 MiB")

TARGET.parent.mkdir(parents=True, exist_ok=True)
copyfile(POSTER, TARGET)
try:
    TARGET.chmod(0o644)
except OSError:
    pass
print("wrote", TARGET, TARGET.stat().st_size, "bytes")
