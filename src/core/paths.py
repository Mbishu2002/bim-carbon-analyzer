"""Path helpers that work whether the app runs from source or as a frozen
PyInstaller bundle."""

import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def _project_root() -> Path:
    # When running from source: src/core/paths.py -> parents[2] is the project root.
    return Path(__file__).resolve().parents[2]


def resource_path(rel: str) -> Path:
    """Read-only resources bundled with the app (LCA db, sample IFCs)."""
    if is_frozen():
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base / rel
    return _project_root() / rel


def app_data_dir() -> Path:
    """Writable location for user output. Lives next to the .exe in frozen
    builds, otherwise inside the project tree."""
    if is_frozen():
        return Path(sys.executable).parent
    return _project_root()
