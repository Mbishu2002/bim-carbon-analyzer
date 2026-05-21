"""Build a Windows executable with PyInstaller.

Usage (from this folder, with the venv active):
    python build.py              # default: single-file exe (slower startup)
    python build.py --onedir     # folder bundle (instant startup)

Output:
    dist/BIM_Carbon_Analyzer.exe                       (--onefile, default)
    dist/BIM_Carbon_Analyzer/BIM_Carbon_Analyzer.exe   (--onedir)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "BIM_Carbon_Analyzer"

ONEFILE = "--onedir" not in sys.argv

# Clean previous build artefacts so we get a deterministic output.
for d in ("build", "dist"):
    p = ROOT / d
    if p.exists():
        shutil.rmtree(p)
spec = ROOT / f"{APP_NAME}.spec"
if spec.exists():
    spec.unlink()

# Windows uses ';' as the --add-data separator.
sep = ";" if os.name == "nt" else ":"

args = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",            # no console window
    "--onefile" if ONEFILE else "--onedir",
    f"--name={APP_NAME}",
    f"--paths={ROOT}",
    # Bundled resources
    f"--add-data=data/lca_database.csv{sep}data",
    f"--add-data=data/samples{sep}data/samples",
    # Native binaries inside ifcopenshell + matplotlib data + PySide6 plugins
    "--collect-all=ifcopenshell",
    "--collect-data=matplotlib",
    # qtawesome ships icon fonts (.ttf) that must be packaged or icons render blank
    "--collect-all=qtawesome",
    "--hidden-import=openpyxl",
    "--hidden-import=PySide6.QtSvg",
    str(ROOT / "app.py"),
]

print(">>", " ".join(args))
res = subprocess.run(args, cwd=ROOT)
sys.exit(res.returncode)
