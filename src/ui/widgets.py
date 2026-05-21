"""Reusable UI widgets shared across pages."""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from src.ui import icons, theme


class _ComboWithCaret(QWidget):
    """Base: QComboBox + Font Awesome caret button (works reliably on Windows)."""

    currentTextChanged = Signal(str)

    def __init__(
        self,
        object_name: str,
        inner_name: str,
        arrow_name: str,
        items: list[str] | None = None,
        current: str | None = None,
        min_width: int = 0,
        max_visible: int = 16,
        min_contents: int = 12,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName(object_name)
        if min_width:
            self.setMinimumWidth(min_width)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._combo = QComboBox()
        self._combo.setObjectName(inner_name)
        self._combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._combo.setCursor(Qt.PointingHandCursor)
        self._combo.setMaxVisibleItems(max_visible)
        if min_contents:
            self._combo.setMinimumContentsLength(min_contents)
        if items:
            self._combo.addItems(items)
        if current:
            idx = self._combo.findText(current)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.currentTextChanged.connect(self.currentTextChanged.emit)

        self._arrow = QToolButton()
        self._arrow.setObjectName(arrow_name)
        self._arrow.setIcon(icons.dropdown_caret())
        self._arrow.setIconSize(QSize(11, 11))
        self._arrow.setFixedWidth(28)
        self._arrow.setCursor(Qt.PointingHandCursor)
        self._arrow.clicked.connect(self._combo.showPopup)

        lay.addWidget(self._combo, 1)
        lay.addWidget(self._arrow, 0)

    def addItems(self, items):
        self._combo.addItems(items)

    def addItem(self, text: str):
        self._combo.addItem(text)

    def clear(self):
        self._combo.clear()

    def currentText(self) -> str:
        return self._combo.currentText()

    def setCurrentText(self, text: str):
        self._combo.setCurrentText(text)

    def setCurrentIndex(self, index: int):
        self._combo.setCurrentIndex(index)

    def blockSignals(self, block: bool) -> bool:
        self._combo.blockSignals(block)
        return super().blockSignals(block)

    def setToolTip(self, tip: str):
        super().setToolTip(tip)
        self._combo.setToolTip(tip)


class DropdownComboBox(_ComboWithCaret):
    """Toolbar / chart-header dropdown with border and FA caret."""

    def __init__(self, items: list[str] | None = None, current: str | None = None,
                 min_width: int = 160, parent=None):
        super().__init__(
            "DropdownCombo",
            "DropdownComboInner",
            "DropdownComboArrow",
            items=items,
            current=current,
            min_width=min_width,
            parent=parent,
        )


class TableCellComboBox(_ComboWithCaret):
    """Excel-style in-cell dropdown with a visible Font Awesome caret button."""

    def __init__(self, items: list[str] | None = None, current: str | None = None, parent=None):
        super().__init__(
            "TableCellCombo",
            "TableCellComboInner",
            "TableCellComboArrow",
            items=items,
            current=current,
            max_visible=18,
            min_contents=24,
            parent=parent,
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        self._arrow.setFixedWidth(26)
        self._arrow.setToolTip("Choose value")
