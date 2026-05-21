"""Green & white light theme: palette, Qt stylesheet, table-cell combos,
and matplotlib rcParams. Keep colour values in one place so charts and
widgets stay in sync.
"""

# -------------------------------------------------
# COLOR PALETTE (light mode, green accent)
# -------------------------------------------------
BG = "#ffffff"
BG_PANEL = "#f6faf7"
BG_ELEV = "#ffffff"
BG_ACTIVE = "#e8f3ea"
BG_HOVER = "#f0f7f2"
ACTIVITYBAR = "#ffffff"
BORDER = "#d4e8d8"
BORDER_STRONG = "#a5d6a7"

TEXT = "#1a2e1f"
TEXT_MUTED = "#5a6f5e"
TEXT_DIM = "#8a9a8c"

ACCENT = "#2e7d32"
ACCENT_HOVER = "#388e3c"
ACCENT_SUBTLE = "#c8e6c9"
ACCENT_DARK = "#1b5e20"

OK = "#2e7d32"
WARN = "#f9a825"
ERR = "#c62828"
INFO = "#0277bd"

# Categorical chart palette (varied hues, readable on white; green leads)
CHART_CYCLE = [
    "#2e7d32",  # forest green (brand)
    "#1976d2",  # blue
    "#f57c00",  # orange
    "#7b1fa2",  # purple
    "#c62828",  # red
    "#00897b",  # teal
    "#5d4037",  # brown
    "#3949ab",  # indigo
    "#f9a825",  # amber
    "#ad1457",  # magenta
    "#546e7a",  # blue grey
    "#689f38",  # lime
    "#e64a19",  # deep orange
    "#0288d1",  # sky blue
    "#6a1b9a",  # deep purple
    "#455a64",  # slate
]

TABLE_ROW_ALT = "#f9fcfa"
TABLE_HEADER_BG = "#e8f5e9"
TABLE_GRID = "#c8e6c9"
TABLE_CELL_COMBO_BG = "#ffffff"
TABLE_CELL_COMBO_BORDER = "#a5d6a7"
TABLE_CELL_COMBO_FOCUS = "#2e7d32"


# -------------------------------------------------
# GLOBAL QT STYLESHEET
# -------------------------------------------------
STYLESHEET = f"""
* {{
    color: {TEXT};
    font-family: "Segoe UI", "SF Pro Text", system-ui, sans-serif;
    font-size: 13px;
}}

QMainWindow, QWidget {{
    background-color: {BG};
}}

/* ---- Activity bar ---- */
QFrame#ActivityBar {{
    background-color: {ACTIVITYBAR};
    border-right: 1px solid {BORDER};
}}
QPushButton#ActivityButton {{
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    color: {TEXT_MUTED};
    padding: 14px 0;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
}}
QPushButton#ActivityButton:hover {{
    color: {ACCENT_DARK};
    background: {BG_HOVER};
}}
QPushButton#ActivityButton:checked {{
    color: {ACCENT_DARK};
    border-left-color: {ACCENT};
    background: {BG_ACTIVE};
}}

/* ---- Header bar ---- */
QFrame#HeaderBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}
QLabel#HeaderTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#HeaderSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

/* ---- KPI cards ---- */
QFrame#KpiCard {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QLabel#KpiLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QLabel#KpiValue {{
    color: {TEXT};
    font-size: 24px;
    font-weight: 600;
}}
QLabel#KpiValueAccent {{
    color: {ACCENT};
    font-size: 24px;
    font-weight: 600;
}}

/* ---- Buttons ---- */
QPushButton {{
    background-color: {BG};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 22px;
}}
QPushButton:hover {{
    background-color: {BG_ACTIVE};
    border-color: {ACCENT};
    color: {ACCENT_DARK};
}}
QPushButton:pressed {{
    background-color: {ACCENT_SUBTLE};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    background-color: {BG_PANEL};
    border-color: {BORDER};
}}
QPushButton#PrimaryButton {{
    background-color: {ACCENT};
    color: white;
    border: 1px solid {ACCENT};
    font-weight: 600;
    padding: 8px 22px;
}}
QPushButton#PrimaryButton:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
    color: white;
}}
QPushButton#PrimaryButton:disabled {{
    background-color: {ACCENT_SUBTLE};
    border-color: {ACCENT_SUBTLE};
    color: {TEXT_DIM};
}}

/* ---- Combo / dropdown (legacy plain QComboBox) ---- */
QComboBox {{
    background: {BG};
    border: 1px solid {BORDER_STRONG};
    border-radius: 4px;
    padding: 5px 10px 5px 8px;
    min-height: 24px;
}}
QComboBox:hover {{
    border-color: {ACCENT};
    background: {BG_PANEL};
}}
QComboBox QAbstractItemView {{
    background: {BG};
    border: 1px solid {BORDER_STRONG};
    selection-background-color: {ACCENT_SUBTLE};
    selection-color: {ACCENT_DARK};
    outline: none;
    padding: 2px;
}}

/* ---- Toolbar / chart / filter dropdown (FA caret button) ---- */
QWidget#DropdownCombo {{
    background: {BG};
    border: 1px solid {BORDER_STRONG};
    border-radius: 4px;
    min-height: 30px;
}}
QWidget#DropdownCombo:hover {{
    border-color: {ACCENT};
    background: {BG_PANEL};
}}
QWidget#DropdownCombo:focus-within {{
    border: 2px solid {ACCENT};
}}
QComboBox#DropdownComboInner {{
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 5px 4px 5px 10px;
    min-height: 22px;
}}
QComboBox#DropdownComboInner:focus {{
    border: none;
    padding: 5px 4px 5px 10px;
}}
QComboBox#DropdownComboInner::drop-down {{
    width: 0;
    border: none;
}}
QComboBox#DropdownComboInner::down-arrow {{
    width: 0;
    height: 0;
    image: none;
}}
QComboBox#DropdownComboInner QAbstractItemView {{
    background: {BG};
    border: 1px solid {BORDER_STRONG};
    selection-background-color: {ACCENT};
    selection-color: white;
    padding: 2px;
}}
QToolButton#DropdownComboArrow {{
    background: {BG_PANEL};
    border: none;
    border-left: 1px solid {BORDER};
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    padding: 0;
    min-height: 0;
}}
QToolButton#DropdownComboArrow:hover {{
    background: {ACCENT_SUBTLE};
}}
QToolButton#DropdownComboArrow:pressed {{
    background: {ACCENT_SUBTLE};
}}

/* ---- Tables (Excel-like grid) ---- */
QTableWidget {{
    background-color: {BG};
    alternate-background-color: {TABLE_ROW_ALT};
    gridline-color: {TABLE_GRID};
    border: 1px solid {BORDER_STRONG};
    border-radius: 2px;
    selection-background-color: {ACCENT_SUBTLE};
    selection-color: {ACCENT_DARK};
}}
QHeaderView::section {{
    background-color: {TABLE_HEADER_BG};
    color: {ACCENT_DARK};
    border: none;
    border-right: 1px solid {TABLE_GRID};
    border-bottom: 1px solid {BORDER_STRONG};
    padding: 7px 8px;
    font-weight: 600;
    font-size: 12px;
}}
QTableWidget::item {{
    border: none;
    padding: 4px 8px;
}}
QTableWidget::item:selected {{
    background-color: {ACCENT_SUBTLE};
    color: {ACCENT_DARK};
}}

/* ---- In-table dropdown (Excel cell editor + FA caret button) ---- */
QWidget#TableCellCombo {{
    background-color: {TABLE_CELL_COMBO_BG};
    border: none;
    margin: 0;
}}
QWidget#TableCellCombo:hover {{
    background-color: {BG_PANEL};
}}
QComboBox#TableCellComboInner {{
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0 4px 0 8px;
    min-height: 0;
}}
QComboBox#TableCellComboInner:focus {{
    border: none;
    padding: 0 4px 0 8px;
}}
QComboBox#TableCellComboInner::drop-down {{
    width: 0;
    border: none;
}}
QComboBox#TableCellComboInner::down-arrow {{
    width: 0;
    height: 0;
    image: none;
}}
QComboBox#TableCellComboInner QAbstractItemView {{
    background: {BG};
    border: 1px solid {BORDER_STRONG};
    selection-background-color: {ACCENT};
    selection-color: white;
}}
QToolButton#TableCellComboArrow {{
    background: {BG_PANEL};
    border: none;
    border-left: 1px solid {TABLE_GRID};
    border-radius: 0;
    padding: 0;
    min-height: 0;
}}
QToolButton#TableCellComboArrow:hover {{
    background: {ACCENT_SUBTLE};
}}
QToolButton#TableCellComboArrow:pressed {{
    background: {ACCENT_SUBTLE};
}}
QWidget#TableCellCombo:focus-within {{
    border: 2px solid {TABLE_CELL_COMBO_FOCUS};
}}

/* ---- Status bar ---- */
QStatusBar {{
    background-color: {ACCENT};
    color: white;
    font-size: 12px;
    min-height: 22px;
}}
QStatusBar QLabel {{
    color: white;
    padding: 0 8px;
}}

/* ---- Progress ---- */
QProgressBar {{
    background-color: rgba(255,255,255,0.25);
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: white;
    border-radius: 2px;
}}

/* ---- Scrollbars ---- */
QScrollBar:vertical, QScrollBar:horizontal {{
    background: {BG_PANEL};
    border: none;
}}
QScrollBar:vertical {{ width: 12px; }}
QScrollBar:horizontal {{ height: 12px; }}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {BORDER_STRONG};
    border-radius: 4px;
    margin: 2px;
}}
QScrollBar::handle:hover {{ background: {ACCENT}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ background: none; height: 0; width: 0; }}

/* ---- Misc ---- */
QLabel {{ background: transparent; }}
QToolTip {{
    background-color: {BG_ELEV};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    padding: 4px 6px;
}}

QFrame#PageHeader {{
    background-color: transparent;
}}
QLabel#PageTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#PageSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

/* ---- Home page ---- */
QLabel#Eyebrow {{
    color: {ACCENT};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 3px;
}}
QLabel#Headline {{
    font-size: 38px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#Tagline {{
    color: {TEXT_MUTED};
    font-size: 15px;
}}
QFrame#DropZone {{
    background-color: {BG_PANEL};
    border: 2px dashed {BORDER_STRONG};
    border-radius: 10px;
}}
QFrame#DropZone[active="true"] {{
    background-color: {ACCENT_SUBTLE};
    border: 2px dashed {ACCENT};
}}
QLabel#DropTitle {{
    color: {TEXT};
    font-size: 18px;
    font-weight: 600;
}}
QLabel#DropHint {{
    color: {TEXT_DIM};
    font-size: 12px;
}}
QLabel#SectionLabel {{
    color: {TEXT_DIM};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 2px;
}}
QFrame#FeatureCard {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QFrame#FeatureCard:hover {{
    border-color: {ACCENT};
}}
QLabel#FeatureNumber {{
    color: {ACCENT};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}}
QLabel#FeatureTitle {{
    color: {TEXT};
    font-size: 15px;
    font-weight: 600;
}}
QLabel#FeatureBody {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QFrame#StatsStrip {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QLabel#StatNumber {{
    color: {ACCENT};
    font-size: 26px;
    font-weight: 700;
}}
QLabel#StatLabel {{
    color: {TEXT_MUTED};
    font-size: 10px;
    letter-spacing: 1.5px;
    font-weight: 600;
}}
QFrame#Divider {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}
QFrame#StatDivider {{
    background-color: {BORDER};
    max-width: 1px;
    min-width: 1px;
}}
"""


# -------------------------------------------------
# MATPLOTLIB LIGHT THEME
# -------------------------------------------------
def apply_mpl_theme():
    import matplotlib as mpl
    from cycler import cycler

    mpl.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.edgecolor": BORDER_STRONG,
        "axes.labelcolor": TEXT_MUTED,
        "axes.titlecolor": TEXT,
        "axes.titlesize": 12,
        "axes.titleweight": "600",
        "axes.titlepad": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": BORDER,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.8,
        "xtick.color": TEXT_MUTED,
        "ytick.color": TEXT_MUTED,
        "text.color": TEXT,
        "legend.facecolor": BG_PANEL,
        "legend.edgecolor": BORDER,
        "legend.labelcolor": TEXT,
        "legend.fontsize": 9,
        "font.family": ["Segoe UI", "sans-serif"],
        "font.size": 10,
        "axes.prop_cycle": cycler(color=CHART_CYCLE),
    })


def configure_excel_table(table) -> None:
    """Apply Excel-like grid and row sizing to a QTableWidget."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QAbstractItemView

    table.setShowGrid(True)
    table.setGridStyle(Qt.SolidLine)
    table.verticalHeader().setDefaultSectionSize(30)
    table.setWordWrap(False)


# Default row height for cells that contain a dropdown
TABLE_COMBO_ROW_HEIGHT = 30
