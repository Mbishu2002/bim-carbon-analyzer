"""Font Awesome icons via qtawesome (cached for combo arrows and toolbar)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QStyleFactory

from src.core.paths import app_data_dir
from src.ui import theme

try:
    import qtawesome as qta
    _HAS_QTA = True
except ImportError:
    qta = None
    _HAS_QTA = False

# Excel-style dropdown caret (Font Awesome 5 solid)
FA_CARET_DOWN = "fa5s.caret-down"

_caret_png: Path | None = None


def dropdown_caret(color: str | None = None) -> QIcon:
    """Font Awesome caret-down icon for combo arrow buttons."""
    if not _HAS_QTA:
        return QIcon()
    return qta.icon(FA_CARET_DOWN, color=color or theme.ACCENT_DARK)


def _caret_png_path() -> str:
    """Cache a small PNG for QSS ``image: url(...)`` on standard combos."""
    global _caret_png
    if _caret_png is None:
        cache = app_data_dir() / ".ui_cache"
        cache.mkdir(parents=True, exist_ok=True)
        _caret_png = cache / "caret_down.png"
        if _HAS_QTA:
            from PySide6.QtCore import QSize

            dropdown_caret().pixmap(QSize(16, 16)).save(str(_caret_png), "PNG")
        else:
            _caret_png.touch()
    return _caret_png.resolve().as_posix()


def apply_fa_dropdown_arrow(combo: QComboBox) -> None:
    """Show a visible FA caret on toolbar/filter combos (Fusion + QSS image)."""
    combo.setStyle(QStyleFactory.create("Fusion"))
    url = _caret_png_path()
    combo.setStyleSheet(
        (combo.styleSheet() or "")
        + f"""
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 24px;
            border: none;
            border-left: 1px solid {theme.BORDER};
            background: {theme.BG_PANEL};
        }}
        QComboBox::down-arrow {{
            image: url({url});
            width: 12px;
            height: 12px;
        }}
        """
    )
